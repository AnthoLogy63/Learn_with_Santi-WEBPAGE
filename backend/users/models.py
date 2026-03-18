from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserManager(BaseUserManager):
    def create_user(self, usu_cod, password=None, **extra_fields):
        if not usu_cod:
            raise ValueError('The Username (usu_cod) must be set')
        user = self.model(usu_cod=usu_cod, username=usu_cod, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, usu_cod, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        return self.create_user(usu_cod, password, **extra_fields)


class Rango(models.Model):
    ran_sig = models.IntegerField(primary_key=True)
    ran_nom = models.CharField(max_length=50)
    ran_pun_min = models.IntegerField(default=0)
    ran_pun_max = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.ran_nom} ({self.ran_sig})"


class Categoria(models.Model):
    cat_cod = models.CharField(max_length=10, primary_key=True)
    cat_nom = models.CharField(max_length=50)

    def __str__(self):
        return self.cat_nom


class Competencia(models.Model):
    com_cod = models.CharField(max_length=50, primary_key=True)
    com_nom = models.CharField(max_length=150)
    com_des = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.com_nom


class User(AbstractBaseUser):
    usu_cod = models.CharField(max_length=50, primary_key=True)
    username = models.CharField(max_length=50, unique=True) # Mantenido para auth de Django
    usu_dni = models.CharField(max_length=15, unique=True, null=True, blank=True)
    usu_nom = models.CharField(max_length=100)
    usu_sex = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Femenino')], null=True, blank=True)
    usu_edad = models.IntegerField(default=0)
    usu_fec_ult = models.DateField(null=True, blank=True)
    usu_reg = models.DateField(auto_now_add=True)
    usu_zon = models.CharField(max_length=50, blank=True, null=True)
    usu_age = models.IntegerField(default=0)
    cat_cod = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, db_column='cat_cod')
    usu_pun_tot = models.IntegerField(default=0)
    ran_sig = models.ForeignKey(Rango, on_delete=models.SET_NULL, null=True, blank=True, db_column='ran_sig')
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'usu_cod'
    REQUIRED_FIELDS = ['usu_nom']

    @property
    def is_superuser(self):
        return self.is_staff

    @property
    def is_active(self):
        return True

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff

    def save(self, *args, **kwargs):
        if not self.usu_cod:
            self.usu_cod = self.username
        if not self.username:
            self.username = self.usu_cod
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.usu_nom} ({self.usu_cod})"

@receiver(post_save, sender=User)
def auto_update_rank(sender, instance, **kwargs):
    pass