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
import json
from dataclasses import dataclass
import slackweb
import sys

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

@dataclass
class Slack:
    notice: str
    error: str

class CatsLogging:
    """[summary]
    """
    app_name = ""
    datefmt = '%d-%m-%Y:%H:%M:%S'
    format = '%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'
    slack_notice = None
    slack_error = None

    @classmethod
    def init(cls, app_name, ouput_dir, log_level, gmail:Gmail=None, slack:Slack=None):
        """[Init logger]
        
        Arguments:
            app_name {[type]} -- [description]
            ouput_dir {[type]} -- [description]
            log_level {[type]} -- [debug/info/error/critical]
        
        Keyword Arguments:
            gmail {Gmail} -- [Send logmessage over error level] (default: {None})
        """
        cls.app_name = app_name
        
        if log_level == "debug":
            level = logging.DEBUG
        elif log_level == "info":
            level = logging.INFO
        elif log_level == "warn":
            level = logging.WARN
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
        if slack:
            cls.slack_notice = slackweb.Slack(url=slack.notice)
            cls.slack_error = slackweb.Slack(url=slack.error)
            
    @classmethod
    def init_by_json(cls, json_path):
        with open(json_path, "r") as f:
            j = json.load(f)
            print(j)
            gmail = None
            try:
                gmail = Gmail(
                    username=j["gmail"]["username"],
                    password=j["gmail"]["password"],
                    to_address=j["gmail"]["to_address"])
            except Exception:
                print("gmail dosen't set")
            slack = None
            try:
                slack = Slack(
                    notice=j["slack"]["notice"],
                    error=j["slack"]["error"])
            except Exception:
                print("slack dosen't set")
            cls.init(app_name=j["log"]["app_name"], ouput_dir=j["log"]["output_dir"], log_level=j["log"]["level"], gmail=gmail, slack=slack)
        
    @classmethod
    def __add_message_option(cls, mesasge, func_name:str=None):
        host_name = socket.gethostname()
        ip_addr  =socket.gethostbyname(socket.gethostname())
        return f"{host_name},{ip_addr},{func_name},{mesasge}"

    @classmethod
    def notify(cls, message, func_name:str=None):
        try:
            cls.slack_notice.notify(text=cls.app_name + ",notify," + cls.__add_message_option(message,func_name))
        except Exception:
            print(f"cls.slack_notice has Exception: {sys.exc_info()}")
              
    @classmethod
    def debug(cls, message, func_name:str=None):
        #logger = logging.getLogger('root')
        #print(message)
        logging.debug(cls.__add_message_option(message,func_name))

    @classmethod
    def info(cls, message, func_name:str=None):
        #logger = logging.getLogger('root')
        logging.info(cls.__add_message_option(message,func_name))

    @classmethod
    def warn(cls, message, func_name:str=None):
        #logger = logging.getLogger('root')
        logger.warn(cls.__add_message_option(message,func_name))
        
    @classmethod
    def error(cls, message, func_name:str=None):
        logger = logging.getLogger('root')
        logger.error(cls.__add_message_option(message,func_name))
        try:
            cls.slack_error.notify(text=cls.app_name + ",error," + cls.__add_message_option(message,func_name))
        except Exception:
            print(f"cls.slack_error has Exception: {sys.exc_info()}")

    @classmethod
    def critical(cls, message, func_name:str=None):
        logger = logging.getLogger('root')
        logger.critical(cls.__add_message_option(message,func_name))
        if cls.slack_error:
            try:
                cls.slack_error.notify(text=cls.app_name + ",critical," + cls.__add_message_option(message,func_name))
            except Exception:
                print(f"cls.slack_error has Exception: {sys.exc_info()}")