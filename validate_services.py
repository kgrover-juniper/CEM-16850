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
                dockers = int(reader.readline())
            elif "Original Version" in line and "State" in line:
                line = reader.readline()
                for i in range(dockers):
                    if version not in line and (status1 not in line or status2 not in line) and line!='\n':
                        print line
                        return "Error in Services"
                    line = reader.readline()
                docker_status = True
            if docker_status is True:
                if "active" not in line and not any(cs in line for cs in contrail_services) and line!='\n' and "exit" not in line:
                    print line
                    return "Error in Services"
            line = reader.readline()


def get_controller_services():
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
    c3 = subprocess.Popen(["grep", "public-address"],stdin=c1.stdout,stdout=subprocess.PIPE)
    addr = c3.communicate()[0]
    addrlen = len("public-address: ")
    ip = addr[addrlen+2:]
    child = pexpect.spawn('ssh ubuntu@'+ip)
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
