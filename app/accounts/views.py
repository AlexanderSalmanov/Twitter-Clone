from django.shortcuts import render, redirect
from django.views import generic 
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.conf import settings
from django.urls import reverse_lazy
from django.utils.http import is_safe_url

from .models import User 
from .forms import SignupForm, LoginForm
# Create your views here.

class LoginView(generic.View):
    
    def get(self, *args, **kwargs):
        request = self.request 
        form = LoginForm()
        return render(request, 'accounts/login.html', {'form': form})
    
    def post(self, *args, **kwargs):
        request = self.request 
        form = LoginForm(request.POST)
        next_ = request.GET.get('next') or None 
        next_post = request.POST.get('next') or None
        redirect_path = next_ or next_post or None 
         
        if form.is_valid():
            user = authenticate(
                email=form.cleaned_data.get('email'),
                password=form.cleaned_data.get('password')
            )
            
            if user is not None:
                user_email = User.objects.get(
                    email=form.cleaned_data.get('email')    
                ).email
                login(request, user, backend="django.contrib.auth.backends.ModelBackend")
                messages.success(request, f"You have logged in as {user_email}.")
                # return redirect(settings.LOGIN_REDIRECT_URL)
                if is_safe_url(redirect_path, request.get_host()):
                    return redirect(redirect_path)
                return redirect('/')
            messages.warning(request, "You have provided invalid credentials.")
            return redirect('authentication:login')
        
        

class SignupView(generic.CreateView):
    
    model = User 
    form_class = SignupForm 
    success_url = reverse_lazy('hello')
    redirect_authenticated_user = True 
    template_name = 'accounts/signup.html'
    
    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(self.request, f"You have created an account!")
            return redirect(settings.LOGIN_REDIRECT_URL)         
        return super(SignupView, self).form_valid(form)
    
        
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have logged out.")
    return redirect(settings.LOGOUT_REDIRECT_URL)


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/emails/password_reset_email.html'
    subject_template_name = 'accounts/emails/password_reset_subject.txt'
    success_message = """We've emailed you to give you a brief instruction on 
                        how to reset your password. If you've provided an invalid
                        email address, please try once again. Make sure to check
                        your spam folder."""
    success_url = reverse_lazy('profiles:my')
            


