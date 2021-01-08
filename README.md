# Juju-ziu-upgrade and Verify-services
Required files:
1. juju-python-ziu.py
2. controller-upgrade.sh (modify as required)
3. agent-upgrade.sh (modify as required)
4. validate_services.py 

# Command line execution
```sh
$ python juju-python-ziu.py -c 2011.138-ubi
```
 
 Output:
 -------
 result.txt #Comment on/off write_result() in main() of juju-python-ziu.py


Validate Service:
-----------------
```sh
$ python validate_services.py ubi-queens-2011-138
```
