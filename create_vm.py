#!usr/bin/python
import time
import pexpect
import subprocess

def create_openstack_instance():
    child = pexpect.spawn('juju ssh contrail-agent/0')
    child.waitnoecho()
    child.sendline ('sudo su')
    child.sendline ('cd')
    child.sendline ('source admin-openrc-v3')
    child.sendline ('openstack network create test-upgrade')
    child.sendline ('openstack subnet create --subnet-range 1.1.1.0/24 --network test-upgrade test-sb')
    child.sendline ('openstack flavor create tiny  --ram 512 --disk 1 --vcpus 1')
    child.sendline ('wget http://10.84.5.120/images/converts/cirros-traffic.vmdk.gz')
    child.sendline ('gunzip cirros-traffic.vmdk.gz')
    child.sendline ('openstack image create --file cirros-traffic.vmdk --container-format bare --disk-format vmdk --property vmware_disktype="sparse" --property vmware_adaptertype="ide" cirros-test')
    child.sendline ('openstack server create --flavor tiny --image cirros-test --network test-upgrade test-instance')
    time.sleep(100)
    child.sendline ('openstack server list')
    global filename
    filename = "/tmp/instance.log"
    child.logfile = open(filename, "w")
    child.expect([pexpect.EOF, pexpect.TIMEOUT], timeout=50)
    child.sendline('exit')

def verify_instance_status():
    cmd = subprocess.call(["sed", "-i", 's/\r//g', filename])
    with open(filename, 'r') as reader:
        line = reader.readline()
        while line != '':
            if "test-instance" in line and "name" not in line and "openstack" not in line:
                if "ACTIVE" not in line:
                    return "Error in VM creation"
                else:
                    return "VM creation verified: JuJu ZIU openstack instance creation passed"
            line = reader.readline()

def main():
    create_openstack_instance()
    print(verify_instance_status())

if __name__ == "__main__":
    main()
