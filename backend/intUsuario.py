import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from users.models import User, Categoria, Rango, Competencia
from exams.models import TipoPregunta
from django.utils import timezone
from django.db import transaction


users_data = [
    {"usu_cod": "44337053","usu_nom": "Alberth","usu_dni": "44337053","usu_tel": "928612471","usu_zon": "IMPERIAL","is_staff": False, "cat_cod": "0"},
]

def run():
    print("🚀 Iniciando sembrado de datos...")
    
    with transaction.atomic():

        # 3. Sembrar Usuarios
        for u in users_data:
            cat_instance = None
            if "cat_cod" in u:
                try:
                    cat_instance = Categoria.objects.get(cat_cod=u["cat_cod"])
                except Categoria.DoesNotExist:
                    print(f"⚠️ Categoría {u['cat_cod']} no encontrada para {u['usu_cod']}")

            user, created = User.objects.update_or_create(
                usu_cod=u["usu_cod"],
                defaults={
                    "username": u["usu_cod"],
                    "usu_nom": u["usu_nom"],
                    "usu_dni": u.get("usu_dni"),
                    "is_staff": u.get("is_staff", False),
                    "cat_cod": cat_instance,
                    "usu_fec_ult": timezone.now().date(),
                }
            )
            if created:
                user.set_password(u["usu_dni"])
                user.save()
                print(f"✅ Usuario creado: {user.usu_cod}")
            else:
                print(f"ℹ️ Usuario {user.usu_cod} actualizado")

    print("✨ Proceso completado con éxito.")

if __name__ == "__main__":
    run()