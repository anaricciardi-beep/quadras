
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction

from .models import *
from .forms import (
    CadastroForm,
    ClienteCadastroForm,
    ReservaGerenciamentoForm
)


# ==========================================
# PÁGINA INICIAL
# ==========================================

class IndexView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "index.html")


# ==========================================
# CONSULTAS
# ==========================================

class CidadesView(View):
    def get(self, request, *args, **kwargs):
        cidades = Cidade.objects.all().order_by("nome")
        return render(request, "cidades.html", {
            "cidades": cidades
        })


class PessoasView(View):
    def get(self, request, *args, **kwargs):
        pessoas = Pessoa.objects.all()
        return render(request, "pessoas.html", {
            "pessoas": pessoas
        })


class ClientesView(View):
    def get(self, request, *args, **kwargs):
        clientes = (
            Cliente.objects.select_related("cidade")
            .all()
            .order_by("nome")
        )

        return render(request, "clientes.html", {
            "clientes": clientes
        })


class GestoresView(View):
    def get(self, request, *args, **kwargs):
        gestores = Gestor.objects.all()
        return render(request, "gestores.html", {
            "gestores": gestores
        })


class ComplexosView(View):
    def get(self, request, *args, **kwargs):
        complexos = ComplexoEsportivo.objects.all()
        return render(request, "complexos.html", {
            "complexos": complexos
        })


class ModalidadesView(View):
    def get(self, request, *args, **kwargs):
        modalidades = Modalidade.objects.all()
        return render(request, "modalidades.html", {
            "modalidades": modalidades
        })


class QuadrasView(View):
    def get(self, request, *args, **kwargs):
        quadras = Quadra.objects.all().order_by(
            "complexo_esportivo__cidade__nome",
            "complexo_esportivo__nome",
            "nome"
        )

        return render(request, "quadras.html", {
            "quadras": quadras
        })


class HorariosView(View):
    def get(self, request, *args, **kwargs):
        horarios = HorarioFuncionamento.objects.all()
        return render(request, "horarios.html", {
            "horarios": horarios
        })


# ==========================================
# CONSULTAR RESERVAS
# ==========================================

class ReservasView(View):
    def get(self, request, *args, **kwargs):

        reservas = (
            Reserva.objects
            .select_related(
                "cliente",
                "quadra",
                "quadra__complexo_esportivo"
            )
            .order_by("-data_hora_inicio")
        )

        return render(request, "reservas.html", {
            "reservas": reservas
        })


class PagamentosView(View):
    def get(self, request, *args, **kwargs):
        pagamentos = Pagamento.objects.all()
        return render(request, "pagamentos.html", {
            "pagamentos": pagamentos
        })


class AvaliacoesView(View):
    def get(self, request, *args, **kwargs):
        avaliacoes = Avaliacao.objects.all()
        return render(request, "avaliacoes.html", {
            "avaliacoes": avaliacoes
        })


# ==========================================
# CADASTRO ANTIGO DE USUÁRIO
# Mantido para não quebrar a URL existente
# ==========================================

def cadastro(request):

    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        form = CadastroForm(request.POST)

        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect("index")
    else:
        form = CadastroForm()

    return render(request, "cadastro.html", {
        "form": form
    })


# ==========================================
# CADASTRAR CLIENTE PELO PAINEL
# ==========================================

@staff_member_required
def cadastrar_cliente(request):

    if request.method == "POST":
        form = ClienteCadastroForm(request.POST)

        if form.is_valid():
            dados = form.cleaned_data

            with transaction.atomic():

                # Procura a cidade no banco
                cidade = Cidade.objects.filter(
                    nome__iexact=dados["cidade_nome"],
                    uf__iexact=dados["uf"]
                ).first()

                # Cadastra a cidade, se necessário
                if cidade is None:
                    cidade = Cidade.objects.create(
                        nome=dados["cidade_nome"],
                        uf=dados["uf"]
                    )

                # Salva o cliente
                Cliente.objects.create(
                    nome=dados["nome"],
                    cpf=dados["cpf"],
                    data_nasc=dados["data_nasc"],
                    email=dados["email"],
                    telefone=dados["telefone"],
                    cidade=cidade
                )

            messages.success(
                request,
                "Cliente cadastrado com sucesso!"
            )

            return redirect("cadastrar_cliente")

    else:
        form = ClienteCadastroForm()

    return render(request, "cadastrar_cliente.html", {
        "form": form
    })


# ==========================================
# REGISTRAR RESERVA PELO PAINEL
# ==========================================

@staff_member_required
def reservar(request):

    if request.method == "POST":
        form = ReservaGerenciamentoForm(request.POST)

        if form.is_valid():

            # Cria a reserva com os dados do formulário
            reserva = form.save(commit=False)

            # Como o administrador registrou a reserva,
            # ela já fica confirmada
            reserva.status = "confirmada"

            # O Model calcula o valor automaticamente
            reserva.save()

            valor = f"{reserva.valor_total:.2f}".replace(".", ",")

            messages.success(
                request,
                f"Reserva nº {reserva.pk} registrada com sucesso! "
                f"Cliente: {reserva.cliente.nome}. "
                f"Quadra: {reserva.quadra.nome}. "
                f"Valor total: R$ {valor}. "
                f"Situação: Confirmada."
            )

            return redirect("reservar")

    else:
        form = ReservaGerenciamentoForm()

    return render(request, "reservar.html", {
        "form": form
    })

# CONFIRMAR OU CANCELAR RESERVA

from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError


@staff_member_required
@require_POST
def alterar_status_reserva(request, reserva_id, acao):

    # Busca a reserva no banco de dados
    reserva = get_object_or_404(Reserva, id=reserva_id)

    # Define as ações permitidas
    if acao == "confirmar":
        novo_status = "confirmada"

    elif acao == "cancelar":
        novo_status = "cancelada"

    else:
        messages.error(request, "Ação inválida.")
        return redirect("reservas")

    # Se já estiver na situação solicitada
    if reserva.status == novo_status:
        messages.info(
            request,
            "A reserva já está nessa situação."
        )
        return redirect("reservas")

    # Altera a situação
    reserva.status = novo_status

    # Antes de confirmar, verifica as regras
    # do Model, incluindo conflitos de horários
    if novo_status == "confirmada":
        try:
            reserva.full_clean()

        except ValidationError:
            messages.error(
                request,
                "Não foi possível confirmar a reserva. "
                "Verifique os dados e possíveis "
                "conflitos de horários."
            )
            return redirect("reservas")

    # Salva a alteração no PostgreSQL
    reserva.save(update_fields=["status"])

    messages.success(
        request,
        f"Reserva nº {reserva.id} "
        f"{novo_status} com sucesso!"
    )

    return redirect("reservas")

# CADASTRAR COMPLEXO ESPORTIVO PELO SITE

from .forms import ComplexoCadastroForm

@staff_member_required
def cadastrar_complexo(request):

    if request.method == "POST":
        form = ComplexoCadastroForm(request.POST)

        if form.is_valid():

            with transaction.atomic():

                # Procura Poços de Caldas no banco
                cidade = Cidade.objects.filter(
                    nome__iexact="Poços de Caldas",
                    uf__iexact="MG"
                ).first()

                # Se não existir, cadastra a cidade
                if cidade is None:
                    cidade = Cidade.objects.create(
                        nome="Poços de Caldas",
                        uf="MG"
                    )

                # Prepara o complexo
                complexo = form.save(commit=False)

                # Define a cidade automaticamente
                complexo.cidade = cidade

                # Salva no PostgreSQL
                complexo.save()

            messages.success(
                request,
                "Complexo esportivo cadastrado com sucesso!"
            )

            return redirect("cadastrar_complexo")

    else:
        form = ComplexoCadastroForm()

    return render(
        request,
        "cadastrar_complexo.html",
        {"form": form}
    )

