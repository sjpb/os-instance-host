#!/usr/bin/env python3

import argparse, openstack, pprint, collections

cli = argparse.ArgumentParser(description='Show instance hosts')
cli.add_argument('network')
cli.add_argument('-n', '--name')

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
if args.name is not None:
    print('INSTANCE HOST')
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
            if args.name is not None and args.name in portinfo.instance_name:
                print(portinfo.instance_name, portinfo.compute_host)

# output by-hosts:
if args.name is None:
    pprint.pprint(hosts)