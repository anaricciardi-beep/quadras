
from django.contrib import admin
from django.urls import path
from django.contrib.admin.views.decorators import staff_member_required
from app.views import *


urlpatterns = [
    path('admin/', admin.site.urls),

    # Página inicial
    path('', IndexView.as_view(), name='index'),
    
    path('cidades/', CidadesView.as_view(), name='cidades'),
    path('complexos/', ComplexosView.as_view(), name='complexos'),
    path('modalidades/', ModalidadesView.as_view(), name='modalidades'),
    path('quadras/', QuadrasView.as_view(), name='quadras'),
    path('horarios/', HorariosView.as_view(), name='horarios'),

    path('pessoas/', staff_member_required(PessoasView.as_view()), name='pessoas'),
    path('clientes/', staff_member_required(ClientesView.as_view()), name='clientes'),
    path('gestores/', staff_member_required(GestoresView.as_view()), name='gestores'),
    path('reservas/', staff_member_required(ReservasView.as_view()), name='reservas'),
    path('pagamentos/', staff_member_required(PagamentosView.as_view()), name='pagamentos'),
    path('avaliacoes/', staff_member_required(AvaliacoesView.as_view()), name='avaliacoes'),
]
