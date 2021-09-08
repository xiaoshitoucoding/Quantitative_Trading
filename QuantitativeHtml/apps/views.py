#coding = utf-8
from django.shortcuts import render, redirect
from django.http import HttpResponse
import urllib
from django import forms
import os
# from httplib import BadStatusLine
# from urllib2 import quote
# Create your views here.
from django.conf import settings
import shutil
from os.path import basename
import logging
import time
import base64
import re
import logging
from . import models
from . import forms

pwd = os.getcwd()
father_path=os.path.abspath(os.path.dirname(pwd)+os.path.sep+".")
script_cmd_pre = 'python ' + father_path + '/common/HtmlScript.py '


def CustomHttpResponse(response_text):
    return HttpResponse("<pre>" + response_text + "</pre>")


def index(request):
    

    volume_form = forms.VolumesForm()
    return render(request, 'index.html', locals())


def IncreaseVolume(request):
    context = {}
    if request.method == 'POST':
        volumedate_form = forms.VolumesForm(request.POST)
        if volumedate_form.is_valid():
            short_xd = volumedate_form.cleaned_data.get('short_xd')
            long_xd = volumedate_form.cleaned_data.get('long_xd')
            times = volumedate_form.cleaned_data.get('times')
            total_asset = volumedate_form.cleaned_data.get('total_asset')
            price_times = volumedate_form.cleaned_data.get('price_times')
            env = request.POST['env'].strip()
            script_cmd = "{} {} {} {} {} {} {} {}".format(script_cmd_pre, env, 'IncreaseVolume', total_asset, short_xd,  long_xd, times, price_times)
            logging.debug(script_cmd)
            result = os.popen(script_cmd).read()
            context = locals()
            return CustomHttpResponse(result)

    volume_form = forms.VolumesForm()
    return render(request, 'IncreaseVolume.html', locals())


def BreakAndVolume(request):
    context = {}
    if request.method == 'POST':
        break_form = forms.BreakAndVolume(request.POST)
        if break_form.is_valid():
            env = request.POST['env'].strip()
            total_asset = break_form.cleaned_data.get('total_asset')
            xd = break_form.cleaned_data.get('xd')
            volume_rank_min = break_form.cleaned_data.get('volume_rank_min')
            # volume_rank_max = break_form.cleaned_data.get('volume_rank_max')
            volume_rank_max = 1
            script_cmd = "{} {} {} {} {} {} {}".format(script_cmd_pre, env, 'BreakAndVolume', total_asset, xd,  volume_rank_min, volume_rank_max)
            logging.debug(script_cmd)
            result = os.popen(script_cmd).read()
            context = locals()
            return CustomHttpResponse(result)

    break_form = forms.BreakAndVolume()
    return render(request, 'BreakAndVolume.html', locals())


def StockShape(request):
    context = {}
    if request.method == 'POST':
        shape_form = forms.StockShapeForm(request.POST)
        if shape_form.is_valid():
            env = request.POST['env'].strip()
            shape_type = request.POST['shape'].strip()
            total_asset = shape_form.cleaned_data.get('total_asset')
            xd = shape_form.cleaned_data.get('xd')
            script_cmd = "{} {} {} {} {} {}".format(script_cmd_pre, env, 'StockShape', total_asset, xd, shape_type)
            logging.debug(script_cmd)
            result = os.popen(script_cmd).read()
            context = locals()
            return CustomHttpResponse(result)

    shape_form = forms.StockShapeForm()
    return render(request, 'StockShape.html', locals())


def ChilliPepper(request):
    context = {}
    if request.method == 'POST':
        chillipepper_form = forms.ChilliPepperForm(request.POST)
        if chillipepper_form.is_valid():
            env = request.POST['env'].strip()
            total_asset = chillipepper_form.cleaned_data.get('total_asset')
            xd = chillipepper_form.cleaned_data.get('xd')
            up_deg_threshold = chillipepper_form.cleaned_data.get('up_deg_threshold')
            script_cmd = "{} {} {} {} {} {}".format(script_cmd_pre, env, 'ChilliPepper', total_asset, xd, up_deg_threshold)
            logging.debug(script_cmd)
            result = os.popen(script_cmd).read()
            context = locals()
            return CustomHttpResponse(result)

    chillipepper_form = forms.ChilliPepperForm()
    return render(request, 'ChilliPepper.html', locals())


def IndustryInfo(request):
    context = {}
    if request.method == 'POST':
        industry_form = forms.IndustryInfoForm(request.POST)
        if industry_form.is_valid():
            env = request.POST['env'].strip()
            xd = industry_form.cleaned_data.get('xd')
            script_cmd = "{} {} {} {} ".format(script_cmd_pre, env, 'IndustryInfo', xd)
            logging.debug(script_cmd)
            result = os.popen(script_cmd).read()
            context = locals()
            return CustomHttpResponse(result)

    industry_form = forms.IndustryInfoForm()
    return render(request, 'IndustryInfo.html', locals())







