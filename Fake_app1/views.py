from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login,logout
from django.contrib import messages
from .models import *

import numpy as np
import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

#注册
def register(request):
    if request.method=='POST':
        form=UserCreationForm(request.POST)
        # print(form.is_valid())
        if form.is_valid():
            user=form.save()
            login(request,user)
            messages.success(request,"注册成功！")
            return redirect('login')
    else:
        form=UserCreationForm()
    return render(request,'register.html',{'form':form})

