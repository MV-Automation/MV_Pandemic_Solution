# Raspberry Pi Interface
## Description
This repository contains the code used to run the solution's UI on the Raspberry Pi. This interface contains instructions for users to follow in order to see themselves on the screen through the RTSP stream from the MV cameras, position themselves and take a snapshot of themselves and their ID. The interface will then upload the images to AWS to compare them and discard them after the processing is done.


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
1. Clone the git repository into the Raspberry Pi. Copy it into the directory where you want it to stay.

##### Adjust the MV camera's zoom and focus and enable the RTSP stream.
1. Navigate into the Meraki Dashboard and find the camera you are going to use.
2. Go to the Settings tab and adjust the Optical Zoom and Focus settings as shown in the picture.

![Image of Optical Zoom setting](
https://github.com/MV-Automation/MV_Pandemic_Solution/blob/main/img/focus_set.png)

3. Enable the RTSP stream and take note of the URL given, you'll need it later.

![Image ofRTSP setting](
https://github.com/MV-Automation/MV_Pandemic_Solution/blob/main/img/rtsp_set.png)

##### Add a promotional image
1. Add a promotional image to the img/ directory located in the repo, which contains all the images with the instructions for the interface. 

##### Create the AmazonKeys.py and config.py files
1. The interface needs to files in order to work: AmazonKeys.py and config.py. AmazonKeys.py contains the AWS access and secret keys in order to upload the images to the cloud and config.py contains the URL for the MV camera's RTSP stream and the file path for a promotional image to be showed while the users wait for the results. The repo comes with example files with the structure for both of them. Create new files with these names and copy this structure, replacing the values with the correct ones.


## How to Run

1. Use the terminal to navigate to the directory containing the interface.py file.
2. Run the application by using the following command:
```
python3 interface.py
```
3. The application will start and will show the instructions on how to use it.