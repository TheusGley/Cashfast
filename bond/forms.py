from django.forms import ModelForm
from .models import Estabelecimento
from django import forms

class EstabelecimentoForm(forms.ModelForm):
    
    
    class Meta:
            model = Estabelecimento
            fields = ['nome', 'representante', 'modelo' ,'maquina' , 'status']  
           
            widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'id':"text-input", 'name':"text-input"}),
            'representante': forms.TextInput(attrs={'class': 'form-control', 'id':"text-input", 'name':"text-input", }),
            'modelo': forms.TextInput(attrs={'class': 'form-control', 'id':"text-input", 'name':"text-input", 'placeholder':"{{estabelecimento.modelo}}" }),
            'maquina': forms.TextInput(attrs={'class': 'form-control', 'id':"text-input", 'name':"text-input", 'placeholder':"{{estabelecimento.maquina}}" }),
            'status': forms.TextInput(attrs={'class': 'form-control', 'id':"text-input", 'name':"text-input", 'placeholder':"{{estabelecimento.status}}" }),
            }  