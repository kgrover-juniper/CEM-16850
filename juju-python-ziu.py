import os
import re
import sys
import time
import filecmp
import pexpect
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

    def get_docker_start_time(self,filename):
        n = 0
        leader_found = False
        while leader_found==False:
            c1 = subprocess.Popen(["/snap/bin/juju", "show-unit", "contrail-controller/"+str(n)],stdout=subprocess.PIPE)
            c2 = subprocess.Popen(["grep", "leader"],stdin=c1.stdout,stdout=subprocess.PIPE)
            lead = c2.communicate()[0]
            if "true" not in lead:
                n += 1
            else:
                leader_found = True
        child = pexpect.spawn('juju ssh contrail-controller/'+str(n))
        child.waitnoecho()
        child.logfile = open(filename, "w")
        child.sendline('sudo docker ps --format "{{.ID}}: {{.CreatedAt}}"')
        child.expect([pexpect.EOF, pexpect.TIMEOUT], timeout=50)
        child.sendline('exit')

    def verify_docker_start_time(self, filename):
        cmd = subprocess.call(["sed", "-i", 's/\r//g', filename])
        comd_line = "sudo docker ps --format "
        data = []
        flag = False
        index = 0
        with open(filename,'r') as f:
            for line in f:
                if comd_line in line:
                    index += 1
                if index == 2 and line.startswith(comd_line):
                    flag = True
                elif index == 2 and line.strip().endswith('exit'):
                    flag = False
                elif flag:
                    data.append(line)
        return data[:-1]

    def upgrade_charms(self):
        # upgrade contrail chatms
        self.get_docker_start_time("/tmp/docker_start_time.log")
        charms = subprocess.call(["./charms-upgrade.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.get_docker_start_time("/tmp/docker_latest_time.log")
        data_at_start = self.verify_docker_start_time("/tmp/docker_start_time.log")
        data_re_start = self.verify_docker_start_time("/tmp/docker_latest_time.log")
        # upgrade agent charm twice and check that deployment should not break
        if data_at_start == data_re_start:
            charms = subprocess.call(["./twice-charms-upgrade.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return_code,return_message,_ = self.verify_deployment(1)
            return True
        else:
            return False

    def upgrade_procedure(self):
        rm_charms = upgarde_charms()
        if rm_charms == True:
            controller = subprocess.call(["./controller-upgrade.sh", self.contrail], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            rc_controller, rm_controller, time_controller = self.verify_upgrade()
            if rc_controller == -1:
                return_message = rm_controller + "Controller Upgrade Failed in approx ~" + str(time_controller) + " minutes\n"
            else:
                return_message = rm_controller + "Controller Upgrade Successful in approx ~" + str(time_controller) + " minutes\n"
                agents = subprocess.call(["./agent-upgrade.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                rc_agents, rm_agents, time_agents = self.verify_deployment(60)
                if rc_agents == -1:
                    return_message += rm_agents + "Computes Upgrade Failed in approx ~" + str(time_agents) + " minutes\n"
                else:
                    return_message += rm_agents + "Computes Upgrade Successful in approx ~" + str(time_agents) + " minutes\n" 
                    return_message += "JuJu ZIU upgrade charms, controller and comptutes passed\n"
        else:
            return "Charms upgrade Failed \n"
        return return_message


    def zero_impact_upgrade(self):
        global start,end,message
        start = datetime.now()
        return_code,return_message,_ = self.verify_deployment(1)
        if return_code == -1:
            message = "\nPreviously faulty deployment, Upgrade not possible"
        else:
            upgrade_result = self.upgrade_procedure()
        message = upgrade_result
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
