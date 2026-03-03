from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExamViewSet, AttemptViewSet

router = DefaultRouter()
router.register(r'', ExamViewSet)
router.register(r'attempts', AttemptViewSet, basename='attempt')

urlpatterns = [
    path('', include(router.urls)),
]
