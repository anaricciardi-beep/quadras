
from django.contrib import admin
from django.contrib.auth.models import Group

from .models import (
    Cidade,
    Cliente,
    ComplexoEsportivo,
    HorarioFuncionamento,
    Modalidade,
    Quadra,
    Reserva,
)

# INLINES

# Quadras de cada complexo esportivo
class QuadraInline(admin.TabularInline):
    model = Quadra
    extra = 0


# Horários de cada quadra
class HorarioInline(admin.TabularInline):
    model = HorarioFuncionamento
    extra = 0


# Reservas de cada cliente
class ReservaInline(admin.TabularInline):
    model = Reserva
    extra = 0
    readonly_fields = ("valor_total",)

# CIDADES

@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    list_display = ("nome", "uf")
    search_fields = ("nome",)
    list_filter = ("uf",)


# CLIENTES

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "cpf",
        "email",
        "cidade",
        "data_cadastro",
        "ativo",
    )

    search_fields = ("nome", "cpf")
    list_filter = ("ativo",)
    inlines = [ReservaInline]


# COMPLEXOS ESPORTIVOS

@admin.register(ComplexoEsportivo)
class ComplexoEsportivoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "endereco",
        "cidade",
    )

    search_fields = ("nome", "endereco")
    list_filter = ("cidade",)
    inlines = [QuadraInline]

# MODALIDADES


@admin.register(Modalidade)
class ModalidadeAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome",)


# QUADRAS

@admin.register(Quadra)
class QuadraAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "modalidade",
        "complexo_esportivo",
        "capacidade",
        "valor_hora",
        "ativa",
    )

    search_fields = ("nome",)
    list_filter = (
        "modalidade",
        "complexo_esportivo",
        "ativa",
    )

    inlines = [HorarioInline]

# HORÁRIOS DE FUNCIONAMENTO


@admin.register(HorarioFuncionamento)
class HorarioFuncionamentoAdmin(admin.ModelAdmin):
    list_display = (
        "quadra",
        "dia_semana",
        "hora_abertura",
        "hora_fechamento",
    )

    list_filter = ("dia_semana", "quadra")

# RESERVAS

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = (
        "cliente",
        "quadra",
        "data_hora_inicio",
        "data_hora_fim",
        "valor_total",
        "status",
    )

    search_fields = (
        "cliente__nome",
        "quadra__nome",
    )

    list_filter = ("status", "quadra")

    readonly_fields = ("valor_total",)


# OCULTAR GRUPOS DO DJANGO ADMIN


if admin.site.is_registered(Group):
    admin.site.unregister(Group)
