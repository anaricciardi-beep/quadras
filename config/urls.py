
from django.contrib import admin
from django.urls import path
from django.contrib.admin.views.decorators import staff_member_required

from app.views import *


urlpatterns = [

    # Django Admin
    path('admin/', admin.site.urls),

    # Painel inicial
    path(
        '',
        staff_member_required(IndexView.as_view()),
        name='index'
    ),

    # Cadastro antigo
    path(
        'cadastro/',
        staff_member_required(cadastro),
        name='cadastro'
    ),

    # Cadastrar clientes
    path(
        'clientes/cadastrar/',
        cadastrar_cliente,
        name='cadastrar_cliente'
    ),

    # Nova reserva
    path(
        'reservar/',
        staff_member_required(reservar),
        name='reservar'
    ),

    # Confirmar ou cancelar reserva
    path(
        'reservas/<int:reserva_id>/<str:acao>/',
        alterar_status_reserva,
        name='alterar_status_reserva'
    ),

    # Consultas
    path('cidades/', staff_member_required(CidadesView.as_view()), name='cidades'),
    path('complexos/', staff_member_required(ComplexosView.as_view()), name='complexos'),
    path('modalidades/', staff_member_required(ModalidadesView.as_view()), name='modalidades'),
    path('quadras/', staff_member_required(QuadrasView.as_view()), name='quadras'),
    path('horarios/', staff_member_required(HorariosView.as_view()), name='horarios'),

    # Gerenciamento
    path('pessoas/', staff_member_required(PessoasView.as_view()), name='pessoas'),
    path('clientes/', staff_member_required(ClientesView.as_view()), name='clientes'),
    path('gestores/', staff_member_required(GestoresView.as_view()), name='gestores'),
    path('reservas/', staff_member_required(ReservasView.as_view()), name='reservas'),
    path('pagamentos/', staff_member_required(PagamentosView.as_view()), name='pagamentos'),
    path('avaliacoes/', staff_member_required(AvaliacoesView.as_view()), name='avaliacoes'),
]
