from netmiko import ConnectHandler
import netmiko
import socket
import struct
import time

iosv_12 = {
    'secret': 'Passw123'
}
ip_mask = []
k = ConnectHandler(**iosv_12)
k.enable()
output = k.send_command('show interfaces')
ip_wildcard = []

def halcim(network):
    szegmens=network.split('.')
    szegmens[3]='0'
    ip = szegmens[0] + '.' + szegmens[1] + '.' + szegmens[2] + '.' + szegmens[3]
    return ip

def subnet_to_wild(subnet_mask):
    subnet_octets = [int(octet) for octet in subnet_mask.split(".")]
    wildcard_octets = [255 - octet for octet in subnet_octets]
    wildcard_mask = ".".join(str(octet) for octet in wildcard_octets)
    return wildcard_mask

def cidr_to_netmask(cidr):
    network, net_bits = cidr.split('/')
    host_bits = 32 - int(net_bits)
    netmask = socket.inet_ntoa(struct.pack('!I', (1 << 32) - (1 << host_bits)))
    return halcim(network), netmask

for sor in output.splitlines():
    if sor.split()[0] == 'Internet':
        ip_mask.append(sor.split()[3])

for adat in ip_mask:
    subnet_mask = (cidr_to_netmask(adat)[1])
    ip_wildcard.append([cidr_to_netmask(adat)[0],subnet_to_wild(subnet_mask)])

area =input("Adja meg az ospf területazonosítóját: ")
azonosito=input("Adja meg az ospf folyamatazonosító számát (maximum 255): ")

k.send_config_set(f'router ospf {azonosito}',exit_config_mode=False)
for i in range(len(ip_mask)):
    k.send_command(f"network {ip_wildcard[i][0]} {ip_wildcard[i][1]} area {area}")

k.disconnect()


