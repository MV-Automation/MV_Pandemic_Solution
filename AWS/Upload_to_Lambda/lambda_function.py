"""
AWS RUNNING

"""

"""
Name: Webex_Logs_and_MV_Access.py
Authors: davijime & josevagu
Date: October 16, 2020
version 4: 04 January 2021
Description: This code takes two images from an S3 bucket, make a comparison between the two faces, uploads the 
text and allows access if the similarity is higher than 80%. All this information is sent to a Webex Bot and then
using a SQS service send the message to the raspberry with the 'Access' variable.

"""
import time
import botocore
from pytz import timezone
from datetime import datetime
from datetime import date
from botocore.exceptions import ClientError
import boto3
import json
import pandas as pd
import requests
import AmazonKeys as key

def get_visit_info():
    dynamodb=boto3.resource('dynamodb', aws_access_key_id=key.aws_access, aws_secret_access_key=key.aws_secret, region_name="us-east-2")
    dynamodb_client = boto3.client('dynamodb', aws_access_key_id=key.aws_access, aws_secret_access_key=key.aws_secret, region_name="us-east-2")
    try:
      table_doctors = dynamodb.Table('Doctors_Agenda')
    except botocore.exceptions.ClientError as e:
      # http://stackoverflow.com/questions/33068055/boto3-python-and-how-to-handle-errors
      return 'failed'
    else:
      response = dynamodb_client.scan(TableName='Doctors_Agenda')
      if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        try:
          item = response['Items']
        except KeyError:
          return None
        return item


def show_same_day(item, fecha):
    filtered_dates = []
    for i in item:
        if i['Date']['S'] == fecha:
            filtered_dates.append(i)
            print(i)
    return filtered_dates


def filter_by_hour_range(filtered_dates, hora):

    [hour, minute] = hora.split(':')
    actual_hour = int(hour)

    min_range = actual_hour-1
    max_range = actual_hour+1

    filter_again = []

    for i in filtered_dates:
        item_time = i['Time']['S']
        [hour, minute] = item_time.split(':')
        hour = int(hour)
        minute = int(minute)

        if hour >= min_range and hour <= max_range:
            filter_again.append(i)

    return filter_again

def find_match_surname_and_get_email (nombre_detectado, primer_apellido, filter_again):
    for i in filter_again:
      f_surname=i['First_Surname']['S']
      f_surname= f_surname.upper()
      f_surname_len=len(f_surname)
      if f_surname_len > 3:
        if primer_apellido.startswith(f_surname[:(f_surname_len-1)]):
            name=i['Name']['S']
            name=name.upper()
            name_len=len(name)
            if nombre_detectado.startswith(name[:(name_len-1)]):
                username= i['User']['S']
                return username
      else:
        if primer_apellido == f_surname:
            name=i['Name']['S']
            name=name.upper()
            print(name)
            name_len=len(name)
            if nombre_detectado.startswith(name[:(name_len-1)]):
                username= i['User']['S']
                return username

def notification_email(doctor_email, person_name):

    SENDER = "Mr. Smith <davijime@cisco.com>"

    # Replace recipient@example.com with a "To" address. If your account 
    # is still in the sandbox, this address must be verified.
    RECIPIENT = doctor_email

    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the 
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    #CONFIGURATION_SET = "ConfigSet"

    # The subject line for the email.
    SUBJECT = "Your pacient has arrived!"

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = ("Notification Email from Meraki Vision\r\n"
                 "Dear doctor: \n\n"
                 "We have identified that your pacient " + person_name + " has arrived. Please, welcome him/her.\n\n"
                 "Message from Meraki Vision\n\n"
                 "This is an automated message, please don't respond to this email.\n"
                )
                
    # The HTML body of the email.
    '''
    BODY_HTML = """<html>
    <head></head>
    <body>
      <h1>Message sent from Meraki Vision</h1>
      <p>Your pacient has arrived!</p>
    </body>
    </html>
                """'''            

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses',aws_access_key_id=key.aws_access, aws_secret_access_key=key.aws_secret, region_name="us-east-2")

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
            # If you are not using a configuration set, comment or delete the
            # following line
            #ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong. 
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])

def mensajeWebex(data_list, bot_file):

    url_webex = "https://webexapis.com/v1/messages"
    data_list = data_list
    mails_to_send = ["davijime@cisco.com", "josevagu@cisco.com", "anarrode@cisco.com"]

    if str(data_list[1]) == 'Allowed':
      access='Permitido'
    elif str(data_list[1]) == 'Denied':
      access='Denegado'

    markdown_message = "Nombre: " + str(data_list[0])  + "\n Clave de Elector: " + str(data_list[4]) + "\n Similitud: " + str(data_list[2]) + "%" + "\n Acceso: " + access + "\n Edad: " + str(data_list[3])
    print(markdown_message)
    bot_bucket = "meraki-vision-bucket-for-clients"
    #bot_file = "00%3A05%3A9a%3A3c%3A7a%3A00/Merged.jpg"

    for user_mail in mails_to_send:

      payload = {"toPersonEmail": user_mail, "markdown": markdown_message, "files": "https://" + bot_bucket +".s3.us-east-2.amazonaws.com/"+bot_file}
      headers = {
      'Authorization': 'Bearer '+key.bot_token,
      'Content-Type': 'application/json'
      }

      response = requests.request("POST", url_webex, headers=headers, json = payload)

def mensajeWebex_Error():

    url_webex = "https://webexapis.com/v1/messages"
    mails_to_send = ["davijime@cisco.com", "josevagu@cisco.com", "anarrode@cisco.com"]

    for user_mail in mails_to_send:

      payload = {"toPersonEmail": user_mail, "text": "Aviso: Alguien intenta entrar pero algo no ha salido bien en el proceso."}
      headers = {
      'Authorization': 'Bearer '+key.bot_token,
      'Content-Type': 'application/json'
      }

      response = requests.request("POST", url_webex, headers=headers, json = payload)

def lambda_handler(event, context):

    # Replace sourceFile and targetFile with the image files you want to compare.
    
    registros = event['Records']
    archivo = registros[0]['s3']['object']['key']
    carpeta = archivo.split("/")[0]
    print("MV Log: Nombre de archivo. ")
    print(archivo)
    print("MV Log: Carpeta de archivo.")
    print(carpeta)
    
    sourceFile= carpeta + '/Face.png'
    targetFile= carpeta + '/Credential.png'
    mergeFile = archivo
    """
    carpeta='123'
    sourceFile='Face.png'
    targetFile='Credential.png'
    #targetFile = 'ID_Sin_Nombre.png'
    mergeFile = 'Merged.jpg'
    """
    bucket='meraki-vision-bucket-for-clients'
    access_granted=[]
    access_denied=[]
    queue_url = 'https://sqs.us-east-2.amazonaws.com/727103842412/MyQueueTest'

    sqs = boto3.client('sqs', aws_access_key_id=key.aws_access, aws_secret_access_key=key.aws_secret, region_name="us-east-2")
    client=boto3.client('rekognition', aws_access_key_id=key.aws_access, aws_secret_access_key=key.aws_secret,region_name="us-east-2")
    client_textract=boto3.client('textract', aws_access_key_id=key.aws_access, aws_secret_access_key=key.aws_secret ,region_name="us-east-2")
    dynamodb=boto3.resource('dynamodb', aws_access_key_id=key.aws_access, aws_secret_access_key=key.aws_secret, region_name="us-east-2")
    dynamodb_client = boto3.client('dynamodb', aws_access_key_id=key.aws_access, aws_secret_access_key=key.aws_secret, region_name="us-east-2")
        # Detecta si hay cara o no.
    try:
      response=client.compare_faces(SimilarityThreshold=80, SourceImage={'S3Object':{'Bucket':bucket,'Name':sourceFile}}, TargetImage={'S3Object':{'Bucket':bucket,'Name':targetFile}})
    except Exception as e:
      print("ERROR: No faces detected.")
      print(e)
      response = "No faces"
      # Sending error messages to rasp. "ERROR"
      #response_sqs = sqs.send_message(QueueUrl=queue_url,MessageBody=('Face_Error'))

    response_textract = client_textract.analyze_document(Document={'S3Object': {'Bucket': bucket, 'Name': targetFile}}, FeatureTypes=["TABLES", "FORMS"])
    table=dynamodb.Table("Faces_Match")
    table_doctors= dynamodb.Table("Doctors_Agenda")


    now = datetime.now() # current date and time
    now_mexico=now.astimezone(timezone('America/Mexico_City'))
    current_time= now_mexico.strftime("%Y-%m-%d %H:%M")
    [fecha,hora]=current_time.split(" ")
    #print("Current Time:", current_time)

    #print("============================================================")
    bloques = response_textract['Blocks']

    # Extracting lenght of lines
    length_of_lines = len(bloques[0]['Relationships'][0]['Ids'])
    counter = 0
    text_words = []

    # Extracting words from json response
    for block in bloques:
      # Just show me the first results.
      if counter > length_of_lines:
        break
      # Show me just the text recognized
      if 'Text' in block:

        # Show words in console
        #print(block['Text'])
        
        counter = counter + 1
        text_words.append(block['Text'])
        #print('    Type: ' + block['BlockType'])
        #print('Id: {}'.format(block['Id']))

    # Cleaning data to extract the name
    # Creating pandas Dataframes
    text_df = pd.DataFrame (text_words,columns=['text_on_id'])
    #print (text_df)

    # pd.Series(text_words)
    # Recovering type of id
    type_of_id = text_df['text_on_id'][0]
    # Casting to capital letters
    text_df['text_on_id'] = text_df['text_on_id'].str.upper()

    # Date validation
    #text_df['text_on_id'].str.contains('^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$', regex=True)
    birthday = text_df['text_on_id'].str.contains('(^(((0[1-9]|1[0-9]|2[0-8])[\/](0[1-9]|1[012]))|((29|30|31)[\/](0[13578]|1[02]))|((29|30)[\/](0[4,6,9]|11)))[\/](19|[2-9][0-9])\d\d$)|(^29[\/]02[\/](19|[2-9][0-9])(00|04|08|12|16|20|24|28|32|36|40|44|48|52|56|60|64|68|72|76|80|84|88|92|96)$)', regex=True)

    if not birthday.any():
      print("No birthday Avaliable.")
      birthday_text = "Not Avaliable"
      index_of_birthday = 0
      age = "Not Avaliable"

    else:
      index_of_birthday = int(birthday.index[birthday].tolist()[0])
      birthday_text = text_df['text_on_id'][index_of_birthday]
      
      splited_date = birthday_text.split("/")
      year_id = int(splited_date[2])
      month_id = int(splited_date[1])
      day_id = int(splited_date[0])

      today = datetime.today() 
      age = today.year - year_id - ((today.month, today.day) < (month_id, day_id))     

    try:
      init_of_name = text_df['text_on_id'].str.contains('NOM', regex=True)
      end_of_name = text_df['text_on_id'].str.contains('DOMICIL', regex=True)   
      
      if not init_of_name.any():
        index_of_init_name = 'Null'      
      else:
        index_of_init_name = int(init_of_name.index[init_of_name].tolist()[0])
      
      if not end_of_name.any():
        index_of_end_name = 'Null'
      else:
        index_of_end_name = int(end_of_name.index[end_of_name].tolist()[0])

      index = 0
      name_of_id = ""
      names_founded = []

      for row in text_df['text_on_id']:

        if index_of_end_name == "Null" or index_of_init_name == "Null":
          print("Log: No name Avaliable")
          print("ERROR: CANT FIND NAME WITH INDEX.")
          #response_sqs = sqs.send_message(QueueUrl=queue_url,MessageBody=('Name_Error'))
          name_of_id = "Not Avaliable"
          break
      
        if index > index_of_init_name and index < index_of_end_name:
          if index != index_of_birthday:
            if "FECHA" in row:
              print("Warn: Date is present.")  
            elif "SEX" in row:
              print("Warn: Gender is present.")
            else:
              names_founded.append(str(row))
              name_of_id = name_of_id + " " + row
        index = index +1

      primer_apellido=names_founded[0]
      nombre_detectado=names_founded[2]

      if name_of_id != 'Not Avaliable': print("Log: Name founded at credential.")

    except Exception as e:
      print(e)
      print("Exception: NO NAME DETECTED.")
      name_of_id = "Not Avaliable"
      # Sending error messages to rasp. "ERROR"
      #response_sqs = sqs.send_message(QueueUrl=queue_url,MessageBody=('Name_Error'))

    #Finding word using regex
    clave_index = text_df['text_on_id'].str.contains('CLAVE DE ELE', regex=True)

    if not clave_index.any():
      print("No elector key Avaliable.")
      # index_of_birthday = 0
      elector_key = "Not Avaliable"
    else:
      index_of_elector = int(clave_index.index[clave_index].tolist()[0])  
      elector_key = text_df['text_on_id'][index_of_elector]
      elector_key = elector_key.split(" ")[3]


    person_name = name_of_id
    Born_Date = age

    if name_of_id != 'Not Avaliable' and response != "No faces":

      k=0
      for faceMatch in response['FaceMatches']:

        name = person_name
        date = age
        access = 'Allowed'
        #position = faceMatch['Face']['BoundingBox']
        confidence = str(faceMatch['Face']['Confidence'])
        similarity = str (faceMatch['Similarity'])
        if k < 1:
          print('The similarity between the faces is '+ similarity +' with '+ confidence + '% of confidence.')
          access_granted.append((current_time, name, date, access, similarity, elector_key))
        k = k + 1

      #print('-----------------------------------------------------------------------------------------------------------------------------------------------------')
      print("Cargando a Dynamodb...")
      print(table.table_status)

      for item in access_granted:
        response_sqs = sqs.send_message(QueueUrl=queue_url,MessageBody=(str(access))) 
        less_decimal = "{:.2f}".format(float(item[4]))
        table.put_item(Item={'Time':item[0], 'Name': item[1], 'Age': item[2], 'Access':item[3], 'Similarity': less_decimal, 'Elector Key': item[5] , 'Location': carpeta})
        #print(item)
        list_to_bot = [item[1], item[3], less_decimal, age, elector_key]
        #breakpoint()
        mensajeWebex(list_to_bot, mergeFile)

      # Here we made a comparison algrorithm to match schedule clients and the personas who has phsyical arrived. 
      consulta_dynamo= get_visit_info()
      filter_by_date= show_same_day(consulta_dynamo,fecha)
      print(filter_by_date)

      filter_by_hour= filter_by_hour_range(filter_by_date,hora)
      print(filter_by_hour)
      
      doctor_email= find_match_surname_and_get_email(nombre_detectado, primer_apellido, filter_by_hour)
      
      print(doctor_email)
      # This function notificate via email to doctor when a pacient has arrived to physical instalations.

      notification_email(doctor_email, person_name)
              
      if response['FaceMatches'] == []:  
        k = 0
        for notfaceMatch in response['UnmatchedFaces']:

          name = person_name
          date = age
          access = 'Denied'
          similarity = '< 80% '
          #similarity = str (faceMatch['Similarity'])
          confidence = str(notfaceMatch['Confidence'])
          if k < 1:
            print("You don't have access, the detected faces has a similarity lower than 80% with a confidence of "+ confidence)
            access_denied.append((current_time, name, date, access, similarity, elector_key))
          k = k + 1

      for item in access_denied:
        response_sqs = sqs.send_message(QueueUrl=queue_url,MessageBody=(str(access)))
        table.put_item(Item={'Time':item[0], 'Name': item[1], 'Age': item[2], 'Access':item[3], 'Similarity': similarity, 'Elector Key': item[5], 'Location': carpeta })
        list_to_bot = [item[1], item[3], similarity, age, elector_key]
        mensajeWebex(list_to_bot, mergeFile)

    else:
      print("ERROR: EXECUTION ABORTED.")
      response_sqs = sqs.send_message(QueueUrl=queue_url,MessageBody=('Error'))
      mensajeWebex_Error()



