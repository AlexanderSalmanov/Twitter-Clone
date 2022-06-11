from django.shortcuts import render, redirect
from django.views import generic

from profiles.models import Profile
# Create your views here.

class ProfileSearchView(generic.ListView):
    template_name = 'search/results.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        request = self.request
        query = request.GET.get('q')
        context['query'] = query
        # if context['query'] != '':
        if query == '*':
            context['results'] = Profile.objects.all()
        else:
            context['results'] = Profile.objects.filter(nickname__icontains=query)
        # else:
        #     return redirect('/')
        return context

    def get_queryset(self):
        request = self.request
        query = request.GET.get('q')
        if query == '*':
            results = Profile.objects.all()
        else:
            results = Profile.objects.filter(nickname__icontains=query)
        return results
