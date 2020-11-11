# AWS SetUp
## Description

In this module we deploy the Amazon Web Services [AWS](https://aws.amazon.com) architecture. This cloud services use machine learning to extract text and do facial recognition.

## Installation Steps

1. Create an Amazon Web Service Account.
2. Obtain aws secret and access key.
```
Example:
Secret Key: 123adsfsaXDAFFEF#r4...
Access Key: 5423t432ewsACFASF$32rR#Cwcxasf12...

```

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
![Image of Setup](
https://github.com/MV-Automation/MV_Pandemic_Solution/blob/main/img/lambda_setup.png)

4. In configuration tab, click on add trigger and select your S3 bucket created in *S3 Bucket* setup. 
5. Setup the trigger as follows:
```
Event type: ObjectCreated
Suffix: .jpg
```
6. Once you had created the trigger, move to function code tab.
   - Click to action.
   - Upload ZIP file. (See Migration instruction [Here](https://github.com/MV-Automation/MV_Pandemic_Solution/blob/main/AWS/Lambda_Migration.md))


## Webex Teams Bot
To create a Bot please follow the next steps:
1. Open the following tutorial [Cisco Devnet](https://developer.webex.com/docs/bots))
2. Create a Bot
3. Generate Token and keep it. (*It's a unique token, take care of it*)
4. Continue migration [Here](https://github.com/MV-Automation/MV_Pandemic_Solution/blob/main/AWS/Lambda_Migration.md))


## Simple Queue Service (SQS)
1. Navigate through SQS Service tab
2. Create a new STANDARD queue
3. Use the following configuration:
	- Visibility Timeout: 30 Seconds
	- Message retention period: 1 Minute
	- Maximum message size: 256 Kb
	- Delivery delay: 0
	- Receive message wait time: 0

4. Use Basic Access Policy
5. Collect the url generated for sqs and save it.


## Architecture

This module is executed by self when receives images from a Raspberry Pi Client and then generated a Webex Teams Bot. 

![Image of Architecture](
https://github.com/MV-Automation/MV_Pandemic_Solution/blob/main/img/Cloud_Architecture.png)


