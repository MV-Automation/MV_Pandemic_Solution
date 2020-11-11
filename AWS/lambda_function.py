"""
AWS RUNNING

"""

"""
Name: Webex_Logs_and_MV_Access.py
Authors: DavidJM3195 & vicente-aguilar
Date: October 16, 2020
Last version: Nov 11 2020
Description: This code takes two images from an S3 bucket, make a comparison between the two faces, uploads the 
text and allows access if the similarity is higher than 80%. All this information is sent to a Webex Bot and then
using a SQS service send the message to the raspberry with the 'Access' variable.

"""
import time
from pytz import timezone
from datetime import datetime
from datetime import date
import boto3
import json
import pandas as pd
import requests
import AmazonKeys as key

def mensajeWebex(data_list, bot_file):

    url_webex = "https://webexapis.com/v1/messages"
    data_list = data_list
    mails_to_send = ["mail1@cisco.com", "mail2@cisco.com", "mail3@cisco.com"]

    if str(data_list[1]) == 'Allowed':
      access='Permitido'
    elif str(data_list[1]) == 'Denied':
      access='Denegado'

    markdown_message = "Nombre: " + str(data_list[0])  + "\n Clave de Elector: " + str(data_list[4]) + "\n Similitud: " + str(data_list[2]) + "%" + "\n Acceso: " + access + "\n Edad: " + str(data_list[3])
    print(markdown_message)
    bot_bucket = "your_new_bucket"
    #bot_file = "Merged.jpg"

    for user_mail in mails_to_send:

      payload = {"toPersonEmail": user_mail, "markdown": markdown_message, "files": "https://" + bot_bucket +".s3.us-east-2.amazonaws.com/"+bot_file}
      headers = {
      'Authorization': 'Bearer '+key.bot_token,
      'Content-Type': 'application/json'
      }

      response = requests.request("POST", url_webex, headers=headers, json = payload)

def mensajeWebex_Error():

    url_webex = "https://webexapis.com/v1/messages"
    mails_to_send = ["mail1@cisco.com", "mail2@cisco.com", "mail3@cisco.com"]

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
    bucket='your_new_bucket'
    access_granted=[]
    access_denied=[]
    queue_url = 'sqs_url'

    sqs = boto3.client('sqs', aws_access_key_id=key.aws_access, aws_secret_access_key=key.aws_secret, region_name="us-east-2")
    client=boto3.client('rekognition', aws_access_key_id=key.aws_access, aws_secret_access_key=key.aws_secret,region_name="us-east-2")
    client_textract=boto3.client('textract', aws_access_key_id=key.aws_access, aws_secret_access_key=key.aws_secret ,region_name="us-east-2")
    dynamodb=boto3.resource('dynamodb', aws_access_key_id=key.aws_access, aws_secret_access_key=key.aws_secret, region_name="us-east-2")
    
        # Detecta si hay cara o no.
    try:
      response=client.compare_faces(SimilarityThreshold=80, SourceImage={'S3Object':{'Bucket':bucket,'Name':sourceFile}}, TargetImage={'S3Object':{'Bucket':bucket,'Name':targetFile}})
    except Exception as e:
      print("ERROR: No faces detected.")
      print(e)
      response = "No faces"

    response_textract = client_textract.analyze_document(Document={'S3Object': {'Bucket': bucket, 'Name': targetFile}}, FeatureTypes=["TABLES", "FORMS"])
    table=dynamodb.Table("your_new_dynamodDB")


    now = datetime.now() # current date and time
    now_mexico=now.astimezone(timezone('America/Mexico_City'))
    current_time= now_mexico.strftime("%d/%m/%Y %H:%M:%S")

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

        counter = counter + 1
        text_words.append(block['Text'])

    # Cleaning data to extract the name
    # Creating pandas Dataframes
    text_df = pd.DataFrame (text_words,columns=['text_on_id'])

    # Recovering type of id
    type_of_id = text_df['text_on_id'][0]
    # Casting to capital letters
    text_df['text_on_id'] = text_df['text_on_id'].str.upper()

    # Date validation
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
      for row in text_df['text_on_id']:

        if index_of_end_name == "Null" or index_of_init_name == "Null":
          print("Log: No name Avaliable")
          print("ERROR: CANT FIND NAME WITH INDEX.")
          name_of_id = "Not Avaliable"
          break
      
        if index > index_of_init_name and index < index_of_end_name:
          if index != index_of_birthday:
            if "FECHA" in row:
              print("Warn: Date is present.")  
            elif "SEX" in row:
              print("Warn: Gender is present.")
            else:
              name_of_id = name_of_id + " " + row
        index = index +1

      if name_of_id != 'Not Avaliable': print("Log: Name founded at credential.")

    except Exception as e:
      print(e)
      print("Exception: NO NAME DETECTED.")
      name_of_id = "Not Avaliable"

    #Finding word using regex
    clave_index = text_df['text_on_id'].str.contains('CLAVE DE ELE', regex=True)

    if not clave_index.any():
      print("No elector key Avaliable.")
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
        confidence = str(faceMatch['Face']['Confidence'])
        similarity = str (faceMatch['Similarity'])
        if k < 1:
          print('The similarity between the faces is '+ similarity +' with '+ confidence + '% of confidence.')
          access_granted.append((current_time, name, date, access, similarity, elector_key))
        k = k + 1

      print("Cargando a Dynamodb...")
      print(table.table_status)

      for item in access_granted:
        response_sqs = sqs.send_message(QueueUrl=queue_url,MessageBody=(str(access))) 
        less_decimal = "{:.2f}".format(float(item[4]))
        table.put_item(Item={'Time':item[0], 'Name': item[1], 'Age': item[2], 'Access':item[3], 'Similarity': less_decimal, 'Elector Key': item[5] , 'Location': carpeta})
        list_to_bot = [item[1], item[3], less_decimal, age, elector_key]
        mensajeWebex(list_to_bot, mergeFile)

      if response['FaceMatches'] == []:  
        k = 0
        for notfaceMatch in response['UnmatchedFaces']:

          name = person_name
          date = age
          access = 'Denied'
          similarity = '< 80% '
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


