#!/bin/bash

juju run-action contrail-agent/0 upgrade &&
juju run-action contrail-agent/1 upgrade &&
juju run-action contrail-agent/2 upgrade 
#juju run-action contrail-agent-csn/0 upgrade
