import RPi.GPIO as GPIO
import time
import sys
import os
import logging
import logging.handlers
from datetime import datetime
import argparse

from utils import read_json
from utils import request_password
from utils import authenticate_email
from utils import take_picture
from utils import send_email


LOG_FILENAME = 'anti_burglar_logging.log'
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(log_format)
# add console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)
# add file handler
fh = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=1000000,
                                          backupCount=5)
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)


def main(email, email_photo):
    '''
    Motion detection.
    Requirements:
    1) respaberry pi
    2) motion sensor, see
    https://thepihut.com/blogs/raspberry-pi-tutorials/raspberry-pi-gpio-sensing-motion-detection
    '''
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    settings = read_json('config/settings.json')
    email_settings = settings['email']
    save_dir = settings['store_location']

    pin = settings['pin']
    GPIO.setup(pin, GPIO.IN)

    if email:
        password = request_password()
        authenticate_email(email_settings['email'], password,
                           email_settings['host'], email_settings['port'])
        email_settings['password'] = password

    logger.debug("You have 10 secs to evacuate the room")
    time.sleep(10)  # give 10 secs to yourself to leave the room.
    logger.debug('Motion detection is on.')

    try:
        while True:
            if GPIO.input(pin):
                currenttime = datetime.now()
                filename = os.path.join(
                    save_dir, currenttime.strftime("%Y_%m_%d_%H_%M_%S"))
                msg = 'Motion detected @ %s' % currenttime
                logger.info(msg)

                # take picture
                try:
                    img_flnm = take_picture(filename)
                except Exception as e:
                    msg = 'An error occured while taking a picture: %s' % e
                    logger.error(msg)

                # send email
                if email:
                    try:
                        logger.info('Sending email')
                        img_flnm = img_flnm if email_photo else None
                        send_email(email_settings, text=msg,
                                   attached_img=img_flnm)
                        logger.info('Email sent')
                    except Exception as e:
                        msg = 'An error occured while sending email: %s' % e
                        logger.error(msg)
                # pause for 10 seconds to avoid spamming with emails.
                time.sleep(10)
            else:
                # scan the system every second
                time.sleep(1)
    except KeyboardInterrupt:

        logger.info('ctl+c')

        GPIO.cleanup()
        sys.exit()

    GPIO.cleanup()
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--email', type=str, default='yes',
                        choices=['yes', 'y', 'no', 'n'],
                        help=('Whether to send email for warning. '
                              'If no, it over-writes the `--email-photo` arg'))
    parser.add_argument('-p', '--email-photo', type=str, default='yes',
                        choices=['yes', 'y', 'no', 'n'],
                        help='whether to include photo in the email.')
    args = parser.parse_args()

    # convert input to bool
    email = True if args.email in ['yes', 'y'] else False
    email_photo = True if args.email_photo in ['yes', 'y'] else False

    # fix for inconcistency
    email_photo = False if email is False else email_photo

    main(email, email_photo)
