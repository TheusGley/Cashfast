from django.db import models


# Create your models here.

# Create your models here.

class Estabelecimento (models.Model):
    
    id = models.IntegerField( null=False, primary_key=True)
    id_vendas =models.CharField(max_length=11, null=True)
    nome =  models.CharField(max_length=100, null=False)
    representante = models.CharField(max_length=100, null=True)
    modelo =models.CharField(max_length=9, null=True)
    maquina = models.CharField(max_length=11, null=True)    
    status = models.CharField(max_length=30, blank=False, null=False)
    ultima_venda = models.CharField(max_length=11, null=True)
    


    def __str__(self) :
        return self.nome
    
class Vendas (models.Model):

    id = models.IntegerField( null=False, primary_key=True)
    id_vendas =models.CharField(max_length=11, null=True)
    nome =  models.CharField(max_length=100, null=False)
    representante = models.CharField(max_length=100, null=True)
    modelo =models.CharField(max_length=9, null=True)
    maquina = models.CharField(max_length=11, null=True)    
    status = models.CharField(max_length=30, blank=False, null=False)
    ultima_venda = models.CharField(max_length=11, null=True)



    def __str__(self) :
        return self.nome

   
    
   




    

     