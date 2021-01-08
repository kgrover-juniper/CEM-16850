import os
import sys
import time
import argparse
import subprocess
from datetime import datetime
minutes_verify = 60

class Upgrade(object):
    def __init__ (self, contrail):
        self.contrail = contrail

    def verify_deployment(self, minutes):
        tries = 0
        status_verified = False
        while (status_verified is False and tries<minutes):
            tries += 1
            time.sleep(60)
            c1 = subprocess.Popen(["juju", "status"], stdout=subprocess.PIPE)
            c2 = subprocess.Popen(["grep", "-e allocating", "-e blocked", "-e pending", "-e waiting", "-e maintenance", "-e executing", "-e error"],
                    stdin=c1.stdout,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout = c2.communicate()[0]
            if not stdout:
                status_verified = True
            c1.wait()
        if status_verified is False:
            return -1,"Tries Expired, ",tries
        else:
            return 0,"",tries


    def verify_upgrade(self):
        tries = 0
        status_verified = False
        while (status_verified is False and tries<minutes_verify):
            tries += 1
            stages = 0
            completed = 0
            time.sleep(60)
            c1 = subprocess.Popen(["juju", "status"], stdout=subprocess.PIPE)
            c2 = subprocess.Popen(["grep", "stage/done"], stdin=c1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout = c2.communicate()[0]
            if stdout:
                lines = stdout.split("\n")
                for item in lines:
                    if item != "":
                        stages += 1
                        if item.find("5/5") != -1:
                            completed += 1
                if stages == completed:
                    status_verified = True
            c1.wait()
        if status_verified is False:
            return -1,"Tries Expired, ",tries
        else:
            return 0,"",tries

    def upgrade_procedure(self):
        controller = subprocess.call(["./controller-upgrade.sh", self.contrail], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return_code,return_message,time = self.verify_upgrade()
        if return_code == -1:
            return_message += "Controller Upgrade Failed in approx ~" + str(time) + " minutes\n"
        else:
            return_message += "Controller Upgrade Successful in approx ~" + str(time) + " minutes\n"
            agents = subprocess.call(["./agent-upgrade.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            rc,rm,t = self.verify_deployment(60)
            if rc == -1:
                return_message += rm + "Computes Upgrade Failed in approx ~" + str(t) + " minutes\n"
            else:
                return_message += rm + "Computes Upgrade Successful in approx ~" + str(t) + " minutes\n"
        return return_message


    def zero_impact_upgrade(self):
        global start,end,message
        start = datetime.now()
        return_code,return_message,_ = self.verify_deployment(1)
        if return_code == -1:
            message = "\nPreviously faulty deployment, Upgrade not possible"
        else:
            upgrade_result = self.upgrade_procedure()
            message = return_message + upgrade_result
        end = datetime.now()


    def write_result(self):
        result = "\nJuju Zero Impact Upgrade to " + str(self.contrail) + "\nStarted at " + str(start) + "\nEnded at " + str(end) + "\nTime taken = " + str(end-start) + "\n" + message
        fout = "result.txt"
        if os.path.exists(fout):
            os.remove(fout)
        with open(fout, 'w') as outfile:
            outfile.write(result)

def parse_cli(args):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-c', '--contrail', default='2011.138-ubi', help='Contrail version to upgrade)')
    pargs = parser.parse_args(args)
    return pargs

def main(contrail):
    obj = Upgrade(contrail)
    obj.zero_impact_upgrade()
    obj.write_result()

if __name__ == "__main__":
    pargs = parse_cli(sys.argv[1:])
    main(pargs.contrail)
