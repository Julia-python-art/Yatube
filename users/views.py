from django.views.generic import CreateView

from django.urls import reverse_lazy
# позволяет получить URL по параметру "name" функции path()

from .forms import CreationForm



class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy("login") #  где login — это параметр "name" в path()
    template_name = "signup.html"  # где login — это параметр "name" в path()
