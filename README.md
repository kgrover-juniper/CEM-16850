# Pre-requisites
Successfully deployed ubuntu bionic and openstack queens with contrail release 2008.123 

# Juju-ziu-upgrade and Verify-services
Required files:
1. juju-python-ziu.py
2. charms-upgrade.sh (modify as required)
3. twice-charms-upgrade.sh (modify as required)
4. controller-upgrade.sh (modify as required)
5. agent-upgrade.sh (modify as required)
6. validate_services.py (modify as required)
7. create_vm.py (modify as required)

# STEP 1: Run Upgrade 
```sh
$ python juju-python-ziu.py -c 2011.138-ubi
```
 
 Output:
 -------
 result.txt #Comment on/off write_result() in main() of juju-python-ziu.py


# STEP 2: Validate Contrail Services 
Finds the leader amongst the contrail-controller and verifies services
```sh
$ python validate_services.py ubi-queens-2011-138
```

# STEP 3: Validate the creation of openstack VM
```sh
$ python create_vm.py
```
