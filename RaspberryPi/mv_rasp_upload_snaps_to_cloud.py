"""
Date: October 21, 2020
Author: josevagu
Description: This programs upload image to CLoud Bucket.
Bucket triggers image anaytics.
Filename ares signed with MAC address and Time.

Reference: https://aws.amazon.com/blogs/compute/uploading-to-amazon-s3-directly-from-a-web-or-mobile-application/

"""

import getmac
import datetime
import pytz
from PIL import Image
import response
import boto3
import AmazonKeys as key
from PIL import Image
import io


"""
Secuencia:

Se crea un watchdog o demonio en linux que dispar cada que se 
agrega algo a una carpeta.
https://stackoverflow.com/questions/49557421/how-to-automatically-run-python-script-when-file-is-added-to-folder/49558384


2. Se leen ambas fotos con un paso de parametros hacia el script ok

3. Se unen ambas fotos ok 

4. Se suben las 3 fotos a un bucket de S3 que detona el reconocimiento.
(La subida debe esconder las llaves, no pueden estar en la raspberry para un ambiente
de produccion)

4.1 Para hacer esto, necesitamos una api gateway que cree entradas genricas.
4.2 Luego haremos que se autentique cada raspberry y no sea subidas abruptas.
5. Verificar que se suben los archivos al bucket (ver en s3)

6. Configurar el bucket desde una lambda.

En el bot, se necesita conocer la url de la imagen unida.
Esa url se configura como jpeg (Content Type)
La url debe ser publica (abierta) para que cualquiera pueda descargar la foto.
"""


def time_prefix():
	# Reaching mac address from raspberry
	mac_client = getmac.get_mac_address()

	# Reaching Mexico Time
	time_mark = pytz.timezone('America/Mexico_City')
	#local_time = datetime.datetime.now(time_mark).strftime("%d-%b-%Y_%H:%M:%S")

	# Default file name stamp
	filename_prefix = str(mac_client)
	filename_prefix = filename_prefix.replace(":","_")
	#filename_prefix = str(mac_client) + "/" + str(local_time)

	print("LOG: MAC " + str(filename_prefix))
	return filename_prefix


def merge_images(face_img, id_img):
	
	# Get size of native images	
	face_img_size = face_img.size

	# Merge both images
	merged_img = Image.new('RGB',(2*face_img_size[0], face_img_size[1]), (250,250,250))
	merged_img.paste(face_img,(0,0))
	merged_img.paste(id_img,(face_img_size[0],0))

	print("Log: Images had been merged.")
	return merged_img


def put_in_cloud(face_snap, credential_snap, merged_snap, filename_prefix):
	#save the pillow images in memory to upload them to AWS
	face_in_mem = io.BytesIO()
	face_snap.save(face_in_mem, "PNG")
	face_in_mem.seek(0)

	id_in_mem = io.BytesIO()
	credential_snap.save(id_in_mem, "PNG")
	id_in_mem.seek(0)

	merged_in_mem = io.BytesIO()
	merged_snap.save(merged_in_mem, "JPEG")
	merged_in_mem.seek(0)

	face_name = filename_prefix + "/Face.png"
	credential_name = filename_prefix + "/Credential.png" 
	merged_name = filename_prefix + "/Merged.jpg"
	
	# trigger_name = filename_prefix +".txt"
	# sample_file = "trigger.txt"
	# print("Log: Files uploaded succesfully to cloud.")

	#Amazon Upload to S3
	s3 = boto3.client('s3',aws_access_key_id=key.aws_access, aws_secret_access_key=key.aws_secret, region_name="us-east-2")
	#bucket_name = "training-data-for-rekognition"
	bucket_name = "meraki-vision-bucket-for-clients"
	try:
		# SUBIR ALIAS DESDE LA CONFIGURACION.
		# PARA SABER NOMBRE DE CADA MAC.
		print("Log: Image Uploading...")
		s3.upload_fileobj(face_in_mem, bucket_name, face_name)
		s3.upload_fileobj(id_in_mem, bucket_name, credential_name)
		s3.upload_fileobj(merged_in_mem, bucket_name, merged_name, ExtraArgs={'ContentType':'image/jpeg', 'ACL':'public-read'})
		#s3.upload_file(sample_file, bucket_name, "hello.txt")
		print("Log: Succesfully uploaded three files to cloud.")
		return True
	
	except:
		print("Exception done!")

	else:
		print("Warning: Unable to upload to cloud.")
		return False

def main(face_img, id_img):
	# Recover time prefix
	filename_prefix = time_prefix()
	merged_img = merge_images(face_img, id_img)
	
	#Try to upload to cloud.
	status = put_in_cloud(face_img, id_img, merged_img, filename_prefix)
	return status
