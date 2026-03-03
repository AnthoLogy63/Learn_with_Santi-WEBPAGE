import random
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Exam, Question, Attempt, AttemptQuestion, AttemptAnswer
from .serializers import ExamSerializer, QuestionSerializer, AttemptSerializer, AttemptAnswerSerializer

class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Exam.objects.filter(is_active=True)
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        exam = self.get_object()
        # Get or create an active attempt for this user and exam
        attempt = Attempt.objects.filter(user=request.user, exam=exam, status='in_progress').first()
        
        if not attempt:
            # Create new attempt
            attempt = Attempt.objects.create(user=request.user, exam=exam)
            
            # Select random questions from the bank
            all_questions = list(Question.objects.filter(exam=exam))
            num_questions = min(len(all_questions), exam.questions_per_attempt)
            selected_questions = random.sample(all_questions, num_questions)
            
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

class AttemptViewSet(viewsets.ModelViewSet):
    queryset = Attempt.objects.all()
    serializer_class = AttemptSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Attempt.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def submit_answers(self, request, pk=None):
        attempt = self.get_object()
        if attempt.status != 'in_progress':
            return Response({'error': 'Attempt is already finished'}, status=status.HTTP_400_BAD_REQUEST)
        
        answers_data = request.data.get('answers', [])
        total_points = 0
        
        for ans in answers_data:
            question_id = ans.get('question_id')
            selected_option = ans.get('selected_option')
            
            try:
                question = Question.objects.get(id=question_id, exam=attempt.exam)
                # Check if already answered
                answer_obj, created = AttemptAnswer.objects.get_or_create(
                    attempt=attempt,
                    question=question,
                    defaults={'selected_option': selected_option}
                )
                if not created:
                    answer_obj.selected_option = selected_option
                    answer_obj.save()
                
                total_points += answer_obj.points_obtained
            except Question.DoesNotExist:
                continue
        
        # Calculate final score (0-100)
        max_possible_points = sum(aq.question.points for aq in attempt.attempt_questions.all())
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
            
        return Response({
            'score': score,
            'status': attempt.status,
            'counts_for_score': attempt.counts_for_score,
            'total_user_score': attempt.user.total_score
        })
