# Raspberry Pi Interface
## Description
This repository contains the code used to run the solution's UI on the Raspberry Pi. This interface contains instructions for users to follow in order to see themselves on the screen through the RTSP stream from the MV cameras, position themselves and take a snapshot of themselves and their ID. The interface will then upload the images to AWS to compare them and discard them after the processing is done.

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
1. Clone the git repository into the Raspberry Pi. Copy it into the directory where you want it to stay.

##### Create the AmazonKeys.py and config.py files
1. The interface needs to files in order to work: AmazonKeys.py and config.py. AmazonKeys.py contains the AWS access and secret keys in order to upload the images to the cloud and config.py contains the URL for the MV camera's RTSP stream and the file path for a promotional image to be showed while the users wait for the results. The repo comes with example files with the structure for both of them. Create new files with these names and copy this structure, replacing the values with the correct ones.

<br/>

## How to Run

1. Use the terminal to navigate to the directory containing the interface.py file.
2. Run the application by using the following command:
```
python3 interface.py
```
3. The application will start and will show the instructions on how to use it.