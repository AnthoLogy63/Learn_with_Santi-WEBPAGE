import random
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import models
from .models import Exam, Question, Option, Attempt, AttemptQuestion, AttemptAnswer
from .serializers import ExamSerializer, QuestionSerializer, AttemptSerializer, AttemptAnswerSerializer

class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Exam.objects.all()
        return Exam.objects.filter(is_active=True, is_enabled=True)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def toggle_enabled(self, request, pk=None):
        if not request.user.is_staff:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        exam = self.get_object()
        exam.is_enabled = not exam.is_enabled
        exam.save()
        return Response({'is_enabled': exam.is_enabled})

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def export_csv(self, request, pk=None):
        if not request.user.is_staff:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
            
        import csv
        from django.http import HttpResponse
        
        exam = self.get_object()
        # Get all questions for this exam to fix columns
        questions = list(Question.objects.filter(exam=exam).order_by('id'))
        attempts = Attempt.objects.filter(exam=exam, status='completed').order_by('started_at')
        
        response = HttpResponse(content_type='text/csv')
        filename = f'resultados_{exam.name.replace(" ", "_").lower()}.csv'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        
        # Add UTF-8 BOM for Excel compatibility with accents
        response.write('\ufeff'.encode('utf8'))
        
        writer = csv.writer(response)
        
        # Pre-fetch question options for letter mapping
        options_map = {}
        for q in questions:
            options_map[q.id] = list(Option.objects.filter(question=q).order_by('id'))
        
        # Header construction
        header = ['ID', 'Start time', 'Completion time', 'Email', 'Name', 'DNI', 'Total points', 'Nº Intento']
        for q in questions:
            header.append(q.text)
            header.append(f'Points - {q.text}')
        
        writer.writerow(header)
        
        for row_idx, obj in enumerate(attempts, start=1):
            # Basic info
            row = [
                row_idx,
                obj.started_at.strftime("%Y-%m-%d %H:%M:%S") if obj.started_at else "",
                obj.completed_at.strftime("%Y-%m-%d %H:%M:%S") if obj.completed_at else "",
                obj.user.email,
                obj.user.username,
                getattr(obj.user, 'dni', ''),
                obj.score_obtained,
                obj.attempt_number,
            ]
            
            # Answer info for each question
            answers_map = {ans.question_id: ans for ans in AttemptAnswer.objects.filter(attempt=obj)}
            
            for q in questions:
                ans_obj = answers_map.get(q.id)
                q_options = options_map.get(q.id, [])
                
                if ans_obj:
                    # Format selected answer text with letters
                    selected_text = ""
                    if q.question_type == 'multiple_choice':
                        selected_parts = []
                        sel_opts = set(ans_obj.selected_options.all().values_list('id', flat=True))
                        for i, opt in enumerate(q_options):
                            if opt.id in sel_opts:
                                selected_parts.append(f"{chr(65+i)}. {opt.text}")
                        selected_text = ", ".join(selected_parts)
                    elif q.question_type == 'open_ended':
                        selected_text = ans_obj.text_response or ""
                    else:
                        if ans_obj.selected_option:
                            index = -1
                            for i, opt in enumerate(q_options):
                                if opt.id == ans_obj.selected_option_id:
                                    index = i
                                    break
                            if index != -1:
                                selected_text = f"{chr(65+index)}. {ans_obj.selected_option.text}"
                            else:
                                selected_text = ans_obj.selected_option.text
                        else:
                            selected_text = ""
                    
                    row.append(selected_text)
                    row.append(ans_obj.points_obtained)
                else:
                    # Question not in this attempt
                    row.append("")
                    row.append(0)
            
            writer.writerow(row)
            
        return response

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def questions(self, request, pk=None):
        exam = self.get_object()
        user = request.user
        
        # Get or create an active attempt
        attempt = Attempt.objects.filter(user=user, exam=exam, status='in_progress').first()
        
        if not attempt:
            # Smart selection logic:
            
            # 1. Get IDs of questions user has EVER answered in this exam
            answered_question_ids = AttemptAnswer.objects.filter(
                attempt__user=user,
                attempt__exam=exam,
                attempt__status='completed'
            ).values_list('question_id', flat=True).distinct()
            
            # 2. Get IDs of questions user has EVER answered CORRECTLY
            correct_question_ids = AttemptAnswer.objects.filter(
                attempt__user=user,
                attempt__exam=exam,
                attempt__status='completed',
                is_correct=True
            ).values_list('question_id', flat=True).distinct()
            
            all_questions = list(Question.objects.filter(exam=exam))
            
            # 3. Categorize questions
            unseen_questions = [q for q in all_questions if q.id not in answered_question_ids]
            failed_questions = [q for q in all_questions if q.id in answered_question_ids and q.id not in correct_question_ids]
            mastered_questions = [q for q in all_questions if q.id in correct_question_ids]
            
            num_needed = min(len(all_questions), exam.questions_per_attempt)
            selected_questions = []

            # Priority 1: Unseen questions
            if len(unseen_questions) > 0:
                take = min(len(unseen_questions), num_needed)
                selected_questions.extend(random.sample(unseen_questions, take))
            
            # Priority 2: Failed questions (if still needed)
            needed_still = num_needed - len(selected_questions)
            if needed_still > 0 and len(failed_questions) > 0:
                take = min(len(failed_questions), needed_still)
                selected_questions.extend(random.sample(failed_questions, take))
            
            # Priority 3: Mastered questions (to fill the 10, if everything else is exhausted)
            needed_still = num_needed - len(selected_questions)
            if needed_still > 0 and len(mastered_questions) > 0:
                take = min(len(mastered_questions), needed_still)
                selected_questions.extend(random.sample(mastered_questions, take))
            
            # Shuffle the final selection so they don't appear in "priority order"
            random.shuffle(selected_questions)
            
            attempt = Attempt.objects.create(user=user, exam=exam)
            
            # Create AttemptQuestions to preserve order
            for i, q in enumerate(selected_questions):
                AttemptQuestion.objects.create(attempt=attempt, question=q, order_number=i+1)
        
        # Return questions in the attempt
        questions = [aq.question for aq in attempt.attempt_questions.all()]
        serializer = QuestionSerializer(questions, many=True)
        return Response({
            'attempt_id': attempt.id,
            'questions': serializer.data
        })

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def stats_summary(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()
        
        exams = Exam.objects.all()
        stats = []
        for exam in exams:
            # Group by analyst, taking their BEST attempt
            analysts = UserModel.objects.filter(is_staff=False)
            best_scores = []
            for analyst in analysts:
                best_q_attempt = Attempt.objects.filter(
                    user=analyst, 
                    exam=exam, 
                    status='completed',
                    counts_for_score=True
                ).order_by('-score_obtained').first()
                if best_q_attempt:
                    best_scores.append(best_q_attempt.score_obtained)
            
            total_analysts = len(best_scores)
            avg_score = sum(best_scores) / total_analysts if total_analysts > 0 else 0
            
            # Question stats based on best qualifying attempts
            questions = Question.objects.filter(exam=exam)
            q_stats = []
            
            # Find all "best qualifying attempts" IDs for this exam
            best_attempt_ids = []
            for analyst in analysts:
                at = Attempt.objects.filter(user=analyst, exam=exam, status='completed', counts_for_score=True).order_by('-score_obtained').first()
                if at: best_attempt_ids.append(at.id)

            for q in questions:
                relevant_answers = AttemptAnswer.objects.filter(question=q, attempt_id__in=best_attempt_ids)
                total_q = relevant_answers.count()
                correct_q = relevant_answers.filter(is_correct=True).count()
                
                # Choice distribution (like Google Forms)
                choices = []
                for opt in q.options.all():
                    # Count how many times this specific option was selected in these best attempts
                    if q.question_type == 'multiple_choice':
                        count = relevant_answers.filter(selected_options=opt).count()
                    else:
                        count = relevant_answers.filter(selected_option=opt).count()
                    
                    choices.append({
                        'text': opt.text,
                        'is_correct': opt.is_correct,
                        'count': count,
                        'percent': round((count / total_q * 100) if total_q > 0 else 0)
                    })

                q_stats.append({
                    'id': q.id,
                    'text': q.text,
                    'type': q.question_type,
                    'total': total_q,
                    'correct': correct_q,
                    'percent': round((correct_q / total_q * 100) if total_q > 0 else 0),
                    'choices': choices
                })

            stats.append({
                'id': exam.id,
                'name': exam.name,
                'total_attempts': total_analysts, 
                'avg_score': round(avg_score),
                'question_stats': q_stats
            })
            
        return Response(stats)

class AttemptViewSet(viewsets.ModelViewSet):
    queryset = Attempt.objects.all()
    serializer_class = AttemptSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Attempt.objects.all()
        return Attempt.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def user_results(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()
        
        search_query = request.query_params.get('search', '')
        offset = int(request.query_params.get('offset', 0))
        limit = 10
        
        analysts = UserModel.objects.filter(is_staff=False)
        if search_query:
            analysts = analysts.filter(username__icontains=search_query)
            
        total_count = analysts.count()
        analysts_page = analysts.order_by('username')[offset:offset+limit]
        
        results = []
        for user in analysts_page:
            user_attempts = Attempt.objects.filter(user=user, status='completed').order_by('-completed_at')
            attempts_data = []
            
            for attempt in user_attempts:
                answers = AttemptAnswer.objects.filter(attempt=attempt)
                ans_data = []
                for a in answers:
                    selected_text = "N/A"
                    if a.question.question_type == 'multiple_choice':
                        selected_text = ", ".join([o.text for o in a.selected_options.all()])
                    elif a.question.question_type == 'open_ended':
                        selected_text = a.text_response or ""
                    else:
                        selected_text = a.selected_option.text if a.selected_option else "N/A"

                    ans_data.append({
                        'question': a.question.text,
                        'selected': selected_text,
                        'is_correct': a.is_correct
                    })
                
                attempts_data.append({
                    'id': attempt.id,
                    'exam_id': attempt.exam.id,
                    'exam_name': attempt.exam.name,
                    'score': attempt.score_obtained,
                    'date': attempt.completed_at,
                    'attempt_number': attempt.attempt_number,
                    'counts_for_score': attempt.counts_for_score,
                    'answers': ans_data
                })
            
            results.append({
                'id': user.id,
                'username': user.username,
                'total_score': user.total_score,
                'attempts': attempts_data
            })
            
        return Response({
            'results': results,
            'total': total_count,
            'has_more': (offset + limit) < total_count
        })

    @action(detail=True, methods=['post'])
    def submit_answers(self, request, pk=None):
        attempt = self.get_object()
        if attempt.status != 'in_progress':
            return Response({'error': 'Attempt is already finished'}, status=status.HTTP_400_BAD_REQUEST)
        
        answers_data = request.data.get('answers', [])
        total_points = 0
        
        for ans in answers_data:
            question_id = ans.get('question_id')
            option_id = ans.get('selected_option_id') # single
            option_ids = ans.get('selected_option_ids', []) # multiple
            text_response = ans.get('text_response') # open
            
            try:
                question = Question.objects.get(id=question_id, exam=attempt.exam)
                
                # Get or create answer object
                answer_obj, created = AttemptAnswer.objects.get_or_create(
                    attempt=attempt,
                    question=question
                )
                
                if question.question_type == 'single_choice':
                    option = Option.objects.get(id=option_id, question=question) if option_id else None
                    answer_obj.selected_option = option
                    answer_obj.save() # calculates points in models.py
                    
                elif question.question_type == 'multiple_choice':
                    # Multiple choice scoring: all correct options must be selected, no incorrect ones
                    options = Option.objects.filter(id__in=option_ids, question=question)
                    answer_obj.selected_options.set(options)
                    
                    correct_options_ids = set(Option.objects.filter(question=question, is_correct=True).values_list('id', flat=True))
                    selected_ids = set(option_ids)
                    
                    if selected_ids == correct_options_ids and len(correct_options_ids) > 0:
                        answer_obj.is_correct = True
                        answer_obj.points_obtained = question.points
                    else:
                        answer_obj.is_correct = False
                        answer_obj.points_obtained = 0
                    answer_obj.save()
                    
                elif question.question_type == 'open_ended':
                    answer_obj.text_response = text_response
                    answer_obj.save() # calculates points in models.py (non-empty = correct)
                
                total_points += answer_obj.points_obtained
            except (Question.DoesNotExist, Option.DoesNotExist):
                continue
        
        # Calculate final score (0-100)
        aq_count = AttemptQuestion.objects.filter(attempt=attempt).count()
        max_possible_points = AttemptQuestion.objects.filter(attempt=attempt).aggregate(total=models.Sum('question__points'))['total'] or 0
        
        if max_possible_points > 0:
            score = round((total_points / max_possible_points) * 100)
        else:
            score = 0
            
        attempt.status = 'completed'
        attempt.score_obtained = score
        attempt.completed_at = timezone.now()
        attempt.save()
        
        # Update user total_score if valid
        if attempt.counts_for_score:
            user = attempt.user
            user.total_score += score
            user.save()
            user.update_rank()
            
        # Calculate correct answers count
        correct_count = AttemptAnswer.objects.filter(attempt=attempt, is_correct=True).count()
        total_questions = AttemptQuestion.objects.filter(attempt=attempt).count()
        
        # Calculate attempts left for scoring
        attempts_count = Attempt.objects.filter(user=attempt.user, exam=attempt.exam).count()
        attempts_left = max(0, attempt.exam.max_scored_attempts - attempts_count)

        return Response({
            'score': score,
            'correct_count': correct_count,
            'total_questions': total_questions,
            'status': attempt.status,
            'counts_for_score': attempt.counts_for_score,
            'attempts_left': attempts_left,
            'total_user_score': attempt.user.total_score
        })
