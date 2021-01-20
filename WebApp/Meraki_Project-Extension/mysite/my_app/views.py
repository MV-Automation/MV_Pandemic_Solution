from django.shortcuts import render

#Login page
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.template import loader
from boto3.dynamodb.conditions import Key, Attr
import boto3
import botocore
from botocore.exceptions import ClientError
import time as Time
from . import AmazonKeys as key


#models
from .models import Doctor
#forms
from . import forms

# Dynamodb resource to table
dynamodb = boto3.resource(
  'dynamodb', aws_access_key_id = key.AccessKey,
  aws_secret_access_key=key.SecretAccessKey,
  region_name='us-east-2')

# Dynamodb Client to select data
dynamodb_client = boto3.client('dynamodb', aws_access_key_id = key.AccessKey,
  aws_secret_access_key=key.SecretAccessKey,
  region_name='us-east-2')

table=dynamodb.Table("Doctors_Agenda")

# Logs site to explore data from DB.
@login_required
def logs(request):
    template = loader.get_template('my_app/logs.html')
    registros = get_access_logs()
    # print(registros)
    context = {
      'registros' : registros
    }
    #print("MANUAL LOG ===================")
    #print(context)

    return HttpResponse(template.render(context, request))

# Call from Dynamo DB
def get_access_logs():
    try:
      table = dynamodb.Table('Faces_Match')
    except botocore.exceptions.ClientError as e:
      # http://stackoverflow.com/questions/33068055/boto3-python-and-how-to-handle-errors
      return 'failed'
    else:
      response = dynamodb_client.scan(TableName='Faces_Match')
      if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        try:
          item = response['Items']
        except KeyError:
          return None
        return item

def login_page(request):
    return render(request,'my_app/login.html')

def index(request):
    return render(request,'my_app/home.html')

def logs_page(request):
    return render(request,'my_app/logs.html')

# Logout view
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

#LOGIN VIEW
def user_login(request):

    if request.method == 'POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        #user athentication
        user=authenticate(username=username, password=password)

        #if login is valid, send the user to the home page
        if user:
            if user.is_active:
                login(request,user)
                #return HttpResponseRedirect(reverse('index'))
                return render(request,'my_app/home.html',{})

            else:
                return HttpResponse("Account Not Active")
        else:
            print("Someone tried to login and failed")
            print("Username: {} and password {}".format(username,password))
            return HttpResponse("Invalid login details suplied.")
    else:
        return render(request,'my_app/login.html',{})

new_register=[]

@login_required
def doctor_view(request):

    form=forms.doctors()
    current_user=request.user

    if request.method=='POST':
        form=forms.doctors(request.POST)
    
        if form.is_valid():
    
            name = form.cleaned_data["Nombre"]
            f_surname = form.cleaned_data["Primer_Apellido"]
            S_surname = form.cleaned_data["Segundo_Apellido"]
            date= form.cleaned_data["Fecha_Solicitada"]
            time= form.cleaned_data["Hora"]
            motive= form.cleaned_data["Motivo"]
    
            print("The name is: " + str(name) + " " + str(f_surname) + " " + str(S_surname))
            print(date)
            print("The time is: " + str(time))
            print(motive)
            print(current_user)
            
            # This is a unique index based on time to identify the entry.     
            unique_key = Time.time()

            new_register.append(( str(unique_key), str(current_user), name, f_surname, S_surname, 
                str(date), str(time), motive))
    
            
        
            for item in new_register:
                table.put_item(Item={'index':item[0], 'user_mail':item[1],'patient_name': item[2],
                'first_surname': item[3], 'second_surname': item[4], 'date':item[5], 'time': item[6],
                'motive': item[7] })

            #Replace the sender name with the address that you want to be your
            #sender address.
            SENDER = "Farmacias del ahorro <davijime@cisco.com>"

            # Replace recipient@example.com with a "To" address. If your account
            # is still in the sandbox, this address must be verified.
            RECIPIENT = str(current_user)

            # The subject line for the email.
            SUBJECT = "Confirmación de registro. Cita: "+ str(unique_key)

            # The email body for recipients with non-HTML email clients.
            BODY_TEXT = ("Tu registro fue realizado con exito.\n\n "
                        "Detalles de confirmación:\r\n"
                         "\rPaciente: " + name + " " + f_surname + " " + S_surname + "\n"
                         "\rFecha: " + str(date) + "\n"
                         "\rHorario: " + str(time) + "\n"
                         "\rMotivo: " + motive + "\n"
                        )
            '''
            # The HTML body of the email
            BODY_HTML = """<html>
            <head></head>
            <body>
              <h1>Detalles de confirmación:</h1>
              <p>Detalles de confirmación:
                           Paciente:  + %name% + %surname% +
                           Fecha: " + %str(date)% +
                           Horario: " + %str(time)% +
                           Motivo: " + %motive% </p>
            </body>
            </html>
            """
            '''

            # The character encoding for the email.
            CHARSET = "UTF-8"

            # Create a new SES resource and specify a region.
            client = boto3.client('ses',aws_access_key_id = key.AccessKey,
            aws_secret_access_key=key.SecretAccessKey,
            region_name='us-east-2')

            # Try to send the email.
            try:
                #Provide the contents of the email.
                response = client.send_email(
                    Destination={
                        'ToAddresses': [
                            RECIPIENT,
                        ],
                    },
                    Message={
                        'Body': {
                            'Text': {
                                'Charset': CHARSET,
                                'Data': BODY_TEXT,
                            },
                        },
                        'Subject': {
                            'Charset': CHARSET,
                            'Data': SUBJECT,
                        },
                    },
                    Source=SENDER,
                )
            # Display an error if something goes wrong.
            except ClientError as e:
                print(e.response['Error']['Message'])
            else:
                print("Email sent! Message ID:"),
                print(response['MessageId'])
            return render(request,'my_app/succesfull.html')
    return render(request,'my_app/doctor_register.html',{'form':form})

def register_patients(request):
    # STATIC VAR FOR SAMPLE 

    form_patient=forms.patients()
    patients_table=dynamodb.Table("Appointment_Info")
    
    if request.method=='POST':
        form_patient=forms.patients(request.POST)

        if form_patient.is_valid():

            patient_name = form_patient.cleaned_data["Nombre"]
            patient_f_surname = form_patient.cleaned_data["Primer_Apellido"]
            patient_s_surname = form_patient.cleaned_data["Segundo_Apellido"]
            patient_email = form_patient.cleaned_data["Email"]
            DOCTOR_EMAIL=form_patient.cleaned_data['Medico_Preferido']
            date = form_patient.cleaned_data["Fecha_Solicitada"]
            time = form_patient.cleaned_data["Hora_Solicitada"]
            patient_symptoms = form_patient.cleaned_data["Sintomas"]


            print("patient name: " + str(patient_name))
            print("patient surname: " + str(patient_f_surname)+ " "+ str(patient_s_surname))
            print(date)
            print("Schedule is: " + str(time))
            print(patient_symptoms)
            print(DOCTOR_EMAIL)

            # This is a unique index based ton time to identify the entry. 
            unique_key = Time.time()
            
            new_patient_entry = []
            # Make a list of usable variables
            new_patient_entry.append((str(unique_key), patient_name, patient_f_surname, patient_s_surname, str(date), 
                str(time), patient_symptoms, patient_email))

            # Insert to the dynamo database the new entry from patient
            for item in new_patient_entry:
                patients_table.put_item(Item={'index':item[0],'patient_name':item[1],'patient_f_surname': item[2], 'patient_s_surname': item[3],
                 'date': item[4], 'time':item[5], 'patient_symptoms': item[6], 'patient_email': item[7] })

            send_mail_to_given_email(patient_email, type = 'patient', patient_entry = new_patient_entry)
            send_mail_to_given_email(DOCTOR_EMAIL, type = 'doctor', patient_entry = new_patient_entry)

            
            return render(request,'my_app/succesfull.html')

    return render(request,'my_app/patient_register.html',{'form_patient':form_patient})


def send_mail_to_given_email(recipient_email, type, patient_entry):
    #Replace the sender name with the address that you want to be your
            #sender address.
            SENDER = "Farmacias del Ahorro <davijime@cisco.com>"

            # Replace recipient@example.com with a "To" address. If your account
            # is still in the sandbox, this address must be verified.
            RECIPIENT = str(recipient_email)

            if type == 'patient':

                # The subject line for the email.
                SUBJECT = "Confirmación de registro a su cita"

                # The email body for recipients with non-HTML email clients.
                BODY_TEXT = ("Su registro ha sido recibido exitosamente. \n\n "
                            "Detalles de su proxima cita médica:\r\n"
                             "\rPaciente: " + patient_entry[0][1] + " " + patient_entry[0][2] + " " +patient_entry[0][3] + "\n"
                             "\rFecha: " + patient_entry[0][4] + "\n"
                             "\rHorario: " + patient_entry[0][5] + "\n"
                             "\rSintomas: " + patient_entry[0][6] + "\n"
                            )
                
                # The character encoding for the email.
                CHARSET = "UTF-8"

                # Create a new SES resource and specify a region.
                client = boto3.client('ses',aws_access_key_id = key.AccessKey,
                aws_secret_access_key=key.SecretAccessKey,
                region_name='us-east-2')

                # Try to send the email.
                try:
                    #Provide the contents of the email.
                    response = client.send_email(
                        Destination={
                            'ToAddresses': [
                                RECIPIENT,
                            ],
                        },
                        Message={
                            'Body': {
                                'Text': {
                                    'Charset': CHARSET,
                                    'Data': BODY_TEXT,
                                },
                            },
                            'Subject': {
                                'Charset': CHARSET,
                                'Data': SUBJECT,
                            },
                        },
                        Source=SENDER,
                    )
                
                # Display an error if something goes wrong.
                except ClientError as e:
                    print(e.response['Error']['Message'])
                    return False
                else:
                    print("Email sent! Message ID:"),
                    print(response['MessageId'])
                    return True
                
            elif type == 'doctor':
                # The subject line for the email.
                SUBJECT = "NUEVA CITA: Un paciente ha reservado con usted. " + patient_entry[0][0]

                # The email body for recipients with non-HTML email clients.
                BODY_TEXT = ("Estimado(a) Dra/Dr. Un paciente ha agendado una nueva cita con usted. \n\n "
                            "\rDetalles de su nueva cita:\r\n"
                            "\rPaciente: " + patient_entry[0][1] + " " + patient_entry[0][2] + " " +patient_entry[0][3] + "\n"
                             "\rFecha: " + patient_entry[0][4] + "\n"
                             "\rHorario: " + patient_entry[0][5] + "\n"
                             "\rSintomas: " + patient_entry[0][6] + "\n"
                             "\rE-Mail de paciente: " + patient_entry[0][7] + "\n\n\n"
                             "\rNOTA: Si por alguna razon no puede atender a su paciente, porfavor contacte a su correo electronico."
                            )                

                # The character encoding for the email.
                CHARSET = "UTF-8"

                # Create a new SES resource and specify a region.
                client = boto3.client('ses',aws_access_key_id = key.AccessKey,
                aws_secret_access_key=key.SecretAccessKey,
                region_name='us-east-2')

                # Try to send the email.
                try:
                    #Provide the contents of the email.
                    response = client.send_email(
                        Destination={
                            'ToAddresses': [
                                RECIPIENT,
                            ],
                        },
                        Message={
                            'Body': {
                                'Text': {
                                    'Charset': CHARSET,
                                    'Data': BODY_TEXT,
                                },
                            },
                            'Subject': {
                                'Charset': CHARSET,
                                'Data': SUBJECT,
                            },
                        },
                        Source=SENDER,
                    )
                
                # Display an error if something goes wrong.
                except ClientError as e:
                    print(e.response['Error']['Message'])
                    return False
                else:
                    print("Email sent! Message ID:"),
                    print(response['MessageId'])
                    return True
                
