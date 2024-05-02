#!/usr/bin/env python3

import argparse, pprint, json, operator, dataclasses
from tabulate import tabulate
import openstack

cli = argparse.ArgumentParser(description='List ports on a given network with instance and hypervisor information.')
cli.add_argument('network', help='name of network')
cli.add_argument('-n', '--name', help='filter output to instances with names containing NAME')
cli.add_argument('-f', '--format', choices=['table', 'json'], default='table', help='output format')
cli.add_argument('-s', '--sort-by', choices=['compute_host'], help='sort output by')

class EnhancedJSONEncoder(json.JSONEncoder):
    #https://stackoverflow.com/a/51286749/916373
        def default(self, o):
            if dataclasses.is_dataclass(o):
                return dataclasses.asdict(o)
            return super().default(o)

def to_json(o):
    return json.dumps(o, cls=EnhancedJSONEncoder, indent=4)

def to_table(o):
    return tabulate(o, headers='keys', tablefmt='simple')

@dataclasses.dataclass
class PortInfo:
    device_id: str = ''
    port_name: str = ''
    instance_name: str = ''
    compute_host: str = ''
    
if __name__ == '__main__':
    args = cli.parse_args()
    conn = openstack.connection.from_config()
    network = conn.network.find_network(args.network)

ports = []
for port in conn.network.ports(): #network_id=network.id):
    portinfo = PortInfo(device_id=port.device_id, port_name=port.name) # either might still be ''
    if portinfo.device_id:
        instance = conn.compute.find_server(port.device_id)
        if instance is not None:
            portinfo.instance_name = instance.name
            portinfo.compute_host = instance.compute_host
            ports.append(portinfo)

# output
if args.name:
    ports = [p for p in ports if args.name in p.instance_name]

if args.sort_by == 'compute_host':
    ports = sorted(ports, key=operator.attrgetter('compute_host'))
if args.format == 'json':
    print(to_json(ports))
else:
    print(to_table(ports))
