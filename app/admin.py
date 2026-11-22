
from django.contrib import admin

from .models import (
    Avaliacao,
    Cidade,
    Cliente,
    ComplexoEsportivo,
    Gestor,
    HorarioFuncionamento,
    Modalidade,
    Pagamento,
    Pessoa,
    Quadra,
    Reserva,
)


# ==========================================
# INLINES
# ==========================================

# Pessoas cadastradas em uma cidade
class PessoaInline(admin.TabularInline):
    model = Pessoa
    extra = 0


# Quadras pertencentes a um complexo esportivo
class QuadraInline(admin.TabularInline):
    model = Quadra
    extra = 1


# Horários de funcionamento de uma quadra
class HorarioInline(admin.TabularInline):
    model = HorarioFuncionamento
    extra = 1


# Reservas realizadas por um cliente
class ReservaInline(admin.TabularInline):
    model = Reserva
    extra = 0
    readonly_fields = ("valor_total",)


# Pagamentos relacionados a uma reserva
class PagamentoInline(admin.TabularInline):
    model = Pagamento
    extra = 1


# Avaliação relacionada a uma reserva
class AvaliacaoInline(admin.TabularInline):
    model = Avaliacao
    extra = 0
    max_num = 1


# ==========================================
# ADMINS
# ==========================================

# RF01 - Gerenciar cidades
@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    list_display = ("nome", "uf")
    search_fields = ("nome",)
    inlines = [PessoaInline]


# RF02 - Gerenciar pessoas
@admin.register(Pessoa)
class PessoaAdmin(admin.ModelAdmin):
    list_display = ("nome", "cpf", "email", "cidade")
    search_fields = ("nome", "cpf")
    list_filter = ("cidade",)


# RF03 - Gerenciar clientes
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome", "cpf", "data_cadastro", "ativo")
    search_fields = ("nome", "cpf")
    list_filter = ("ativo",)
    inlines = [ReservaInline]


# RF04 - Gerenciar gestores
@admin.register(Gestor)
class GestorAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "complexo_esportivo",
        "ativo",
    )
    search_fields = ("nome", "cpf")
    list_filter = ("ativo", "complexo_esportivo")


# RF05 - Gerenciar complexos esportivos
@admin.register(ComplexoEsportivo)
class ComplexoEsportivoAdmin(admin.ModelAdmin):
    list_display = ("nome", "cidade", "telefone")
    search_fields = ("nome", "endereco")
    list_filter = ("cidade",)
    inlines = [QuadraInline]


# RF06 - Gerenciar modalidades
@admin.register(Modalidade)
class ModalidadeAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome",)


# RF07 - Gerenciar quadras
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
    list_filter = ("modalidade", "ativa")
    inlines = [HorarioInline]


# RF08 - Gerenciar horários de funcionamento
@admin.register(HorarioFuncionamento)
class HorarioFuncionamentoAdmin(admin.ModelAdmin):
    list_display = (
        "quadra",
        "dia_semana",
        "hora_abertura",
        "hora_fechamento",
    )
    list_filter = ("dia_semana", "quadra")


# RF09 - Gerenciar reservas
@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = (
        "quadra",
        "cliente",
        "data_hora_inicio",
        "data_hora_fim",
        "valor_total",
        "status",
    )
    search_fields = ("cliente__nome", "quadra__nome")
    list_filter = ("status", "quadra")
    readonly_fields = ("valor_total",)
    inlines = [PagamentoInline, AvaliacaoInline]


# RF10 - Gerenciar pagamentos
@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = (
        "reserva",
        "forma",
        "valor",
        "status",
        "data_pagamento",
    )
    list_filter = ("forma", "status")


# RF11 - Gerenciar avaliações
@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ("reserva", "nota")
    list_filter = ("nota",)
