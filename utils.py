import sys
import os
import json
import cv2
import getpass
import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


def read_json(file):
    '''Reads data from json file'''
    with open(file, 'r', encoding='utf8') as file:
        data = json.load(file)
    return data


def request_password():
    '''Request password from the user. 3 attempts, then exit'''
    n = 0
    match = False
    while n < 3:
        password1 = getpass.getpass('Type your email password:')
        password2 = getpass.getpass('Type your email password:')
        if password1 != password2:
            print('Passwords do not match, try again')
        else:
            match = True
            break
        n += 1

    exit_msg = ('Passwords do not match. Consider running without '
                'sending email warning')
    if not match:
        logger.error(exit_msg)
        sys.exit(exit_msg)
    return password1


def authenticate_email(username, password, host, port):
    '''Authenticate user's email and password'''
    valid = True
    logger.debug('establishing SMTP')
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(host=host,
                          port=port) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()

            server.login(username, password)
            logger.info('Login succesful')
    except Exception as e:
        logger.error(e)
        valid = False
        exit_msg = 'Invalid email and/or passwords.'
        logger.error(exit_msg)
        sys.exit(exit_msg)

    return valid


def take_picture(filename, format='jpg'):
    '''Capture and save image, return filename'''
    cam = cv2.VideoCapture(0)
    status, img = cam.read()
    img_flnm = '%s.%s' % (filename, format)
    if status:
        cv2.imwrite(img_flnm, img)
    return img_flnm


def send_email(email_settings, text='', attached_img=None):
    '''
    Send email with attached image (optional).
    For details on the implementation see
    https://realpython.com/python-send-email/#adding-attachments-using-the-email-package
    https://tutorials-raspberrypi.com/connect-and-control-raspberry-pi-motion-detector-pir/
    '''
    username = email_settings['email']  # sender
    password = email_settings['password']  # password
    receivers = email_settings['receivers']  # receivers
    ccs = email_settings['ccs']  # copied
    subject = email_settings['subject']  # email subject

    # convert lists to str if needed
    receivers = (', '.join(receivers) if isinstance(receivers, list)
                 else receivers)
    ccs = ', '.join(ccs) if isinstance(ccs, list) else ccs

    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = username
    message['To'] = receivers
    message['Cc'] = ccs
    message.attach(MIMEText(text, 'plain'))

    if attached_img is not None and os.path.isfile(attached_img):
        logger.debug("Add attachment")
        with open(attached_img, 'rb') as fp:
            img = MIMEImage(fp.read())
        img.add_header('Content-Disposition',
                       "attachment; filename= %s" % attached_img)
        message.attach(img)

    logger.debug('establishing SMTP')
    context = ssl.create_default_context()
    with smtplib.SMTP(host=email_settings['host'],
                      port=email_settings['port']) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()

        logger.debug('logging in')
        server.login(username, password)
        logger.debug('logged in')

        logger.debug('sending message')
        # server.sendmail(username, receivers, message.as_string())
        server.send_message(message)
        logger.debug('message sent')
    return
