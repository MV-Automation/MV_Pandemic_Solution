# AWS Architecture
## Description

In this module we deploy the amazon web services [AWS](https://aws.amazon.com) architecture. This cloud services use machine learning to extract text and do facial recognition.

## Installation Steps

1. Create an Amazon Web Service Account.
2. Obtain aws secret and access key.
```
secret_key = 123adsfsaXDAFFEF#r4
acces_key = 5423t432ewsACFASF$32rR#Cwcxasf12

```

###### S3 Bucket

1. On service tab, open S3 service. 
2. Create a Bucket that will store client image. 
```
Bucket Name : meraki-vision-bucket-for-clients

```
	1. In our deployment we use this name but you should replace it with the name of the new bucket you will create.

###### Lambda 

1. Inside aws console, open the service tab and open Lambda.
2. Create a new lambda function. 
3. In configuration tab, click on add trigger and select your S3 bucket created in *S3 Bucket* setup. 
4. Setup the trigger as follows:
```
Event type: ObjectCreated
Suffix: .jpg
```
   1. 
   1. Item 3b




## How to use