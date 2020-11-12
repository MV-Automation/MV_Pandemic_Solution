# Web Application
## Description
In this module we deploy the Web Applicaton  that allows users to monitor access logs of this solution. Users are created just in admin panel. 

## Installation Steps
For this Web App deployment you will need to use your Amazon Web Services Account  previously created. 

###### Virtual Machine in AWS (EC2)
1. Open your AWS Console [AWS](https://aws.amazon.com) and choose EC2 Service. 
2. Launch a new instance and select the following *free tier* version:
``` bash
Ubuntu Server 20.04 LTS (HVM), SSD Volume Type - ami-0a91cd140a1fc148a (64-bit x86) / ami-0742a572c2ce45ebf (64-bit Arm)
```
3. Downloadd and safetly save the '.PEM' file that will create SSH conecction to this new instance.

> You could add a security group to allow access from specific IP addreses only.

4. Create a connection with a terminal emulator (ie. Putty, Secure CRT) using the downloaded key-pair (.PEM)

``` bash
ssh -i "key_pair_name.pem" ubuntu@ec2-XX-XX-XX-XX.us-west-2.compute.amazonaws.com
```


###### Install Python
1. Please install the following packages from cli.

``` bash
sudo apt-get update
sudo apt-get install python3-pip apache2 libapache2-mod-wsgi-py3
```

###### Create a virtual enviroment 
1. Install virtualenv using the following command.
``` bash
sudo pip3 install virtualenv
```
2. Create a new folder called django as follows:
``` bash
mdkir django
cd django
```

3. Create an virtual enviroment in django folder and clone the web app project. 
``` bash
virtualenv mv_env
git clone "https://github.com/MV-Automation/MV_Pandemic_Solution/" 
```
4. Activate the virtual enviroment:
``` bash
source mv_env/bin/activate
```

## Django Deployment Server

###### Deploy in EC2
1. Once you had cloned the project repository, navigate to project folder and open settings.py
``` bash
cd Meraki_Project/mysite/mysite

sudo vi Meraki_Project/mysite/mysite/settings.py
```
2. Replace the allowed host with your EC2 instance name.
``` bash
ALLOWED_HOSTS = ['Your_EC2_DNS_NAME']
```
3. Install the project requirements.
``` bash
pip install -r requirements.txt
```
4. Install django.
``` bash
pip install django
```
5. Migrate the django project into EC2 instance with the following commands:
``` bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
```
> Just to verify you had correct install all the package, you could run the following command and open in a web browser, port 8000 .Example: www.your_ec2_dns_name.com:8000
``` bash
python manage.py runserver 0.0.0.0:8000
```


###### Deploy in Apache Server



> Please verify versions of library used in this project before install. 