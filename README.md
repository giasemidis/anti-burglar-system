# Anti-burglar System

A motion detection and warning system built from Raspberry Pi and PIR motion sensor.

The system scans a space for motion detection. When motion is detected, it takes a picture of the "intruder". All detections are logged to a file and pictures are stored. The system can also send an email notification to the user with the photo attached (optional).

To set-up the system you need the following components:

1. A raspberry pi (this module was built with rapsberry pi 2 B+)
2. A PIR sensor for motion detection (see https://thepihut.com/products/pir-motion-sensor-module)
3. A usb camera

## Setting up and Configuration file

Connect the usb camera to one of the usb ports of the Raspberry Pi. 

To connect the PIR sensor to the Raspberry Pi follow the instructions [here](https://tutorials-raspberrypi.com/connect-and-control-raspberry-pi-motion-detector-pir/). You are free to connect it the `OUT` pin of the PIR sensor to any GPIO pin on the Raspberry Pi. The input GPIO pin should be included in the `config/settings.json` file, next to the file `pin`. Be aware that the number should correspond to the GPIO pin number, for detils see [here](https://www.raspberrypi.org/documentation/usage/gpio/).

Next, you need to configure the `settings.json` file. 

* Choose a location where the pictures will be stored under the `store_location` field.
* Email settings:
  - Fill in your email address, where the messages will be sent from.
  - Fill in the SMTP host of the email provider
  - Fill in the port
  - Fill in the receivers' emails, if more than one, include them in a list.
  - Fill in copied email address, if more than one, include them in a list.
  - Adjust the subject to your choice.
  
## Start the system
Run the main file, which is `$ python anti_burglar_system.py`. 
 
It takes two optional console arguments:
 * `--email`, whether to send or not email warning. If not, the system works locally, logging every detection (timestamp) and every photo is stored at the specified location.
 * `--email-photo`, whether to attach the photo to the email or not.
 
When the system runs and the email option is on, it will prompt to user to write the email password. This is stored nowhere. The user must verify the password twice and has three attempts, otherwise the system exits. The system first verifies the email logging details. If succesful, it gives 10 seconds to the user to vacuate the room before the detection starts.

The system scans for motion detections every 1 second, except when motion is detected, then it scans every 10 seconds, to avoid spamming the email with photos. 

To stop it, press `ctrl + c`.
