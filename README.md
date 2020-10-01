# Golang juju-ziu-upgrade
Required files:
1. juju-python-ziu.py
2. controller-upgrade.sh
3. agent-upgrade.sh
4. validate_services.py

Command line execution:
-----------------------
```sh
$ python juju-python-ziu.py 2008.12
```
 
 Output:
 -------
 result.txt
 #Comment on/off write_result() in main() of juju-python-ziu.py


Validate Service:
-----------------
```sh
$ python validate_services.py 2008-12
```
