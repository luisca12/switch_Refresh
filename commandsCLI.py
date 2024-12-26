from netmiko import ConnectHandler
from log import authLog
from functions import genTxtFile, addToList

import traceback
import ipaddress
import re
import os

shRun = "show run"
shIntStatConn = "show interface status | inc connected"
showVlanMGMT = "show vlan br | inc mgmt|MGMT"
shRunVLAN = "show run | sec vlan|VLAN"
shIntStat = "show interface status | exc Po"
shIntBr = "show ip interface brief | exclude un"
shCDPNeigh = "show cdp neighbor | sec core|CORE|Core"

commandOutput = []
intConfig = []

intPatt = r'[a-zA-Z]+\d+\/(?:\d+\/)*\d+'
mgmtVlanPatt = r'[0-9]{4}'
idfPatt = r'-idf.*'
vlanPatt = r'vlan\s+\d+\s+name\s+[^\n]+'
voiceVlanPatt = r'(vlan\s+)(\d+\s+)(name\s+[^\n]+[Vv][Oo][Ii][Cc][Ee])'
dataVlanPatt = r'(vlan\s+)(\d+\s+)(name\s+[^\n]+[Dd][Aa][Tt][Aa])'
ipPatt = r'\d+\.\d+\.\d+\.\d+'
vlanIDsPatt = r'\d{4}'
coreIntPatt = r'\d+\/(?:\d+\/)*\d+'

def shCoreInfo(validIPs, username, netDevice):

    try:
        currentNetDevice = {
            'device_type': 'cisco_xe',
            'ip': validIPs,
            'username': username,
            'password': netDevice['password'],
            'secret': netDevice['secret'],
            'global_delay_factor': 2.0,
            'timeout': 120,
            'session_log': 'netmikoLog.txt',
            'verbose': True,
            'session_log_file_mode': 'append'
        }

        print(f"Connecting to device {validIPs}...")
        with ConnectHandler(**currentNetDevice) as sshAccess:
            try:
                sshAccess.enable()
                authLog.info(f"Generating hostname for {validIPs}")
                shHostnameOutDoc = re.sub(".mgmt.internal.das|.cm.mgmt.internal.das|.mgmt.wellpoint.com","", validIPs)
                shHostnameOut = re.sub(".mgmt.internal.das|.cm.mgmt.internal.das|.mgmt.wellpoint.com","#", validIPs)
                authLog.info(f"Hostname for {validIPs}: {shHostnameOut}")
                print(f"INFO: This is the hostname: {shHostnameOut}")

                print(f"INFO: Taking a show run for device: {validIPs}")
                authLog.info(f"Taking a show run for device: {validIPs}")
                shRunOut = sshAccess.send_command(shRun)
                authLog.info(f"Successfully ran the command {shRun} on device: {validIPs}")
                genTxtFile(validIPs, username, f"Show run before refresh for {shHostnameOutDoc}", shRunOut)
                
                print(f"INFO: Taking a \"{shIntStatConn}\" for device: {validIPs}")
                shIntStatConnOut = sshAccess.send_command(shIntStatConn)
                authLog.info(f"Automation successfully ran the command:{shIntStatConn}\n{shHostnameOut}{shIntStatConn}\n{shIntStatConnOut}")

                print(f"INFO: Taking a \"{showVlanMGMT}\" for device: {validIPs}")
                showVlanMGMTOut = sshAccess.send_command(showVlanMGMT)
                authLog.info(f"Automation successfully ran the command:{showVlanMGMT}\n{shHostnameOut}{showVlanMGMT}\n{showVlanMGMTOut}")
                showVlanMGMTOut1 = re.findall(mgmtVlanPatt, showVlanMGMTOut)
                authLog.info(f"Automation successfully found the Mangaement VLAN for device: {validIPs}: {showVlanMGMTOut1}")

                mgmtVlan = f"{showVlanMGMTOut1[0]}"
                ipDomainLookupVLAN = "ip domain lookup source-interface " + f"{mgmtVlan}"
                authLog.info(f"Automation successfully completed the command \"ip domain lookup source-interface\" with VLAN {mgmtVlan} on device {validIPs}: {ipDomainLookupVLAN}")

                site_code = re.sub(idfPatt,"",shHostnameOutDoc)
                vtpDomain = "vtp domain " + f"{site_code}"
                authLog.info(f"Automation successfully completed the command \"vtp domain\" with site-code {site_code} on device {validIPs}: {vtpDomain}")

                print(f"INFO: Taking a \"{shRunVLAN}\" for device: {validIPs}")
                shRunVLANOut = sshAccess.send_command(shRunVLAN)
                authLog.info(f"Automation successfully ran the command:{shRunVLAN}\n{shHostnameOut}{shRunVLAN}\n{shRunVLANOut}")
                shRunVLANOut1 = re.findall(vlanPatt, shRunVLANOut)
                authLog.info(f"Automation successfully found the Mangaement VLAN for device: {validIPs}: {shRunVLANOut1}")

                commandOutput.append(shHostnameOutDoc, ipDomainLookupVLAN, vtpDomain)

                for vlanID in shRunVLANOut1:
                    commandOutput. append(vlanID)
                    authLog.info(f"Item: {vlanID}, from the command {shRunVLAN} was appended to the list on device: {validIPs}")
                
                dataVLAN = re.findall(dataVlanPatt, shRunVLANOut)
                voiceVLAN = re.findall(voiceVlanPatt, shRunVLANOut)

                dataVLAN = str(dataVLAN[0][1]).strip()
                voiceVLAN = str(voiceVLAN[0][1]).strip()

                print(f"INFO: Taking a \"{shIntStat}\" for device: {validIPs}")
                shIntStatOut = sshAccess.send_command(shIntStat)
                authLog.info(f"Automation successfully ran the command:{shIntStat}\n{shHostnameOut}{shIntStat}\n{shIntStatOut}")
                shIntStatOut1 = re.findall(intPatt, shIntStatOut)
                authLog.info(f"Automation successfully found the Ports for device: {validIPs}: {shIntStatOut1}")
                shIntStatOut2 = shIntStatOut1[-1]
                authLog.info(f"Automation successfully found the last Port for device: {validIPs}: {shIntStatOut2}")
                shIntStatOut3 = shIntStatOut2.split('/')
                shIntStatOut4 = int(re.sub(r'\D',"",shIntStatOut3[0]))
                authLog.info(f"Automation successfully found the total amount of line cards/stack members: {shIntStatOut4} on device: {validIPs}")

                for stackNumber in range(1,shIntStatOut4+1):
                    authLog.info(f"Generating the config for: interface range TwoGigabitEthernet{stackNumber}/0/1 - 36, on device: {validIPs}")
                    intConfigHosts = [
                        f'interface range TwoGigabitEthernet{stackNumber}/0/1 - 36'
                        'desc VOIP POE PORTS',
                        f'switchport access vlan {dataVLAN}',
                        'switchport mode access',
                        f'switchport voice vlan {voiceVLAN}',
                        'ip access-group ACL-LOW-IMPACT in',
                        'device-tracking attach-policy DEVTRK',
                        'no logging event link-status',
                        'authentication event fail action next-method',
                        f'authentication event server dead action authorize vlan {dataVLAN}',
                        'authentication event server dead action authorize voice',
                        'authentication event server alive action reinitialize',
                        'authentication host-mode multi-auth',
                        'authentication open',
                        'authentication order dot1x mab',
                        'authentication priority dot1x mab',
                        'authentication port-control auto',
                        'authentication periodic',
                        'authentication timer reauthenticate server',
                        'authentication timer inactivity server',
                        'authentication violation restrict',
                        'mab,'
                        'snmp trap mac-notification change added',
                        'no snmp trap link-status',
                        'dot1x pae authenticator',
                        'dot1x timeout tx-period 4',
                        'service-policy input ingress-untrusted-20230615',
                        'service-policy output egress-queuing-20230615',
                        'ip dhcp snooping limit rate 50'
                    ]

                    intConfigHosts1 = [
                        f'interface range TenGigabitEthernet{stackNumber}/0/37 - 48'
                        'desc VOIP POE PORTS',
                        f'switchport access vlan {dataVLAN}',
                        'switchport mode access',
                        f'switchport voice vlan {voiceVLAN}',
                        'ip access-group ACL-LOW-IMPACT in',
                        'device-tracking attach-policy DEVTRK',
                        'no logging event link-status',
                        'authentication event fail action next-method',
                        f'authentication event server dead action authorize vlan {dataVLAN}',
                        'authentication event server dead action authorize voice',
                        'authentication event server alive action reinitialize',
                        'authentication host-mode multi-auth',
                        'authentication open',
                        'authentication order dot1x mab',
                        'authentication priority dot1x mab',
                        'authentication port-control auto',
                        'authentication periodic',
                        'authentication timer reauthenticate server',
                        'authentication timer inactivity server',
                        'authentication violation restrict',
                        'mab,'
                        'snmp trap mac-notification change added',
                        'no snmp trap link-status',
                        'dot1x pae authenticator',
                        'dot1x timeout tx-period 4',
                        'service-policy input ingress-untrusted-20230615',
                        'service-policy output egress-queuing-20230615',
                        'ip dhcp snooping limit rate 50'
                    ]

                    addToList(validIPs, commandOutput, intConfigHosts, intConfigHosts1)

                print(f"INFO: Taking a \"{shIntBr}\" for device: {validIPs}")
                shIntBrOut = sshAccess.send_command(shIntBr)
                authLog.info(f"Automation successfully ran the command:{shIntBr}\n{shHostnameOut}{shIntBr}\n{shIntBrOut}")

                mgmtIP = str(re.findall(ipPatt, shIntBrOut)).strip()
                authLog.info(f"Automation successfully found the managment IP for device: {validIPs}: {mgmtIP}")
                mgmtIPOut = mgmtIP.split('.')
                portChannelNumber = mgmtIPOut[3]
                authLog.info(f"Automation successfully found the last portion of the IP (Port Channel Number) for device: {validIPs}: {portChannelNumber}")

                allowedVlansList = re.findall(vlanIDsPatt, shRunVLANOut1)
                filteredVlansList = [vlan for vlan in allowedVlansList if vlan != '1001']
                allowedVlans = ",".join(filteredVlansList).strip()

                print(f"INFO: Taking a \"{shCDPNeigh}\" for device: {validIPs}")
                shCDPNeighOut = sshAccess.send_command(shCDPNeigh)
                authLog.info(f"Automation successfully ran the command:{shCDPNeigh}\n{shHostnameOut}{shCDPNeigh}\n{shCDPNeighOut}")
                shCDPNeighOut1 = re.findall(coreIntPatt, shCDPNeighOut)

                if len(shCDPNeighOut1) < 1:
                    coreInt1 = "NOT FOUND - PLEASE DOUBLE CHECK THE INTERFACE TO THE CORE"
                    coreInt2 = "NOT FOUND - PLEASE DOUBLE CHECK THE INTERFACE TO THE CORE"
                    authLog.info(f"Automation didn't find any interface on the '{shCDPNeigh}' command on device {validIPs}")
                elif len(shCDPNeighOut1) == 2:
                    coreInt1 = shCDPNeighOut1[1]
                    coreInt2 = "NOT FOUND - PLEASE DOUBLE CHECK THE INTERFACE TO THE CORE"
                    authLog.info(f"Automation found one entry on the '{shCDPNeigh}' command on device {validIPs}: interface {coreInt1}")
                    authLog.info(f"This is part the description for the first interface going to the core: {coreInt1}")
                elif len(shCDPNeighOut1) > 2:
                    coreInt1 = shCDPNeighOut1[1]
                    coreInt2 = shCDPNeighOut1[3]
                    authLog.info(f"Automation successfully found two entries on the '{shCDPNeigh}' command on device {validIPs}: interfaces: {coreInt1} and {coreInt2}")
                    authLog.info(f"This is part the description for the first interface going to the core: {coreInt1}")
                    authLog.info(f"This is part the description for the second interface going to the core: {coreInt2}")

                portChannel = [
                    f'interface Port-channel{portChannelNumber}'
                    f'description {site_code}-CORE-01 - PO{portChannelNumber}'
                    'switchport'
                    'switchport access vlan 1001'
                    'switchport trunk native vlan 998'
                    f'switchport trunk allowed vlan {allowedVlans}'
                    'switchport mode trunk'
                    'logging event link-status'
                    'logging event trunk-status'
                    'snmp trap link-status'
                    'spanning-tree portfast disable'
                    'spanning-tree bpduguard disable'
                    'ip dhcp snooping trust'
                    'no shutdown'
                ]

                trunkInt = [
                    'interface TenGigabitEthernet3/1/1'
                    f'description {site_code}-CORE-01 - {coreInt1}',
                    'switchport access vlan 1001',
                    'switchport trunk native vlan 998',
                    f'switchport trunk allowed vlan {allowedVlans}',
                    'switchport mode trunk',
                    'logging event link-status',
                    'snmp trap link-status',
                    'udld port aggressive',
                    'spanning-tree portfast disable',
                    'spanning-tree bpduguard disable',
                    f'channel-group {portChannelNumber} mode active',
                    'service-policy output egress-queuing-20230615',
                    'ip dhcp snooping trust',
                    'no shutdown',
                    '',
                    'interface TenGigabitEthernet4/1/2',
                    f'description {site_code}-CORE-01 - {coreInt2}',
                    'switchport access vlan 1001',
                    'switchport trunk native vlan 998',
                    f'switchport trunk allowed vlan {allowedVlans}',
                    'switchport mode trunk',
                    'no logging event link-status',
                    'snmp trap link-status',
                    'udld port aggressive',
                    'spanning-tree portfast disable',
                    'spanning-tree bpduguard disable',
                    f'channel-group {portChannelNumber} mode active',
                    'service-policy output egress-queuing-20230615',
                    'ip dhcp snooping trust',
                    'no shutdown'
                ]

                addToList(validIPs, commandOutput, portChannel, trunkInt)

                return commandOutput
            
            except Exception as error:
                print(f"ERROR: An error occurred: {error}\n", traceback.format_exc())
                authLog.error(f"User {username} connected to {validIPs} got an error: {error}")
                authLog.debug(traceback.format_exc(),"\n")
    
    except Exception as error:
        print(f"ERROR: An error occurred: {error}\n", traceback.format_exc())
        authLog.error(f"User {username} connected to {validIPs} got an error: {error}")
        authLog.debug(traceback.format_exc(),"\n")
        with open(f"failedDevices.txt","a") as failedDevices:
            failedDevices.write(f"User {username} connected to {validIPs} got an error.\n")