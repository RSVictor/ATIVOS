from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .custom_user_manager import CustomUserManager

class status_ativos(models.TextChoices):
    ATIVO='ATIVO',
    EM_MANUTENCAO='EM_MANUTENCAO',
    DESATIVADO='DESATIVADO'


class status_chamado(models.TextChoices):
    AGUARDANDO_ATENDIMENTO='AGUARDANDO_ATENDIMENTO',
    EM_ANDAMENTO='EM_ANDAMENTO',
    CONCLUIDO='CONCLUIDO'
    CANCELADO='CANCELADO'

class prioridade_chamado(models.TextChoices):
    BAIXA='BAIXA',
    MEDIA='MEDIA',
    ALTA='ALTA'


class Users(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('pendente', 'Pendente'),
        ('usuario', 'Usuário'),
        ('tecnico', 'Técnico'),
    )

    name = models.CharField(max_length=150, null=False)
    email = models.EmailField(max_length=255, unique=True)
    cargo = models.CharField(max_length=50, null=False)
    cpf = models.CharField(max_length=11, null=False, blank=False, unique=True)
    dt_nascimento = models.DateField(null=False, blank=False)
    endereco = models.CharField(max_length=255, null=False, blank=False)
    foto_user = models.TextField(null=True, blank=True)

    # campos de permissão
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)  # só acessa após aprovação
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='pendente')  # 👈 novo campo

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'cargo', 'cpf', 'dt_nascimento', 'endereco', 'foto_user']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.name} ({self.role})"


class Environment(models.Model):
    name = models.CharField(max_length=250, null=False)
    description = models.CharField(max_length=400)
    employee = models.ForeignKey(Users, related_name='environment_funcionario_FK', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class Ativo(models.Model):
    name = models.CharField(max_length=250, null=False)
    description = models.CharField(max_length=400)
    status = models.CharField(
        max_length=60,
        choices=status_ativos.choices,
        default=status_ativos.ATIVO,
    )
    environment_FK = models.ForeignKey(Environment, related_name='ativo_ambiente_FK', on_delete=models.CASCADE)   

    def __str__(self):
        return self.name


class Chamado(models.Model):
    title = models.CharField(max_length=250, null=False)
    description = models.CharField(max_length=250, null=False)
    dt_criacao = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=60,
        choices=status_chamado.choices,
        default=status_chamado.AGUARDANDO_ATENDIMENTO,
    )
    prioridade = models.CharField(
        max_length=60,
        choices=prioridade_chamado.choices,
    )
    creator = models.ForeignKey(Users, related_name='chamado_usuario_FK', on_delete=models.CASCADE)
    employee = models.ManyToManyField(Users, related_name='chamado_funcionario_FK')
    asset = models.ForeignKey(Ativo, related_name='chamado_ativo_FK', on_delete=models.CASCADE)
    update_date = models.DateTimeField(auto_now=True)
    photo = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title
    

class Notificate(models.Model):
    title = models.CharField(max_length=50, null=False)
    description = models.CharField(max_length=500, null=False)
    dt_criacao = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Users, related_name='notificate_usuario_FK', on_delete=models.CASCADE)
    chamado_FK = models.ForeignKey(Chamado, related_name='notificate_chamado_FK', on_delete=models.CASCADE)
    

    def __str__(self):
        return self.title