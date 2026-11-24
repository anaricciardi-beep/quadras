
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction

from .models import Cidade, Pessoa, Cliente


class CadastroForm(UserCreationForm):

    nome = forms.CharField(
        label="Nome completo",
        max_length=150,
        required=True
    )

    cpf = forms.CharField(
        label="CPF",
        max_length=14,
        required=True
    )

    data_nasc = forms.DateField(
        label="Data de nascimento",
        widget=forms.DateInput(
            attrs={"type": "date"}
        ),
        required=True
    )

    email = forms.EmailField(
        label="E-mail",
        max_length=150,
        required=True
    )

    telefone = forms.CharField(
        label="Telefone",
        max_length=20,
        required=False
    )

    cidade = forms.ModelChoiceField(
        queryset=Cidade.objects.all(),
        label="Cidade",
        empty_label="Selecione sua cidade",
        required=True
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

    # Verifica se o e-mail já está cadastrado
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

    # Verifica o CPF
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

    # Cria usuário e cliente no banco de dados
    @transaction.atomic
    def save(self, commit=True):

        usuario = super().save(commit=False)

        # O e-mail será usado internamente como username
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
