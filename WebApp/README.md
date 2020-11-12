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
``` bash
Code sample
```

###### Install django and apache
``` bash
Code sample
```

###### Clone git repository
``` bash
Code sample
```

###### Deploy in apache server
``` bash
Code sample
```


> Please verify versions of library used in this project before install. 