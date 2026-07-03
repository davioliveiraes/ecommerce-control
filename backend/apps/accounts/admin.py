from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import Empresa
from .username import USERNAME_MENSAGEM, normalizar_username, username_valido


class EmpresaAdminForm(forms.ModelForm):
    """
    Expõe as credenciais de acesso (que ficam no User) junto dos dados da
    empresa: usuário e e-mail de login, ambos editáveis pelo admin.
    """

    username = forms.CharField(
        label="usuário de acesso",
        help_text="Usuário usado no login (3–30 caracteres, minúsculos).",
    )
    email = forms.EmailField(
        label="e-mail de acesso",
        help_text="E-mail do usuário responsável (também aceito no login).",
    )

    class Meta:
        model = Empresa
        fields = ("user", "nome", "cnpj", "username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["username"].initial = self.instance.user.username
            self.fields["email"].initial = self.instance.user.email

    def clean_username(self):
        value = normalizar_username(self.cleaned_data["username"])
        # Contas legadas usam o e-mail como username; manter o valor atual
        # sem mexer é permitido, só um username novo precisa seguir o formato.
        atual = self.instance.user.username if self.instance.pk else None
        if value != atual and not username_valido(value):
            raise forms.ValidationError(USERNAME_MENSAGEM)
        return value

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    def clean(self):
        cleaned = super().clean()
        username = cleaned.get("username")
        email = cleaned.get("email")
        user = cleaned.get("user") if not self.instance.pk else self.instance.user
        if user is None:
            return cleaned
        outros = get_user_model().objects.exclude(pk=user.pk)
        if username and outros.filter(username__iexact=username).exists():
            self.add_error("username", "Já existe uma conta com este usuário.")
        if email and outros.filter(
            Q(email__iexact=email) | Q(username__iexact=email)
        ).exists():
            self.add_error("email", "Já existe uma conta com este e-mail.")
        return cleaned

    def save(self, commit=True):
        # O admin chama save(commit=False) e depois salva só a empresa em
        # save_model; o User é salvo aqui para as credenciais persistirem.
        empresa = super().save(commit=False)
        user = empresa.user
        user.username = self.cleaned_data["username"]
        user.email = self.cleaned_data["email"]
        user.save(update_fields=["username", "email"])
        if commit:
            empresa.save()
        return empresa


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    form = EmpresaAdminForm
    list_display = ("nome", "cnpj", "username", "email", "criado_em")
    search_fields = ("nome", "cnpj", "user__username", "user__email")

    @admin.display(description="usuário de acesso", ordering="user__username")
    def username(self, obj):
        return obj.user.username

    @admin.display(description="e-mail de acesso", ordering="user__email")
    def email(self, obj):
        return obj.user.email
