from rest_framework import serializers
from .models import Exam, Question, Attempt, AttemptQuestion, AttemptAnswer

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'image', 'option_a', 'option_b', 'option_c', 'option_d', 'points', 'time_limit_seconds']

class ExamSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    last_score = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = ['id', 'name', 'description', 'bank_total_questions', 'questions_per_attempt', 'max_scored_attempts', 'max_points', 'is_active', 'status', 'last_score']

    def get_status(self, obj):
        user = self.context['request'].user
        if Attempt.objects.filter(user=user, exam=obj, status='completed').exists():
            return 'completed'
        return 'pending'

    def get_last_score(self, obj):
        user = self.context['request'].user
        last_attempt = Attempt.objects.filter(user=user, exam=obj, status='completed').order_by('-completed_at').first()
        if last_attempt:
            return last_attempt.score_obtained
        return None

class AttemptAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttemptAnswer
        fields = ['question', 'selected_option', 'is_correct', 'points_obtained', 'answered_at']
        read_only_fields = ['is_correct', 'points_obtained', 'answered_at']

class AttemptSerializer(serializers.ModelSerializer):
    answers = AttemptAnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Attempt
        fields = ['id', 'user', 'exam', 'attempt_number', 'counts_for_score', 'status', 'score_obtained', 'started_at', 'completed_at', 'answers']
        read_only_fields = ['user', 'attempt_number', 'counts_for_score', 'status', 'score_obtained', 'completed_at']
