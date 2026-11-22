
from django.shortcuts import render
from django.views import View
from .models import *


class IndexView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')


class CidadesView(View):
    def get(self, request, *args, **kwargs):
        cidades = Cidade.objects.all()
        return render(request, 'cidades.html', {'cidades': cidades})


class PessoasView(View):
    def get(self, request, *args, **kwargs):
        pessoas = Pessoa.objects.all()
        return render(request, 'pessoas.html', {'pessoas': pessoas})


class ClientesView(View):
    def get(self, request, *args, **kwargs):
        clientes = Cliente.objects.all()
        return render(request, 'clientes.html', {'clientes': clientes})


class GestoresView(View):
    def get(self, request, *args, **kwargs):
        gestores = Gestor.objects.all()
        return render(request, 'gestores.html', {'gestores': gestores})


class ComplexosView(View):
    def get(self, request, *args, **kwargs):
        complexos = ComplexoEsportivo.objects.all()
        return render(request, 'complexos.html', {'complexos': complexos})


class ModalidadesView(View):
    def get(self, request, *args, **kwargs):
        modalidades = Modalidade.objects.all()
        return render(request, 'modalidades.html', {'modalidades': modalidades})


class QuadrasView(View):
    def get(self, request, *args, **kwargs):
        quadras = Quadra.objects.all()
        return render(request, 'quadras.html', {'quadras': quadras})


class HorariosView(View):
    def get(self, request, *args, **kwargs):
        horarios = HorarioFuncionamento.objects.all()
        return render(request, 'horarios.html', {'horarios': horarios})


class ReservasView(View):
    def get(self, request, *args, **kwargs):
        reservas = Reserva.objects.all()
        return render(request, 'reservas.html', {'reservas': reservas})


class PagamentosView(View):
    def get(self, request, *args, **kwargs):
        pagamentos = Pagamento.objects.all()
        return render(request, 'pagamentos.html', {'pagamentos': pagamentos})


class AvaliacoesView(View):
    def get(self, request, *args, **kwargs):
        avaliacoes = Avaliacao.objects.all()
        return render(request, 'avaliacoes.html', {'avaliacoes': avaliacoes})
