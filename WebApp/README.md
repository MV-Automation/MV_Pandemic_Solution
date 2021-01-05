# Web Application
## Description
In this module we deploy the Web Applicaton  that allows users to monitor access logs of this solution. Users are created just in admin panel. 

## Installation Steps
For this Web App deployment you will need to use your Amazon Web Services Account  previously created. 

###### Virtual Machine in AWS (EC2)
1. Open your AWS Console [AWS](https://aws.amazon.com) and choose EC2 Service. 
2. Launch a new instance and select the following *free tier* version:

	
``` bash
IMPORTANT: If you can't create an instance in your actual region (example: Ohio us-east-2), try to create an EC2 instance in another region of Amazon Web Services (example: Oregon us-west-2) 
```

2.1 Choose the following image and select the default values as follows.

``` bash
Ubuntu Server 20.04 LTS (HVM), SSD Volume Type - ami-0a91cd140a1fc148a (64-bit x86) / ami-0742a572c2ce45ebf (64-bit Arm)
```

![Image of Web App](
https://github.com/MV-Automation/MV_Pandemic_Solution/blob/main/img/web_01.PNG)

![Image of Web App](
https://github.com/MV-Automation/MV_Pandemic_Solution/blob/main/img/web_02.PNG)

![Image of Web App](
https://github.com/MV-Automation/MV_Pandemic_Solution/blob/main/img/web_03.PNG)

![Image of Web App](
https://github.com/MV-Automation/MV_Pandemic_Solution/blob/main/img/web_04.PNG)

![Image of Web App](
https://github.com/MV-Automation/MV_Pandemic_Solution/blob/main/img/web_05.PNG)

![Image of Web App](
https://github.com/MV-Automation/MV_Pandemic_Solution/blob/main/img/web_06.PNG)

![Image of Web App](
https://github.com/MV-Automation/MV_Pandemic_Solution/blob/main/img/web_07.PNG)


3. Downloadd and safetly save the '.PEM' file that will create SSH conecction to this new instance.

![Image of Web App](
https://github.com/MV-Automation/MV_Pandemic_Solution/blob/main/img/web_08.PNG)

> You could add a security group to allow access from specific IP addreses only.

4. Verify that your instance has been launched and is online.

![Image of Web App](
https://github.com/MV-Automation/MV_Pandemic_Solution/blob/main/img/web_09.PNG)

5. Create a connection with a terminal emulator (ie. Putty, Secure CRT) using the downloaded key-pair (.PEM)

5.1 Click on you instance ID and this will show you the Instance Summary, then click on the Connect button.

![Image of Web App](
https://github.com/MV-Automation/MV_Pandemic_Solution/blob/main/img/web_010.PNG)

5.2 Finally, move into SSH client tab and find the command to connect into the EC2 instance. 

![Image of Web App](
https://github.com/MV-Automation/MV_Pandemic_Solution/blob/main/img/web_011.PNG)

5.3 Use Windows CMD or your prefered terminal emulator to connect to the instance. 

Make sure that the PEM file is in the same folder from wich you try to make the conection with SSH client. 

``` bash
Example: 
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
mkdir django
cd django
```

3. Create an virtual enviroment in django folder and clone the web app project. 
``` bash
virtualenv mv_env
git clone "https://github.com/MV-Automation/MV_Pandemic_Solution/" 
```
4. Add your AmazonKeys.py file to the project using the following path:

``` bash
mv AmazonKeys.py django/Meraki_Project/mysite/my_app/AmazonKeys.py
```

5. Activate the virtual enviroment:
``` bash
source mv_env/bin/activate
```

## Django Deployment Server

###### Deploy in EC2
1. Once you had cloned the project repository, navigate to project folder and open settings.py
``` bash

cd MV_P-Extention/Meraki_Project-Extension/mysite/mysite

sudo vi MV_P-Extention/Meraki_Project-Extension/mysite/mysite/settings.py
```
2. Replace the allowed host with your EC2 instance name.
``` bash
ALLOWED_HOSTS = ['YOUR_EC2_DNS_NAME']
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
## Add the following inbound rule for the security group that use the instance in Amazon Web Services for port TCP 80 and TCP 8000.

![Image of Web App](
https://github.com/MV-Automation/MV_Pandemic_Solution/blob/main/img/web_012.PNG)

![Image of Web App](
https://github.com/MV-Automation/MV_Pandemic_Solution/blob/main/img/web_013.PNG)



> Please verify versions of library used in this project before install. 

###### Deploy in Apache Server

After you had installed django and deployed in EC2 instance its time to mount as a linux process to run in background. 

First, desactivate the virtual enviroment and return to root folder with this command. 
``` bash
desactivate
cd ~
```

1. Open the *000-default.conf* file in your EC2 instance. 
``` bash
sudo vi /etc/apache2/sites-available/000-default.conf
```

2. Replace the file configuration as follows:

``` bash
<VirtualHost *:80>

ServerAdmin webmaster@example.com
DocumentRoot /home/ubuntu/django/MV_P-Extention/Meraki_Project-Extension/mysite
ErrorLog ${APACHE_LOG_DIR}/error.log
CustomLog ${APACHE_LOG_DIR}/access.log combined
Alias /static /home/ubuntu/django/MV_P-Extention/Meraki_Project-Extension/mysite/static
<Directory /home/ubuntu/django/MV_P-Extention/Meraki_Project-Extension/mysite/static>
Require all granted
</Directory>

<Directory /home/ubuntu/django/MV_P-Extention/Meraki_Project-Extension/mysite/mysite>
<Files wsgi.py>
Require all granted
</Files>
</Directory>

WSGIDaemonProcess MV_P-Extention python-path=/home/ubuntu/django/MV_P-Extention/Meraki_Project-Extension/mysite python-home=/home/ubuntu/django/mv_env
WSGIProcessGroup MV_P-Extention
WSGIScriptAlias / /home/ubuntu/django/MV_P-Extention/Meraki_Project-Extension/mysite/mysite/wsgi.py
</VirtualHost>
```
3. Move to the project folder
``` bash
cd /home/ubuntu/django/MV_P-Extention/Meraki_Project-Extension/mysite
```
4. Give required permisson to some files with the following commands:

``` bash
chmod 664 db.sqlite3
sudo chown :www-data db.sqlite3
sudo chown :www-data ~/django/MV_P-Extention/Meraki_Project-Extension/mysite
```
5. Finally, restart apach2 server with this command.

``` bash
sudo service apache2 restart
```

###### Create Web Admin (Super User)
Inside EC2 instance, navigate to the project folder and create a super user with all privileges. 

``` bash
cd ~/django/MV_P-Extention/Meraki_Project-Extension/mysite

python manage.py createsuperuser 
```
Then, fill the form with your respective data:

``` bash
Username: Your_Name
Email address: example@mail.com
Password: admin_password
Password admin_password
```
> This super user will create any other users that will have acces to web application. 

###### Create Web App Users
Now that you have created a super user, login into the Web App and using de GUI click on add user.

This will open a new form and just need to fill with non superusers data.

![Image of Create Users](
https://github.com/MV-Automation/MV_Pandemic_Solution/blob/main/img/user_add.png)


###### Congrats! You're ready to use Meraki Vision Solution, Enjoy!

![Image of Web App](
https://github.com/MV-Automation/MV_Pandemic_Solution/blob/main/img/web_app.png)
