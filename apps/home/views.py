# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView

from apps.home.forms import BookingForm
from apps.home.models import Booking


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


class BookingCreateView(CreateView):
    model = Booking
    form_class = BookingForm
    template_name = "home/booking_create.html"
    success_url = reverse_lazy("home:index")

def turkey_hotel(request):
    return render(request, 'home/turkey_hotel.html')

def egypt_hotel(request):
    return render(request, 'home/egypt_hotel.html')
def odessa_hotel(request):
    return render(request, 'home/odessa_hotel.html')
def thailand_hotel(request):
    return render(request, 'home/thailand_hotel.html')

def about_us(request):
    return render(request, 'home/about-us.html')