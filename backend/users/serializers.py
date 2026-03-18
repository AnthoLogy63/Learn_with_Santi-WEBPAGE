from rest_framework import serializers
from .models import User, Rango, Categoria, Competencia

class RangoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rango
        fields = '__all__'

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class CompetenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competencia
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    ran_sig = RangoSerializer(read_only=True)
    cat_cod = CategoriaSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['usu_cod', 'username', 'usu_dni', 'usu_nom', 'usu_sex', 'usu_edad', 'usu_pun_tot', 'cat_cod', 'ran_sig', 'is_staff']
        read_only_fields = ['usu_pun_tot', 'ran_sig', 'cat_cod', 'is_staff']

class UserListSerializer(serializers.ModelSerializer):
    ran_sig = RangoSerializer(read_only=True)
    cat_cod = CategoriaSerializer(read_only=True)
    usu_fec_ult = serializers.DateField(format="%d/%m/%Y", read_only=True)
    usu_reg = serializers.DateField(format="%d/%m/%Y", read_only=True)

    class Meta:
        model = User
        fields = [
            'usu_cod', 'username', 'usu_dni', 'usu_nom', 'usu_sex', 'usu_edad',
            'usu_pun_tot', 'ran_sig', 'cat_cod',
            'usu_fec_ult', 'usu_reg', 'is_staff'
        ]
