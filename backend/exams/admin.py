from django.contrib import admin
from .models import TipoPregunta, Examen, CategoriaExamen, Pregunta, Opcion, Intento, Respuesta, PreguntaCompetencia, ExamenCategoriaCompetencia

admin.site.register(TipoPregunta)
admin.site.register(Examen)
admin.site.register(CategoriaExamen)
admin.site.register(Pregunta)
admin.site.register(Opcion)
admin.site.register(Intento)
admin.site.register(Respuesta)
admin.site.register(PreguntaCompetencia)
admin.site.register(ExamenCategoriaCompetencia)
