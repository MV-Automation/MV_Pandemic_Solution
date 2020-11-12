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
cd Meraki_Project/mysite/mysite

sudo vi Meraki_Project/mysite/mysite/settings.py
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

> Please verify versions of library used in this project before install. 

###### Deploy in Apache Server

After you had installed django and deployed in EC2 instance its time to mount as a linux process to run in background. 


1. Open the *000-default.conf* file in your EC2 instance. 
``` bash
sudo vi /etc/apache2/sites-available/000-default.conf
```

2. Replace the file configuration as follows:

``` bash
<VirtualHost *:80>

	ServerAdmin webmaster@example.com
	DocumentRoot /home/ubuntu/django/Web_App/Meraki_Project/mysite
	ErrorLog ${APACHE_LOG_DIR}/error.log
	CustomLog ${APACHE_LOG_DIR}/access.log combined
	Alias /static /home/ubuntu/django/Web_App/Meraki_Project/mysite/static
<Directory /home/ubuntu/django/Web_App/Meraki_Project/mysite/static>
	Require all granted
</Directory>

<Directory /home/ubuntu/django/Web_App/Meraki_Project/mysite/mysite>
	<Files wsgi.py>
		Require all granted
	</Files>
</Directory>

	WSGIDaemonProcess Web_App python-path=/home/ubuntu/django/Web_App/Meraki_Project/mysite python-home=/home/ubuntu/django/MV_Project
	WSGIProcessGroup Web_App
	WSGIScriptAlias / /home/ubuntu/django/Web_App/Meraki_Project/mysite/mysite/wsgi.py
</VirtualHost>
```
3. Move to the project folder
``` bash
cd /home/ubuntu/django/Meraki_Project/mysite/mysite
```
4. Give required permisson to some files with the following commands:

``` bash
chmod 664 db.sqlite3
sudo chown :www-data db.sqlite3
sudo chown :www-data ~/django/Meraki_Project/mysite/mysite
```
5. Finally, restart apach2 server with this command.

``` bash
sudo service apache2 restart
```

###### Create Web Admin (Super User)
Inside EC2 instance, navigate to the project folder and create a super user with all privileges. 

``` bash
cd ~/django/Web_App/Meraki_Project/mysite
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
