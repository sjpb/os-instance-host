#!/usr/bin/env python3

import argparse, pprint
from tabulate import tabulate
import openstack

cli = argparse.ArgumentParser(description='Show instance hosts')
cli.add_argument('network')
cli.add_argument('-n', '--name', help='filter output to instances with names containing NAME')

class PortInfo:
    FIELDS = ('device_id', 'port_name', 'instance_name', 'compute_host')
    def __init__(self):
        for f in self.FIELDS:
            setattr(self, f, None)

    def __str__(self):
        return ' '.join(getattr(self, f) or '-' for f in self.FIELDS)

if __name__ == '__main__':
    args = cli.parse_args()
    conn = openstack.connection.from_config()
    network = conn.network.find_network(args.network)

hosts = {}
ports = []
for port in conn.network.ports(network_id=network.id):
    portinfo = PortInfo()
    if port.device_id != '':
        portinfo.device_id = port.device_id
    portinfo.port_name = port.name
    if portinfo.device_id is not None:
        instance = conn.compute.find_server(port.device_id)
        if instance is not None:
            portinfo.instance_name = instance.name
            portinfo.compute_host = instance.compute_host
            if portinfo.compute_host not in hosts:
                hosts[portinfo.compute_host] = []
            hosts[portinfo.compute_host].append(portinfo.instance_name)
            ports.append(portinfo)

if args.name is None: # output by-hosts:
    pprint.pprint(hosts)
else: # output by name:
    instance_info = [(p.instance_name, p.compute_host) for p in ports if args.name in p.instance_name]
    print(tabulate(instance_info, headers=('INSTANCE', 'HOST')))
