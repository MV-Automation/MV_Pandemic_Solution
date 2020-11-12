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
import AmazonKeys as AmazonKeys


# Dynamodb resource to table
dynamodb = boto3.resource(
  'dynamodb', aws_access_key_id=AmazonKeys.aws_access,
  aws_secret_access_key=AmazonKeys.aws_secret,
  region_name='us-east-2')

# Dyano Client to select data
dynamodb_client = boto3.client('dynamodb', aws_access_key_id=AmazonKeys.aws_access,
  aws_secret_access_key=AmazonKeys.aws_secret,
  region_name='us-east-2')

# Logs site to explore data from DB.
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
                return logs(request)

            else:
                return HttpResponse("Account Not Active")
        else:
            print("Someone tried to login and failed")
            print("Username: {} and password {}".format(username,password))
            return HttpResponse("Invalid login details suplied.")
    else:
        return render(request,'my_app/login.html',{})
