import subprocess
import datetime
import os 
import shutil
import time
import argparse

class BackUp():
    def __init__(self, args):
        """ Local dir is defined as relative path.
        """
        self.args = args
        self.local_dir = os.getcwd() + "/../hokumed_backup"
        self.server = "hokumednet@153.127.43.183"
        self.server_sync_dir = "/home/hokumednet/hokumed_net_web"

    def rsync_backup(self, dir_: str):
        """

        Args:   
            dir_ : start with "/" and end with "/". Ex. "/dir/"
        """
        print(f"##### {dir_} synchronization ######")
        
        target_dir = self.server_sync_dir + dir_
        src = f"{self.server}:{target_dir}"
        dist = f"{self.local_dir}/default{dir_}"
        subprocess.check_call(["sshpass","-p", self.args.PW, "rsync","-av", src, dist])

    def copy_to_unique_dir(self):
        print("copying files...\n")
        now = datetime.datetime.now() + datetime.timedelta(seconds = 60)
        now_str = now.strftime("%Y%m%d%H%M%S") 
        now_dir = f"{self.local_dir}/back_up_{now_str}" 

        if(not os.path.exists(now_dir)):
            os.mkdir(now_dir)
        src = f"{self.local_dir}/default/."
        subprocess.check_call(["cp", "-a", src, now_dir])

    def hibernate(self):
        """Hibernate, say, sleeping for specific time.
        Change this function for test and production.
        """
        if self.args.prod:
            # for production.
            next_ = datetime.datetime.now() + datetime.timedelta(days=1)
            next_str = next_.strftime("%Y%m%d") + "120000" 
        else:
            # for test
            next_ = datetime.datetime.now() + datetime.timedelta(seconds = 60)
            next_str = next_.strftime("%Y%m%d%H%M%S") 

        subprocess.check_call(["sudo", "rtcwake","--date", next_str,"-m","mem"])
        time.sleep(20)

    def preparation(self):
        if not os.path.exists(self.local_dir):
            os.mkdir(self.local_dir)

    def start(self,n=3):
        self.preparation()
        if self.args.prod:
            print("Production mode\n")
        for i in range(3):
            self.rsync_backup("/db/")
            if self.args.prod:
                self.rsync_backup("/downloads/")
            self.copy_to_unique_dir()
            self.hibernate()

def parse_args():
    parser = argparse.ArgumentParser(description="Tranlate article from doi into markdown/html.")
    parser.add_argument("--PW", required=True,
                        help="Password for server access.")
    parser.add_argument("--prod", action="store_true",
                        help="Production movement. Wait for long, and files are also sync")

    args = parser.parse_args()
    return(args)

if __name__ == "__main__": 
    args = parse_args()
    back_up = BackUp(args)
    back_up.start(3)
