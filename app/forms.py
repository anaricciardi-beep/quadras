
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from .models import (
    Cidade,
    Pessoa,
    Cliente,
    Reserva,
    Quadra,
    ComplexoEsportivo,
)


# ==========================================
# 1. CADASTRO ANTIGO DE USUÁRIOS
# ==========================================

class CadastroForm(UserCreationForm):

    nome = forms.CharField(
        label="Nome completo",
        max_length=150
    )

    cpf = forms.CharField(
        label="CPF",
        max_length=14
    )

    data_nasc = forms.DateField(
        label="Data de nascimento",
        widget=forms.DateInput(
            attrs={"type": "date"}
        )
    )

    email = forms.EmailField(
        label="E-mail",
        max_length=150
    )

    telefone = forms.CharField(
        label="Telefone",
        max_length=20,
        required=False
    )

    cidade = forms.ModelChoiceField(
        queryset=Cidade.objects.all(),
        label="Cidade",
        empty_label="Selecione sua cidade"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "nome",
            "cpf",
            "data_nasc",
            "email",
            "telefone",
            "cidade"
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if (
            User.objects.filter(email__iexact=email).exists()
            or User.objects.filter(username__iexact=email).exists()
        ):
            raise forms.ValidationError(
                "Este e-mail já está cadastrado."
            )

        return email

    def clean_cpf(self):
        cpf = self.cleaned_data["cpf"]

        numeros = "".join(
            caractere for caractere in cpf
            if caractere.isdigit()
        )

        if len(numeros) != 11:
            raise forms.ValidationError(
                "O CPF deve conter 11 dígitos."
            )

        cpf_formatado = (
            f"{numeros[:3]}.{numeros[3:6]}."
            f"{numeros[6:9]}-{numeros[9:]}"
        )

        if Pessoa.objects.filter(
            cpf__in=[numeros, cpf_formatado]
        ).exists():
            raise forms.ValidationError(
                "Este CPF já está cadastrado."
            )

        return cpf_formatado

    @transaction.atomic
    def save(self, commit=True):
        usuario = super().save(commit=False)

        usuario.username = self.cleaned_data["email"]
        usuario.first_name = self.cleaned_data["nome"]
        usuario.email = self.cleaned_data["email"]

        if commit:
            usuario.save()

            Cliente.objects.create(
                usuario=usuario,
                nome=self.cleaned_data["nome"],
                cpf=self.cleaned_data["cpf"],
                data_nasc=self.cleaned_data["data_nasc"],
                email=self.cleaned_data["email"],
                telefone=self.cleaned_data["telefone"],
                cidade=self.cleaned_data["cidade"]
            )

        return usuario


# ==========================================
# 2. FORMULÁRIO ANTIGO DE RESERVAS
# ==========================================

class ReservaForm(forms.ModelForm):

    nome = forms.CharField(
        label="Nome completo",
        max_length=150
    )

    cpf = forms.CharField(
        label="CPF",
        max_length=14
    )

    data_nasc = forms.DateField(
        label="Data de nascimento",
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control"
            }
        )
    )

    email = forms.EmailField(
        label="E-mail"
    )

    telefone = forms.CharField(
        label="Telefone",
        max_length=20,
        required=False
    )

    cidade = forms.ModelChoiceField(
        queryset=Cidade.objects.all().order_by("nome"),
        label="Cidade onde mora",
        empty_label="Selecione sua cidade"
    )

    data_hora_inicio = forms.DateTimeField(
        label="Data e hora de início",
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M",
            attrs={
                "type": "datetime-local",
                "class": "form-control"
            }
        )
    )

    data_hora_fim = forms.DateTimeField(
        label="Data e hora de término",
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M",
            attrs={
                "type": "datetime-local",
                "class": "form-control"
            }
        )
    )

    class Meta:
        model = Reserva

        fields = [
            "nome",
            "cpf",
            "data_nasc",
            "email",
            "telefone",
            "cidade",
            "quadra",
            "data_hora_inicio",
            "data_hora_fim"
        ]

        widgets = {
            "quadra": forms.Select(
                attrs={"class": "form-control"}
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["quadra"].queryset = (
            Quadra.objects.filter(ativa=True)
            .select_related(
                "complexo_esportivo__cidade",
                "modalidade"
            )
            .order_by(
                "complexo_esportivo__cidade__nome",
                "complexo_esportivo__nome",
                "nome"
            )
        )

        self.fields["quadra"].label_from_instance = (
            lambda quadra: (
                f"{quadra.complexo_esportivo.cidade.nome} - "
                f"{quadra.complexo_esportivo.nome} - "
                f"{quadra.nome} ({quadra.modalidade.nome})"
            )
        )

    def clean_cpf(self):
        cpf = self.cleaned_data["cpf"]

        numeros = "".join(
            caractere for caractere in cpf
            if caractere.isdigit()
        )

        if len(numeros) != 11:
            raise forms.ValidationError(
                "O CPF deve conter 11 dígitos."
            )

        return (
            f"{numeros[:3]}.{numeros[3:6]}."
            f"{numeros[6:9]}-{numeros[9:]}"
        )

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    def clean(self):
        dados = super().clean()

        inicio = dados.get("data_hora_inicio")
        fim = dados.get("data_hora_fim")

        if inicio and fim:

            if inicio <= timezone.now():
                self.add_error(
                    "data_hora_inicio",
                    "Escolha uma data e hora futuras."
                )

            if fim <= inicio:
                self.add_error(
                    "data_hora_fim",
                    "O horário final deve ser maior que o inicial."
                )

        return dados


# ==========================================
# 3. CADASTRO DE CLIENTES PELO SISTEMA
# ==========================================

class ClienteCadastroForm(forms.Form):

    nome = forms.CharField(
        label="Nome completo",
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        )
    )

    cpf = forms.CharField(
        label="CPF",
        max_length=14,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "000.000.000-00"
            }
        )
    )

    data_nasc = forms.DateField(
        label="Data de nascimento",
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control"
            }
        )
    )

    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(
            attrs={"class": "form-control"}
        )
    )

    telefone = forms.CharField(
        label="Telefone",
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        )
    )

    cidade_nome = forms.CharField(
        label="Cidade onde mora",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ex.: Varginha"
            }
        )
    )

    uf = forms.CharField(
        label="UF",
        max_length=2,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ex.: MG"
            }
        )
    )

    def clean_nome(self):
        return self.cleaned_data["nome"].strip()

    def clean_cidade_nome(self):
        cidade = self.cleaned_data["cidade_nome"].strip()

        if not cidade:
            raise forms.ValidationError(
                "Informe a cidade do cliente."
            )

        return cidade

    def clean_uf(self):
        uf = self.cleaned_data["uf"].strip().upper()

        if len(uf) != 2 or not uf.isalpha():
            raise forms.ValidationError(
                "Informe uma UF válida com duas letras."
            )

        return uf

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    def clean_cpf(self):
        cpf = self.cleaned_data["cpf"]

        numeros = "".join(
            caractere for caractere in cpf
            if caractere.isdigit()
        )

        if len(numeros) != 11:
            raise forms.ValidationError(
                "O CPF deve conter 11 dígitos."
            )

        cpf_formatado = (
            f"{numeros[:3]}.{numeros[3:6]}."
            f"{numeros[6:9]}-{numeros[9:]}"
        )

        if Pessoa.objects.filter(
            cpf__in=[numeros, cpf_formatado]
        ).exists():
            raise forms.ValidationError(
                "Já existe uma pessoa cadastrada com este CPF."
            )

        return cpf_formatado


# ==========================================
# 4. RESERVAS PELO PAINEL ADMINISTRATIVO
# HORÁRIOS EM FORMATO BRASILEIRO
# ==========================================

class ReservaGerenciamentoForm(forms.ModelForm):

    data_hora_inicio = forms.DateTimeField(
        label="Data e hora de início",
        input_formats=["%d/%m/%Y %H:%M"],
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ex.: 30/11/2026 14:00"
            }
        )
    )

    data_hora_fim = forms.DateTimeField(
        label="Data e hora de término",
        input_formats=["%d/%m/%Y %H:%M"],
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ex.: 30/11/2026 15:00"
            }
        )
    )

    class Meta:
        model = Reserva

        fields = [
            "cliente",
            "quadra",
            "data_hora_inicio",
            "data_hora_fim"
        ]

        widgets = {
            "cliente": forms.Select(
                attrs={"class": "form-control"}
            ),

            "quadra": forms.Select(
                attrs={"class": "form-control"}
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Mostra apenas clientes ativos
        self.fields["cliente"].queryset = (
            Cliente.objects.filter(ativo=True)
            .order_by("nome")
        )

        self.fields["cliente"].label_from_instance = (
            lambda cliente: (
                f"{cliente.nome} - {cliente.cpf}"
            )
        )

        # Mostra apenas quadras ativas
        self.fields["quadra"].queryset = (
            Quadra.objects.filter(ativa=True)
            .select_related(
                "complexo_esportivo__cidade",
                "modalidade"
            )
            .order_by(
                "complexo_esportivo__cidade__nome",
                "complexo_esportivo__nome",
                "nome"
            )
        )

        self.fields["quadra"].label_from_instance = (
            lambda quadra: (
                f"{quadra.complexo_esportivo.cidade.nome} - "
                f"{quadra.complexo_esportivo.nome} - "
                f"{quadra.nome} ({quadra.modalidade.nome})"
            )
        )

    def clean(self):
        dados = super().clean()

        inicio = dados.get("data_hora_inicio")
        fim = dados.get("data_hora_fim")

        if inicio and inicio <= timezone.now():
            self.add_error(
                "data_hora_inicio",
                "Escolha uma data e hora futuras."
            )

        if inicio and fim and fim <= inicio:
            self.add_error(
                "data_hora_fim",
                "O término deve ser posterior ao início."
            )

        return dados


# ==========================================
# 5. CADASTRO DE COMPLEXOS ESPORTIVOS
# ==========================================

class ComplexoCadastroForm(forms.ModelForm):

    class Meta:
        model = ComplexoEsportivo

        fields = [
            "nome",
            "endereco"
        ]

        labels = {
            "nome": "Nome do complexo",
            "endereco": "Endereço do complexo"
        }

        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nome do complexo"
                }
            ),

            "endereco": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Rua, número e bairro"
                }
            )
        }
