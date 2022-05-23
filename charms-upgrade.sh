#!/bin/bash
  
juju run-action --wait contrail-controller/leader upgrade-ziu &&
sleep 20 &&

juju upgrade-charm contrail-analytics --path /root/tf-charms/contrail-analytics
juju upgrade-charm contrail-analyticsdb --path /root/tf-charms/contrail-analyticsdb
juju upgrade-charm contrail-agent --path /root/tf-charms/contrail-agent
juju upgrade-charm contrail-openstack --path /root/tf-charms/contrail-openstack
juju upgrade-charm contrail-controller --path /root/tf-charms/contrail-controller
