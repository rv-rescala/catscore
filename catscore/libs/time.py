from datetime import datetime, timezone
import email.utils as eut

def get_current_time():
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    return now

def get_today_date():
    now = datetime.now().strftime("%Y%m%d")
    return now

def parse_http_date(s):
    """[parse http data format "Wed, 06 Nov 2019 06:53:33 GMT" to datetime]

    Arguments:
        s {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    return datetime(*eut.parsedate(s)[:6], tzinfo=timezone.utc)