from django.contrib import admin
from .models import *

# Register your models here.



class admin_estabelecimento (admin.ModelAdmin):
    
    list_display = ('nome' ,'representante', 'maquina','modelo', 'status')
    search_fields = ('^nome',)
    ordering = ('nome', )


admin.site.register(Estabelecimento, admin_estabelecimento)




# Funçao para mudar Status para 1 = Ativo, 2= Estoque, 3= Parado, 4= Pax e 5=  Retirar, conforme a coluna sts.

# @admin.action(description='Marcar') # opcao no acoes

# class ArticleAdmin(admin.ModelAdmin):
#     actions = ('make_published',)
    
    
#     def make_published(modeladmin, request, queryset):
#         count = queryset.update(status ='Parado') #Coloque o status que deseja.
                    
#     list_display = ('nome', 'maquina','modelo','status', 'sts')
#     search_fields = ( '^sts',)
#     ordering = ('sts', )
    

# admin.site.register(Estabelecimento, ArticleAdmin)
    
