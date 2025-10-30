from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import Users, Environment, Ativo, Chamado, Notificate 


class ReadWriteSerializer(object):
    read_serializer_class = None
    write_serializer_class = None

    def get_serializer_class(self):
        if self.action in ['create','update',
                           'partial_update','destroy']:
            return self.get_write_serializer_class()
        return self.get_read_serializer_class()
    
    def get_read_serializer_class(self):
        return self.read_serializer_class
    
    def get_write_serializer_class(self):
        return self.write_serializer_class
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'
       

class EnvironmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Environment
        fields = '__all__'
        

class AtivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ativo
        fields = '__all__'
        


class ChamadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chamado
        fields = '__all__'
        read_only_fields = ['creator', 'dt_criacao', 'update_date']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['creator'] = request.user
        return super().create(validated_data)
        



class ChamadoReadSerializer(serializers.ModelSerializer):
    from .models import Users

    chamado_funcionario_FK = UserSerializer()
    chamado_usuario_FK = UserSerializer()
    
    class Meta:
        model = Chamado
        fields = '__all__'
        



class NotificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificate
        fields = '__all__'
        

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = Users.USERNAME_FIELD

    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.is_active:
            raise serializers.ValidationError("Aguardando aprovação do administrador.")

        data["user"] = {
            "id": self.user.id,
            "name": self.user.name,
            "cargo": self.user.cargo,
            "email": self.user.email
        }
        return data