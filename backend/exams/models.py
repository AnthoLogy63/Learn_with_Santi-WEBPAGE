from django.db import models
from django.conf import settings
from users.models import Categoria, Competencia

class TipoPregunta(models.Model):
    tip_pre_cod = models.IntegerField(primary_key=True)
    tip_pre_nom = models.CharField(max_length=50)

    def __str__(self):
        return self.tip_pre_nom

class Examen(models.Model):
    exa_cod = models.CharField(max_length=20, primary_key=True)
    exa_nom = models.CharField(max_length=100)
    exa_des = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.exa_nom

class CategoriaExamen(models.Model):
    cat_cod = models.ForeignKey(Categoria, on_delete=models.CASCADE, db_column='cat_cod')
    exa_cod = models.ForeignKey(Examen, on_delete=models.CASCADE, db_column='exa_cod')

    class Meta:
        unique_together = (('cat_cod', 'exa_cod'),)

    def __str__(self):
        return f"{self.exa_cod_id} - {self.cat_cod_id}"

class Pregunta(models.Model):
    pre_cod = models.CharField(max_length=25, primary_key=True)
    exa_cod = models.ForeignKey(Examen, on_delete=models.CASCADE, db_column='exa_cod')
    tip_pre_cod = models.ForeignKey(TipoPregunta, on_delete=models.SET_NULL, null=True, blank=True, db_column='tip_pre_cod')
    pre_tex = models.CharField(max_length=200)
    pre_fot = models.ImageField(upload_to='questions/', blank=True, null=True)
    pre_pun = models.IntegerField(default=0)
    pre_tie = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.pre_cod} ({self.exa_cod_id})"

class Opcion(models.Model):
    opc_cod = models.CharField(max_length=30, primary_key=True)
    pre_cod = models.ForeignKey(Pregunta, on_delete=models.CASCADE, db_column='pre_cod', related_name='opciones')
    opc_tex = models.CharField(max_length=100)
    opc_cor = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.opc_cod} - {'Correcta' if self.opc_cor else 'Incorrecta'}"

class Intento(models.Model):
    int_cod = models.CharField(max_length=50, primary_key=True)
    usu_cod = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='usu_cod', related_name='intentos')
    exa_cod = models.ForeignKey(Examen, on_delete=models.CASCADE, db_column='exa_cod')
    exa_num_int = models.IntegerField(default=1)
    exa_fec_ini = models.DateTimeField(auto_now_add=True)
    exa_fec_fin = models.DateTimeField(null=True, blank=True)
    exa_pun_tot = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.int_cod} ({self.usu_cod_id})"

class Respuesta(models.Model):
    res_cod = models.CharField(max_length=50, primary_key=True)
    int_cod = models.ForeignKey(Intento, on_delete=models.CASCADE, db_column='int_cod', related_name='respuestas')
    pre_cod = models.ForeignKey(Pregunta, on_delete=models.CASCADE, db_column='pre_cod')
    opc_cod = models.ForeignKey(Opcion, on_delete=models.SET_NULL, null=True, blank=True, db_column='opc_cod')
    res_tex = models.CharField(max_length=200, blank=True, null=True)
    res_pun = models.IntegerField(default=0)
    res_cor = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.res_cod} en intento {self.int_cod_id}"

class PreguntaCompetencia(models.Model):
    pre_cod = models.ForeignKey(Pregunta, on_delete=models.CASCADE, db_column='pre_cod')
    com_cod = models.ForeignKey(Competencia, on_delete=models.CASCADE, db_column='com_cod')

    class Meta:
        unique_together = (('pre_cod', 'com_cod'),)

    def __str__(self):
        return f"{self.pre_cod_id} - {self.com_cod_id}"

class ExamenCategoriaCompetencia(models.Model):
    exa_cod = models.ForeignKey(Examen, on_delete=models.CASCADE, db_column='exa_cod')
    cat_cod = models.ForeignKey(Categoria, on_delete=models.CASCADE, db_column='cat_cod')
    com_cod = models.ForeignKey(Competencia, on_delete=models.CASCADE, db_column='com_cod')
    num_preguntas = models.IntegerField(default=0)

    class Meta:
        unique_together = (('exa_cod', 'cat_cod', 'com_cod'),)

    def __str__(self):
        return f"{self.exa_cod_id} - {self.cat_cod_id} - {self.com_cod_id}: {self.num_preguntas} preg"
