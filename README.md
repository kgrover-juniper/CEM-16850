# Pre-requisites
Successfully deployed ubuntu bionic and openstack queens with contrail release 2008.123 

# Juju-ziu-upgrade and Verify-services
Required files:
1. juju-python-ziu.py
2. controller-upgrade.sh (modify as required)
3. agent-upgrade.sh (modify as required)
4. validate_services.py 

# Run Upgrade
```sh
$ python juju-python-ziu.py -c 2011.138-ubi
```
 
 Output:
 -------
 result.txt #Comment on/off write_result() in main() of juju-python-ziu.py


# Validate Contrail Services
```sh
$ python validate_services.py ubi-queens-2011-138
```
