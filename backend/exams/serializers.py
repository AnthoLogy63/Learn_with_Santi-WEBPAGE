from rest_framework import serializers
from .models import TipoPregunta, Examen, CategoriaExamen, Pregunta, Opcion, Intento, Respuesta

class TipoPreguntaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoPregunta
        fields = '__all__'

class CategoriaExamenSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaExamen
        fields = '__all__'

class OpcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opcion
        fields = ['opc_cod', 'pre_cod', 'opc_tex', 'opc_cor']
        extra_kwargs = {
            'opc_cod': {'required': False},
        }

    def create(self, validated_data):
        if 'opc_cod' not in validated_data or not validated_data['opc_cod']:
            import uuid
            validated_data['opc_cod'] = 'OPC_' + uuid.uuid4().hex[:15].upper()
        return super().create(validated_data)

class PreguntaSerializer(serializers.ModelSerializer):
    com_cod = serializers.SerializerMethodField()
    options = OpcionSerializer(many=True, required=False, source='opciones')
    
    class Meta:
        model = Pregunta
        fields = ['pre_cod', 'exa_cod', 'tip_pre_cod', 'pre_tex', 'pre_fot', 'pre_pun', 'pre_tie', 'options', 'com_cod']
        extra_kwargs = {
            'pre_cod': {'required': False},
            'exa_cod': {'required': False},
            'tip_pre_cod': {'required': False, 'allow_null': True},
            'pre_fot': {'required': False, 'allow_null': True},
        }

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Limpiar la URL de la foto si es necesario
        if instance.pre_fot:
            val = str(instance.pre_fot)
            # Si es una URL completa guardada por error, extraer el path relativo
            if val.startswith('http://') or val.startswith('https://'):
                from urllib.parse import urlparse
                path = urlparse(val).path
                if path.startswith('/media/'):
                    ret['pre_fot'] = path
                else:
                    ret['pre_fot'] = f"/media/{path.lstrip('/')}"
            elif not val.startswith('/'):
                ret['pre_fot'] = f"/media/{val}"
            else:
                ret['pre_fot'] = val
        return ret

    def get_com_cod(self, obj):
        from .models import PreguntaCompetencia
        pc = PreguntaCompetencia.objects.filter(pre_cod=obj).first()
        return pc.com_cod_id if pc else None

    def create(self, validated_data):
        if 'pre_cod' not in validated_data or not validated_data['pre_cod']:
            import uuid
            validated_data['pre_cod'] = 'PRE_' + uuid.uuid4().hex[:12].upper()
        return super().create(validated_data)

class ExamenSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    last_score = serializers.SerializerMethodField()

    class Meta:
        model = Examen
        fields = ['exa_cod', 'exa_nom', 'exa_des', 'status', 'last_score']
        extra_kwargs = {'exa_cod': {'required': False}}

    def __init__(self, *args, **kwargs):
        # Optimización: No calcular status/score si el contexto indica que es para una lista administrativa rápida
        simple = kwargs.pop('simple', False)
        super().__init__(*args, **kwargs)
        if simple:
            self.fields.pop('status', None)
            self.fields.pop('last_score', None)

    def create(self, validated_data):
        if 'exa_cod' not in validated_data or not validated_data['exa_cod']:
            import uuid
            validated_data['exa_cod'] = 'EX_' + uuid.uuid4().hex[:8].upper()
        return super().create(validated_data)

    def get_status(self, obj):
        try:
            user = self.context.get('request') and self.context['request'].user
            if not user or not user.is_authenticated:
                return 'pending'
            if Intento.objects.filter(usu_cod=user, exa_cod=obj, exa_fec_fin__isnull=False).exists():
                return 'completed'
            return 'pending'
        except Exception:
            return 'pending'

    def get_last_score(self, obj):
        try:
            user = self.context.get('request') and self.context['request'].user
            if not user or not user.is_authenticated:
                return None
            best_attempt = Intento.objects.filter(
                usu_cod=user,
                exa_cod=obj,
                exa_fec_fin__isnull=False
            ).order_by('-exa_pun_tot').first()
            if best_attempt:
                return best_attempt.exa_pun_tot
            return None
        except Exception:
            return None

class RespuestaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Respuesta
        fields = ['res_cod', 'int_cod', 'pre_cod', 'opc_cod', 'res_tex', 'res_pun', 'res_cor']
        read_only_fields = ['res_pun', 'res_cor']

class IntentoSerializer(serializers.ModelSerializer):
    respuestas = RespuestaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Intento
        fields = ['int_cod', 'usu_cod', 'exa_cod', 'exa_num_int', 'exa_fec_ini', 'exa_fec_fin', 'exa_pun_tot', 'respuestas']
        read_only_fields = ['usu_cod', 'exa_num_int', 'exa_pun_tot', 'exa_fec_fin']
