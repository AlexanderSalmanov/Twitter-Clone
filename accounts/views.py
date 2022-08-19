from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy, reverse
from django.utils.http import is_safe_url
from django.contrib.auth.views import LoginView as BaseLoginView

from .forms import LoginForm, RegisterForm


# Create your views here.


class RegisterView(generic.CreateView):
    template_name = 'accounts/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('hello')
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
            return redirect('profiles:my')
        return super(RegisterView, self).form_valid(form)

class LoginView(generic.FormView):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('hello')

    def form_valid(self, form):

        request = self.request
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None

        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            if is_safe_url(redirect_path, request.get_host()):
                return redirect(redirect_path)
            else:
                return redirect('/')

        return super(LoginView, self).form_invalid(form)
