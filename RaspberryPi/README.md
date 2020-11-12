# Raspberry Pi Interface
## Description
This repository contains the code used to run the solution's UI on the Raspberry Pi.

</br>

## Installation Steps

##### Updating the OS and installing the dependencies
1. First, it's important to make sure the Raspberry Pi's OS, Raspbian, is updated. In order to do this, run the following code in the terminal.

```
sudo apt-get update
sudo apt full-upgrade --fix-missing
sudo reboot
```
<br/>

2. After that, we need to install two Python related packages and libraries so all of our Python dependencies work

```
sudo apt-get install libatlas-base-dev
sudo apt-get install python3-tk 
```
<br/>

3. Finally, we can use pip to install all of the Python packages that are needed.
```
pip3 install opencv-python
pip3 install Pillow
pip3 install boto3
pip3 install getmac
pip3 install pytz
pip3 install response
```
##### Cloning the repository

##### Create the AmazonKeys.py and config.py files


