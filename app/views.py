
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login

from .models import *
from .forms import CadastroForm


# Página inicial
class IndexView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')


# Consulta de cidades
class CidadesView(View):
    def get(self, request, *args, **kwargs):
        cidades = Cidade.objects.all()
        return render(request, 'cidades.html', {'cidades': cidades})


# Consulta de pessoas
class PessoasView(View):
    def get(self, request, *args, **kwargs):
        pessoas = Pessoa.objects.all()
        return render(request, 'pessoas.html', {'pessoas': pessoas})


# Consulta de clientes
class ClientesView(View):
    def get(self, request, *args, **kwargs):
        clientes = Cliente.objects.all()
        return render(request, 'clientes.html', {'clientes': clientes})


# Consulta de gestores
class GestoresView(View):
    def get(self, request, *args, **kwargs):
        gestores = Gestor.objects.all()
        return render(request, 'gestores.html', {'gestores': gestores})


# Consulta de complexos esportivos
class ComplexosView(View):
    def get(self, request, *args, **kwargs):
        complexos = ComplexoEsportivo.objects.all()
        return render(request, 'complexos.html', {'complexos': complexos})


# Consulta de modalidades
class ModalidadesView(View):
    def get(self, request, *args, **kwargs):
        modalidades = Modalidade.objects.all()
        return render(request, 'modalidades.html', {'modalidades': modalidades})


# Consulta de quadras
class QuadrasView(View):
    def get(self, request, *args, **kwargs):
        quadras = Quadra.objects.all()
        return render(request, 'quadras.html', {'quadras': quadras})


# Consulta de horários
class HorariosView(View):
    def get(self, request, *args, **kwargs):
        horarios = HorarioFuncionamento.objects.all()
        return render(request, 'horarios.html', {'horarios': horarios})


# Consulta de reservas
class ReservasView(View):
    def get(self, request, *args, **kwargs):
        reservas = Reserva.objects.all()
        return render(request, 'reservas.html', {'reservas': reservas})


# Consulta de pagamentos
class PagamentosView(View):
    def get(self, request, *args, **kwargs):
        pagamentos = Pagamento.objects.all()
        return render(request, 'pagamentos.html', {'pagamentos': pagamentos})


# Consulta de avaliações
class AvaliacoesView(View):
    def get(self, request, *args, **kwargs):
        avaliacoes = Avaliacao.objects.all()
        return render(request, 'avaliacoes.html', {'avaliacoes': avaliacoes})


# Cadastro de novos usuários pelo site
def cadastro(request):

    # Se o usuário já estiver conectado,
    # retorna para a página inicial
    if request.user.is_authenticated:
        return redirect('index')

    # Recebe os dados enviados pelo formulário
    if request.method == 'POST':
        form = CadastroForm(request.POST)

        # Valida e salva o usuário
        if form.is_valid():
            usuario = form.save()

            # Faz login automaticamente
            login(request, usuario)

            return redirect('index')

    else:
        # Exibe o formulário vazio
        form = CadastroForm()

    return render(request, 'cadastro.html', {'form': form})
