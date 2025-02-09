from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate, get_backends
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView
from .forms import CustomUserCreationForm, CustomUserLoginForm
from .models import CustomUser
from django.shortcuts import redirect, render


class CustomRegisterView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        user = form.save()

        backend = next((b for b in get_backends() if isinstance(b, get_backends()[0].__class__)), None)

        if backend:
            user.backend = f"{backend.__module__}.{backend.__class__.__name__}"

        login(self.request, user)
        return redirect("home")


class CustomLoginView(LoginView):
    template_name = "users/login.html"
    authentication_form = CustomUserLoginForm
    redirect_authenticated_user = True

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                return redirect(reverse_lazy("home"))
            else:
                form.add_error(None, "Невірний email або пароль")

        return render(request, self.template_name, {"form": form})


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("login")
