import csv
from django.http import HttpResponse
from django.contrib import admin
from .models import Exam, Question, Option, Attempt

def generate_csv_response(queryset, filename):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    writer = csv.writer(response)

    # Header: Fecha Inicio, Fecha Cierre, Usuario, DNI, Examen, Intento, Puntaje
    writer.writerow(['Fecha de Inicio', 'Fecha de Cierre', 'Usuario', 'DNI', 'Examen', 'Nº de Intento', 'Puntaje'])
    
    for obj in queryset:
        row = [
            obj.started_at.strftime("%Y-%m-%d %H:%M:%S") if obj.started_at else "",
            obj.completed_at.strftime("%Y-%m-%d %H:%M:%S") if obj.completed_at else "",
            obj.user.username,
            getattr(obj.user, 'dni', ''),
            obj.exam.name,
            obj.attempt_number,
            obj.score_obtained
        ]
        writer.writerow(row)
    return response

def export_as_csv(self, request, queryset):
    return generate_csv_response(queryset, 'resultados_seleccionados.csv')

export_as_csv.short_description = "Descargar seleccionados como Excel (CSV)"

@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('started_at', 'completed_at', 'user', 'get_dni', 'exam', 'attempt_number', 'score_obtained', 'status')
    list_filter = ('exam', 'status', 'started_at')
    search_fields = ('user__username', 'user__dni', 'exam__name')
    actions = [export_as_csv]

    def get_dni(self, obj):
        return getattr(obj.user, 'dni', '')
    get_dni.short_description = 'DNI'

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'questions_per_attempt', 'max_scored_attempts', 'is_active', 'is_enabled')
    list_editable = ('is_active', 'is_enabled')

class OptionInline(admin.TabularInline):
    model = Option
    extra = 3

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'exam', 'question_type', 'points')
    list_filter = ('exam', 'question_type')
    inlines = [OptionInline]

admin.site.register(Option)
