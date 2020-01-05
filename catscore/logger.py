import logging
import logging.handlers
from datetime import datetime
import os
import errno
import logging
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
import socket

class Gmail:
    smtp_url = 'smtp.gmail.com'
    smtp_port = 587

    def __init__(self, username, password, to_address):
        """[summary]

        Arguments:
            username {[type]} -- [description]
            password {[type]} -- [description]
            to_address {[type]} -- [description]
        """
        self.username = username
        self.password = password
        self.to_address = to_address

    def login(self):
        """[summary]
        """
        self.smtp = smtplib.SMTP(self.smtp_url, self.smtp_port)
        self.smtp.ehlo()
        self.smtp.starttls()
        self.smtp.ehlo()
        self.smtp.login(self.username, self.password)

    def send(self, body, subject):
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.username
        msg['To'] = self.conf.to_address
        msg['Date'] = formatdate()
        self.smtp.sendmail(self.username, self.to_address, msg.as_string())

    def close(self):
        self.smtp.close()

class CatsLogging:
    """[summary]
    """

    datefmt = '%d-%m-%Y:%H:%M:%S'
    format = '%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'

    @classmethod
    def init(cls, app_name, ouput_dir, log_level, gmail: Gmail=None):
        """[Init logger]
        
        Arguments:
            app_name {[type]} -- [description]
            ouput_dir {[type]} -- [description]
            log_level {[type]} -- [debug/info/error/critical]
        
        Keyword Arguments:
            gmail {Gmail} -- [Send logmessage over error level] (default: {None})
        """
        if log_level == "debug":
            level = logging.DEBUG
        elif log_level == "info":
            level = logging.INFO
        elif log_level== "error":
            level = logging.ERROR
        elif log_level == "critical":
            level = logging.CRITICAL
        else:
            level = logging.INFO

        logging.basicConfig(level=level,
                            filename=f"{ouput_dir}/{app_name}.log",
                            format=cls.format,
                            datefmt=cls.datefmt)
        logging.getLogger('sqlalchemy.engine').setLevel(level)
        if gmail:
                try:
                    gmail.login()
                    handler = logging.handlers.SMTPHandler(mailhost=(gmail.smtp_url, gmail.smtp_port),
                                                        fromaddr=gmail.username,
                                                        toaddrs=gmail.to_address,
                                                        subject=app_name,
                                                        credentials=(gmail.username, gmail.password),
                                                        secure=())
                    handler.setLevel(logging.ERROR)
                    logger = logging.getLogger('root')
                    logger.addHandler(handler)
                except smtplib.SMTPAuthenticationError:
                    cls.error("Cannot login to google")

    @classmethod
    def __add_message_option(cls, mesasge):
        host_name = socket.gethostname()
        ip_addr  =socket.gethostbyname(socket.gethostname())
        return f"{host_name},{ip_addr},{mesasge}"

    @classmethod
    def debug(cls, message):
        #logger = logging.getLogger('root')
        #print(message)
        logging.debug(cls.__add_message_option(message))

    @classmethod
    def info(cls, message):
        #logger = logging.getLogger('root')
        logging.info(cls.__add_message_option(message))

    @classmethod
    def error(cls, message):
        logger = logging.getLogger('root')
        logger.error(cls.__add_message_option(message))

    @classmethod
    def critical(cls, message):
        logger = logging.getLogger('root')
        logger.critical(cls.__add_message_option(message))