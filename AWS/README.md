# AWS Architecture
## Description

In this module we deploy the amazon web services [AWS](https://aws.amazon.com) architecture. This cloud services use machine learning to extract text and do facial recognition.

## Installation Steps

1. Create an Amazon Web Service Account.
2. Obtain aws secret and access key.
```
Example:
secret_key = 123adsfsaXDAFFEF#r4...
acces_key = 5423t432ewsACFASF$32rR#Cwcxasf12...

```
3. Replace you AWS keys in the file AmazonKeys.py and save.

###### S3 Bucket

1. On service tab, open S3 service. 
2. Create a Bucket that will store client image. 
```
Bucket Name : meraki-vision-bucket-for-clients
```
> In our deployment we use this name but you should replace it with the name of the new bucket you will create.




###### Lambda 

1. Inside aws console, open the service tab and open Lambda.
2. Create a new lambda function from scratch with *Python 3.6* as Runtime.
3. Modify lambda settings to the following:
![Image of Yaktocat](
https://github.com/MV-Automation/MV_Pandemic_Solution/blob/main/AWS/img/lambda_setup.png)

4. In configuration tab, click on add trigger and select your S3 bucket created in *S3 Bucket* setup. 
5. Setup the trigger as follows:
```
Event type: ObjectCreated
Suffix: .jpg
```
6. Once you had created the trigger, move to function code tab.
   - Click to action.
   - Upload ZIP file. (See Migration instructtion [Here](https://github.com/MV-Automation/MV_Pandemic_Solution/blob/main/AWS/Lambda_Migration.md))



## How to use