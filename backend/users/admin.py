from django.contrib import admin
from .models import User, Rango, Categoria, Competencia

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('usu_cod', 'usu_nom', 'usu_dni', 'usu_pun_tot')
    search_fields = ('usu_cod', 'usu_nom', 'usu_dni')

admin.site.register(Rango)
admin.site.register(Categoria)
admin.site.register(Competencia)
