#!usr/bin/python

import sys
import time
import pexpect
import subprocess

def check_services_status():
    cmd = subprocess.call(["sed", "-i", 's/\r//g', filename])
    version = sys.argv[1]
    status1 = "running"
    status2 = "exited"
    docker_status = False
    contrail_services = ["Contrail control", "Contrail analytics-alarm", "Contrail database", "Contrail analytics", "Contrail config-database",
            "Contrail webui", "Contrail analytics-snmp", "Contrail config"]
    with open(filename, 'r') as reader:
        line = reader.readline()
        while line != '':
            if "$ sudo docker ps | wc -l" in line:
                dockers = int(reader.readline())+1
            elif "Original Version" in line and "State" in line:
                line = reader.readline()
                for i in range(dockers):
                    if version not in line and (status1 not in line or status2 not in line):
                        return "Error in Services"
                    line = reader.readline()
                docker_status = True
            if docker_status is True:
                if "active" not in line and not any(cs in line for cs in contrail_services) and line!='\n' and "exit" not in line:
                    return "Error in Services"
            line = reader.readline()


def get_controller_services():
    child = pexpect.spawn('ssh ubuntu@10.84.49.131')
    child.waitnoecho()
    child.sendline ('sudo docker ps | wc -l')
    child.sendline ('sudo contrail-status')
    global filename
    filename = "/tmp/services.log"
    child.logfile = open(filename, "w")
    child.expect([pexpect.EOF, pexpect.TIMEOUT], timeout=50)
    child.sendline('exit')

def main():
    get_controller_services()
    print(check_services_status())

if __name__ == "__main__":
    main()
