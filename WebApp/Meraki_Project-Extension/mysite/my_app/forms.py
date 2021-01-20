from django import forms
from django.core import validators
from django.forms.widgets import NumberInput

motives=(('Consulta General','Consulta General'),
        ('Consulta COVID','Consulta COVID'),
        ('Otros','Otros'))

times = ((' 08 :00' ,' 08 :00' ),
        (' 08 :30' ,' 08 :30' ),
        (' 09 :00' ,' 09 :00' ),
        (' 09 :30' ,' 09 :30' ),
        (' 10 :00' ,' 10 :00' ),
        (' 10 :30' ,' 10 :30' ),
        (' 11 :00' ,' 11 :00' ),
        (' 11 :30' ,' 11 :30' ),
        (' 12 :00' ,' 12 :00' ),
        (' 12 :30' ,' 12 :30' ),
        (' 13 :00' ,' 13 :00' ),
        (' 13 :30' ,' 13 :30' ),
        (' 14 :00' ,' 14 :00' ),
        (' 14 :30' ,' 14 :30' ),
        (' 15 :00' ,' 15 :00' ),
        (' 15 :30' ,' 15 :30' ),
        (' 16 :00' ,' 16 :00' ),
        (' 16 :30' ,' 16 :30' ),
        (' 17 :00' ,' 17 :00' ),
        (' 17 :30' ,' 17 :30' ),
        (' 18 :00' ,' 18 :00' ),
        (' 18 :30' ,' 18 :30' ),
        (' 19 :00' ,' 19 :00' ),
        (' 19 :30' ,' 19 :30' ),
        (' 20 :00' ,' 20 :00' ),
        (' 20 :30' ,' 20 :30' ))

class doctors(forms.Form):
    Nombre = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Nombre"}))
    Primer_Apellido=forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Primer Apellido"}))
    Segundo_Apellido=forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Segundo Apellido"}),required=False)
    #Fecha=forms.DateField(widget=forms.SelectDateWidget())
    Fecha_Solicitada=forms.DateField(widget=NumberInput(attrs={'type':'date'}))
    Hora=forms.ChoiceField(choices=times)
    Motivo=forms.ChoiceField(choices=motives)

doctors_mail=(('noreply@gmail.com','Dr. Shawn Murphy'),
            ('mail@mail.com','Dr. Gregory House'),
            ('example.mail@gmail.com','Dr. Foreman Hilton'),
            ('No preference','No preference'))

class patients(forms.Form):
    Nombre= forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Nombre"}))
    Primer_Apellido=forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Primer apellido"}))
    Segundo_Apellido=forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Segundo apellido"}))
    Email= forms.EmailField()
    Medico_Preferido=forms.ChoiceField(choices=doctors_mail)
    Fecha_Solicitada=forms.DateField(widget=NumberInput(attrs={'type':'date'}))
    Hora_Solicitada=forms.ChoiceField(choices=times)
    Sintomas=forms.CharField()


'''
    def clean(self):
        all_clean = super().clean()
        email= all_clean_data['email']
        vemail= all_clean_data['verify_email']

        if email != vmail:
            raise forms.ValidarionError("Make sure emails match")
'''
