import subprocess
from catscore.lib.env import get_os_type
import time
from catscore.lib.logger import CatsLogging as logging

class Tor:
    @classmethod
    def wait_start(cls):
        #proc = subprocess.Popen(['tor'], stdout=subprocess.PIPE, shell=False)
        #for line in proc.stdout:
        #    print(str(line))
            #if str(line).count("100%"):
            #    proc.kill()
            #    time.sleep(3)
            #    retur
        time.sleep(1)
        return 
    
    @classmethod
    def restart(cls):
        logging.info("tor restart")
        os_type = get_os_type()
        if os_type == "linux":
            args = ['sudo', 'service', 'tor','restart']
        elif os_type == "mac": #brew services start tor
            args = ['brew', 'services', 'restart','tor']
        logging.info(f"execute command: {args}")
        subprocess.call(args)
        cls.wait_start()

    @classmethod
    def start(cls):
        logging.info("tor start")
        os_type = get_os_type()
        if os_type == "linux":
            args = ['sudo', 'service', 'tor', 'start']
        elif os_type == "mac": #brew services start tor
            args = ['brew', 'services', 'start','tor']
        logging.info(f"execute command: {args}")
        subprocess.call(args)
        cls.wait_start()

    @classmethod
    def stop(cls):
        os_type = get_os_type()
        if os_type == "linux":
            args = ['sudo', 'service', 'tor','stop']
        elif os_type == "mac": #brew services start tor
            args = ['brew', 'services', 'stop','tor']
        subprocess.call(args)