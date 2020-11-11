from tkinter import Tk, Label, Button, Frame
from PIL import ImageTk, Image
import cv2
from camera import camera
import config as cfg
import mv_rasp_upload_snaps_to_cloud as awsupload
import AmazonKeys as key
import boto3


"""
Secuencia:

1. Se inicializan todos los componentes de la GUI y se añaden a la ventana de Tkinter.
2. Se crea el proceso paralelo de la cámara y se inicia el stream de rtsp.
3. Se inicia el mainloop de Tkinter para que funcione al interfaz.
4. Del frame de portada se va al frame con las instrucciones para tomar el snapshot de la cara.
    -El retraso actual del stream de RTSP es de alrededor de 2 segundos.
4. Se muestra la pantalla con el contenido del stream de RTSP y un overlay para indicar dónde colocarse.
5. Se toma el snapshot y se pasa al frame con las instrucciones para el snapshot de la identificación.
6. Se muestra la pantalla con el contenido del stream de RTSP y un overlay para indicar dónde colocar la identificación.
7. Se toma el snapshot y se pasa a un frame indicando que el resultado se está procesando.
8. Se muestra una imagen promocional mientras los resultados son calculados.
9. Se muestra el resultado al usuario.
10. La aplicación regresa al frame portada.


"""


#status flags and snapshot variables
face_snapshot = False
id_snapshot = False
face_img = None
id_img = None

#Load images for instructions
cover_img = Image.open("img/cover.jpg")
face_ins_img = Image.open("img/face_instructions.jpg")
id_ins_img = Image.open("img/id_instructions.jpg")
processing_img = Image.open("img/processing.jpg")
positive_result_img = Image.open("img/positive_result.jpg")
negative_result_img = Image.open("img/negative_result.jpg")

promo_img = Image.open(cfg.promo_img['location'])
promo_img = promo_img.resize((800,480))

#Function to initialize the rtsp stream
def init_stream():
    global cam
    cam = camera(cfg.rtsp['address'])
    face_stream()

#Raise a frame to show it
def raise_frame(frame):
    frame.tkraise()

#Function to get the rtsp stream for the face snapshot
def face_stream():
    #Get the next frame of the video
    frame = cam.get_frame(resize=None)

    #Resize the frame and draw the rectangle for where the face should go
    resize_img = cv2.resize(frame, (800,480))
    cv2.rectangle(resize_img, (200,80), (600,400), (255,255,255), 3)

    #Add the image to the Tkinter interface
    img = Image.fromarray(resize_img)
    imgtk = ImageTk.PhotoImage(img)
    global bface
    bface.imgtk = imgtk
    bface.configure(image=imgtk)
    
    #Repeat the process after 30ms in order to achieve a video of around ~30 FPS
    faceloop = window.after(30, face_stream)
    if face_snapshot == True:
        global face_img
        face_img = Image.fromarray(frame)
        window.after_cancel(faceloop) 
        bface.configure(image='')


#Function to get the rtsp stream for the id snapshot
def id_stream():
    #Get the next frame of the video
    frame = cam.get_frame(resize=None)

    #Resize the frame and draw the rectangle for where the id should go
    resize_img = cv2.resize(frame, (800,480))
    cv2.rectangle(resize_img, (150,120), (650,360), (255,0,0), 3)
    
    #Add the image to the Tkinter interface
    img = Image.fromarray(resize_img)
    imgtk = ImageTk.PhotoImage(image=img)
    
    global bid
    bid.imgtk = imgtk
    bid.configure(image=imgtk)
    
    #Repeat the process after 30ms in order to achieve a video of around ~30 FPS
    idloop = window.after(30, id_stream)
    if id_snapshot == True:
        global id_img
        id_img = Image.fromarray(frame)
        window.after_cancel(idloop) 
        bid.configure(image='')
        print("Images are ready")
        upload_images()
    
#Upload the images to AWS, raise the frame with the promo image and open the sqs notification function
def upload_images():
    print("Uploading images")
    
    cv2.destroyAllWindows()
    awsupload.main(face_img, id_img)
    
    window.after(1000, change_promo, promo_img)

    try:
        window.after(15000, sqs_notif)
        
        global cam
        cam.end()
        cam = None
        

    except:
        print("No message in the queue")

#SQS notifications, raising the results frame and redirecting to the application cover frame
def sqs_notif():        
    global face_snapshot
    global id_snapshot
    global face_img
    global id_img
    face_snapshot = False
    id_snapshot = False
    face_img = None
    id_img = None

    init_stream()    

    # Create SQS client
    sqs = boto3.client('sqs', aws_access_key_id=key.aws_access, aws_secret_access_key=key.aws_secret, region_name="us-east-2")
    queue_url = 'https://sqs.us-east-2.amazonaws.com/727103842412/MyQueueTest'

    # Receive message from SQS queue
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )

    if 'Messages' not in response:
        print("No hay mensaje")
        raise_frame(negative_results_frame)
        window.after(10000, raise_frame, cover_frame)
        
    else:
        message = response['Messages'][0]
        print("LOG: Hay mensaje.")
        body = message['Body']
        receipt_handle = message['ReceiptHandle']
        print('Mensaje desde lambda: %s' % body)

        if body == 'Allowed':
            raise_frame(positive_results_frame)

        else:
            print('not allowed')
            raise_frame(negative_results_frame)
            
        window.after(10000, raise_frame, cover_frame)

        # Delete received message from queue
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )

#Change the promo image
def change_promo(promo_img):
    global bpromo
    promo_img = ImageTk.PhotoImage(image=promo_img)
    bpromo.img = promo_img
    bpromo.configure(image=promo_img)
    bpromo.grid(sticky='news')
    raise_frame(promo_frame)

#Switch to the id snapshot instructions frame
def switch_to_id_ins():
    global face_snapshot
    id_stream()
    face_snapshot = True
    raise_frame(id_ins_frame)

#Switch to the face snapshot instructions fame
def switch_to_face_ins():
    raise_frame(face_ins_frame)

#Switch to the id snapshot frame
def switch_to_id():
    raise_frame(id_frame)

#Switch to the face snapshot frame
def switch_to_face():
    raise_frame(face_frame)

#Switch to the processing results frame
def switch_to_processing():
    global id_snapshot
    id_snapshot = True
    raise_frame(processing_frame)

    
#Create the root component, named window and its attributes
window = Tk()
window.geometry("800x480")
window.attributes('-fullscreen', True) #alt + F4 allows you to exit the fullscreen app

# Create the initial instructions frame and button 
cover_frame = Frame(window, bg="white")
bcover = Button(cover_frame, command=switch_to_face_ins)
cover_img = ImageTk.PhotoImage(image=cover_img)
bcover.img = cover_img
bcover.configure(image=cover_img)
bcover.grid(sticky='news')

# Create the face snapshot instructions frame and button 
face_ins_frame = Frame(window, bg="white")
bface_ins = Button(face_ins_frame, command=switch_to_face)
face_ins_img = ImageTk.PhotoImage(image=face_ins_img)
bface_ins.img = face_ins_img
bface_ins.configure(image=face_ins_img)
bface_ins.grid(sticky='news')

# Create the id snapshot instructions frame and button 
id_ins_frame = Frame(window, bg="white")
bid_ins = Button(id_ins_frame, command=switch_to_id)
id_ins_img = ImageTk.PhotoImage(image=id_ins_img)
bid_ins.img = id_ins_img
bid_ins.configure(image=id_ins_img)
bid_ins.grid(sticky='news')

# Create a frame and button for the face snapshot
face_frame = Frame(window, bg="white")
bface = Button(face_frame, command=switch_to_id_ins)
bface.grid(sticky='news')

# Create a frame and button for the id snapshot
id_frame = Frame(window, bg="white")
bid = Button(id_frame, command=switch_to_processing)
bid.grid(sticky='news')

# Create a frame and button for the processing results screen
processing_frame = Frame(window, bg="white")
bprocessing = Button(processing_frame)
processing_img = ImageTk.PhotoImage(image=processing_img)
bprocessing.img = processing_img
bprocessing.configure(image=processing_img)
bprocessing.grid(sticky='news')

# Create a frame and button for the positive results screen
positive_results_frame = Frame(window, bg="white")
bresults = Button(positive_results_frame)
positive_result_img = ImageTk.PhotoImage(image=positive_result_img)
bresults.img = positive_result_img
bresults.configure(image=positive_result_img)
bresults.grid(sticky='news')

# Create a frame and button for the negative results screen
negative_results_frame = Frame(window, bg="white")
bnegresults = Button(negative_results_frame)
negative_result_img = ImageTk.PhotoImage(image=negative_result_img)
bnegresults.img = negative_result_img
bnegresults.configure(image=negative_result_img)
bnegresults.grid(sticky='news')

# Create a frame and button for the promo screen
promo_frame = Frame(window, bg="white")
bpromo = Label(promo_frame)

#Add the frames to the grid
for frame in (cover_frame, face_frame, id_frame, face_ins_frame, id_ins_frame, processing_frame, positive_results_frame, negative_results_frame, promo_frame):
    frame.grid(row=0, column=0, sticky='news')


if __name__ == "__main__":
    #Raise the cover frame so we start with the cover
    raise_frame(cover_frame)

    # initialize the cam object
    cam = None

    init_stream()

    window.mainloop()

    cam.end()
    cv2.destroyAllWindows()