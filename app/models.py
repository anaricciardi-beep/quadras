
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from django.utils import timezone

# CIDADES
class Cidade(models.Model):
    nome = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)

    class Meta:
        verbose_name = "Cidade"
        verbose_name_plural = "Cidades"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome}/{self.uf}"


# PESSOAS (CLASSE BASE)
class Pessoa(models.Model):
    nome = models.CharField(max_length=150)
    cpf = models.CharField(max_length=14, unique=True)
    data_nasc = models.DateField("Data de nascimento")
    email = models.EmailField()
    telefone = models.CharField(max_length=20, blank=True)
    cidade = models.ForeignKey(
        Cidade,
        on_delete=models.PROTECT,
        related_name="pessoas"
    )

    class Meta:
        verbose_name = "Pessoa"
        verbose_name_plural = "Pessoas"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


#  COMPLEXOS ESPORTIVOS
class ComplexoEsportivo(models.Model):
    nome = models.CharField(max_length=150)
    endereco = models.CharField(max_length=200)
    telefone = models.CharField(max_length=20, blank=True)
    cidade = models.ForeignKey(
        Cidade,
        on_delete=models.PROTECT
    )

    class Meta:
        verbose_name = "Complexo esportivo"
        verbose_name_plural = "Complexos esportivos"

    def __str__(self):
        return self.nome


# GERENCIAR CLIENTES (HERANÇA)
class Cliente(Pessoa):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="cliente",
        null=True,
        blank=True,
        verbose_name="Usuário do sistema"
    )
    data_cadastro = models.DateField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"


#  GERENCIAR GESTORES (HERANÇA)
class Gestor(Pessoa):
    complexo_esportivo = models.ForeignKey(
        ComplexoEsportivo,
        on_delete=models.PROTECT,
        related_name="gestores"
    )
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Gestor"
        verbose_name_plural = "Gestores"


#  MODALIDADES
class Modalidade(models.Model):
    nome = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Modalidade"
        verbose_name_plural = "Modalidades"

    def __str__(self):
        return self.nome


# QUADRAS
class Quadra(models.Model):
    nome = models.CharField(max_length=100)
    capacidade = models.PositiveIntegerField()
    valor_hora = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    ativa = models.BooleanField(default=True)

    complexo_esportivo = models.ForeignKey(
        ComplexoEsportivo,
        on_delete=models.CASCADE,
        related_name="quadras"
    )

    modalidade = models.ForeignKey(
        Modalidade,
        on_delete=models.PROTECT,
        related_name="quadras"
    )

    class Meta:
        verbose_name = "Quadra"
        verbose_name_plural = "Quadras"

    def __str__(self):
        return f"{self.nome} ({self.modalidade})"


# HORÁRIOS DE FUNCIONAMENTO
class HorarioFuncionamento(models.Model):
    DIAS = [
        (0, "Segunda"),
        (1, "Terça"),
        (2, "Quarta"),
        (3, "Quinta"),
        (4, "Sexta"),
        (5, "Sábado"),
        (6, "Domingo"),
    ]

    quadra = models.ForeignKey(
        Quadra,
        on_delete=models.CASCADE,
        related_name="horarios"
    )

    dia_semana = models.IntegerField(choices=DIAS)
    hora_abertura = models.TimeField()
    hora_fechamento = models.TimeField()

    class Meta:
        verbose_name = "Horário de funcionamento"
        verbose_name_plural = "Horários de funcionamento"

    def clean(self):
        super().clean()

        if self.hora_abertura and self.hora_fechamento:
            if self.hora_fechamento <= self.hora_abertura:
                raise ValidationError(
                    "O horário de fechamento deve ser maior que o de abertura."
                )

    def __str__(self):
        return f"{self.quadra} - {self.get_dia_semana_display()}"


#  RESERVAS
class Reserva(models.Model):
    STATUS = [
        ("pendente", "Pendente"),
        ("confirmada", "Confirmada"),
        ("cancelada", "Cancelada"),
    ]

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="reservas"
    )

    quadra = models.ForeignKey(
        Quadra,
        on_delete=models.PROTECT,
        related_name="reservas"
    )

    data_hora_inicio = models.DateTimeField()
    data_hora_fim = models.DateTimeField()

    valor_total = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS,
        default="pendente"
    )

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"

    def clean(self):
        super().clean()

        if self.data_hora_inicio and self.data_hora_fim:
            if self.data_hora_fim <= self.data_hora_inicio:
                raise ValidationError(
                    "O horário final deve ser maior que o inicial."
                )

        if (
            self.status != "cancelada"
            and self.quadra_id
            and self.data_hora_inicio
            and self.data_hora_fim
        ):
            conflito = Reserva.objects.filter(
                quadra_id=self.quadra_id,
                data_hora_inicio__lt=self.data_hora_fim,
                data_hora_fim__gt=self.data_hora_inicio
            ).exclude(
                pk=self.pk
            ).exclude(
                status="cancelada"
            )

            if conflito.exists():
                raise ValidationError(
                    "Já existe uma reserva para essa quadra neste horário."
                )

            
    def save(self, *args, **kwargs):
        duracao = self.data_hora_fim - self.data_hora_inicio

        horas = Decimal(str(duracao.total_seconds())) / Decimal("3600")

        self.valor_total = (
            horas * self.quadra.valor_hora
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quadra} - {self.data_hora_inicio:%d/%m/%Y %H:%M}"


    

# PAGAMENTOS
class Pagamento(models.Model):
    FORMAS = [
        ("pix", "PIX"),
        ("cartao", "Cartão"),
        ("dinheiro", "Dinheiro no local"),
    ]

    STATUS = [
        ("pendente", "Pendente"),
        ("pago", "Pago"),
    ]

    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.CASCADE,
        related_name="pagamentos"
    )

    forma = models.CharField(
        max_length=10,
        choices=FORMAS
    )

    valor = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS,
        default="pendente"
    )

    data_pagamento = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"

    def __str__(self):
        return f"Pagamento {self.pk} - {self.get_status_display()}"


#  AVALIAÇÕES
class Avaliacao(models.Model):
    reserva = models.OneToOneField(
        Reserva,
        on_delete=models.CASCADE,
        related_name="avaliacao"
    )

    nota = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

    comentario = models.TextField(blank=True)

    class Meta:
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"

    def __str__(self):
        return f"Reserva {self.reserva_id} - nota {self.nota}"
