from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ExamenViewSet, IntentoViewSet, ImportExamView, 
    PreguntaViewSet, OpcionViewSet, TipoPreguntaViewSet,
    ExportExamTemplateView
)

router = DefaultRouter()
router.register(r'attempts', IntentoViewSet, basename='attempt')
router.register(r'questions', PreguntaViewSet)
router.register(r'options', OpcionViewSet)
router.register(r'tipos-pregunta', TipoPreguntaViewSet)
router.register(r'', ExamenViewSet)

urlpatterns = [
    path('import/', ImportExamView.as_view(), name='exam-import'),
    path('template/', ExportExamTemplateView.as_view(), name='exam-template'),
    path('', include(router.urls)),
]
