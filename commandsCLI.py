from netmiko import ConnectHandler
from log import authLog
from functions import genTxtFile, addToList, checkIsDigit, cutSheet
from strings import hostnameTxt, ipDomainLookTxt, vtpDomainTxt, vlanTxt, hostPortTxt, trunkPortTxt, mgmtVlanTxt, defaultGateTxt, snmpLocationTxt, apIntConfigTxt, faIntConfigTxt, inputErrorString

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
shRunDefaultGateway = "show run | inc ip default-gateway"
shRunDefaultRoute = "show run | inc ip route 0.0.0.0"
shRunSNMPLocation = "show run | sec snmp-server location"
shIntAP = "show interface status | inc AP|ap"
shRunInt = "show run int "
shVlanFa = "show vlan brief | inc Facilities|facilities|FACILITIES" 

intPatt = r'[a-zA-Z]+\d+\/(?:\d+\/)*\d+'
mgmtVlanPatt = r'[0-9]{4}'
idfPatt = r'-idf.*'
vlanPatt = r'vlan\s+\d+\s+name\s+[^\n]+'
voiceVlanPatt = r'(vlan\s+)(\d+\s+)(name\s+[^\n]+[Vv][Oo][Ii][Cc][Ee])'
dataVlanPatt = r'(vlan\s+)(\d+\s+)(name\s+[^\n]+[Dd][Aa][Tt][Aa])'
ipPatt = r'\d+\.\d+\.\d+\.\d+'
vlanIDsPatt = r'\d{4}'
coreIntPatt = r'\d+\/(?:\d+\/)*\d+'
cutSheetPatt = r'([a-zA-Z]+\d+\/(?:\d+\/)*\d+|Po\d*)(\s+.*)(connected|notconnect)\s+(\d{4}|trunk)\s+(auto|a-full)\s+(auto|a-100|a-1000)'

def shCoreInfo(validIPs, username, netDevice):
    authLog.info(f"The following IP/hostname was received: {validIPs}")
    print(f"The following IP/hostname was received: {validIPs}")
    commandOutput = []
    oldInt = []
    oldIntDesc = []
    vlanIDList = []
    oldIntStat = []

    try: 
        while True:
            stackAmount = ""
            stackAmount = input(f"QUESTION: Please enter the amount of switches:")
            if checkIsDigit(stackAmount):
                print(f"INFO: The amount of switches will be: {stackAmount}")
                authLog.info(f"The amount of switches will be: {stackAmount}")
                stackAmount = int(stackAmount)
                break
            else:
                authLog.error(f"Wrong option chosen {stackAmount}")
                inputErrorString()
                os.system("PAUSE")

        authLog.info(f"The script is currently working on device: {validIPs}")
        print(f"The script is currently working on device: {validIPs}")
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

                print(f"INFO: Taking a \"{showVlanMGMT}\" for device: {validIPs}")
                showVlanMGMTOut = sshAccess.send_command(showVlanMGMT)
                authLog.info(f"Automation successfully ran the command:{showVlanMGMT}\n{shHostnameOut}{showVlanMGMT}\n{showVlanMGMTOut}")
                showVlanMGMTOut1 = re.findall(mgmtVlanPatt, showVlanMGMTOut)
                authLog.info(f"Automation successfully found the Management VLAN for device: {validIPs}: {showVlanMGMTOut1}")

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
                authLog.info(f"Automation successfully found the VLANs for device: {validIPs}: {shRunVLANOut1}")

                addToList(validIPs, commandOutput, hostnameTxt)
                commandOutput.append(f'hostname {shHostnameOutDoc}')
                authLog.info(f"The following strings were appended to list 'commandOutput':\n{shHostnameOutDoc}")

                addToList(validIPs, commandOutput, ipDomainLookTxt)
                commandOutput.append(ipDomainLookupVLAN)
                authLog.info(f"The following strings were appended to list 'commandOutput':\n{ipDomainLookupVLAN}")

                addToList(validIPs, commandOutput, vtpDomainTxt)
                commandOutput.append(vtpDomain)
                authLog.info(f"The following strings were appended to list 'commandOutput':\n{vtpDomain}")

                addToList(validIPs, commandOutput, vlanTxt)

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


                for stackNumber in range(1,stackAmount+1):
                    authLog.info(f"Generating the config for: interface range TwoGigabitEthernet{stackNumber}/0/1 - 36, on device: {validIPs}")
                    intConfigHosts = [
                        '',
                        f'interface range TwoGigabitEthernet{stackNumber}/0/1 - 36',
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
                        'mab',
                        'snmp trap mac-notification change added',
                        'no snmp trap link-status',
                        'dot1x pae authenticator',
                        'dot1x timeout tx-period 4',
                        'service-policy input ingress-untrusted-20230615',
                        'service-policy output egress-queuing-20230615',
                        'ip dhcp snooping limit rate 50'
                    ]

                    authLog.info(f"Generating the config for: interface range TenGigabitEthernet{stackNumber}/0/37 - 48, on device: {validIPs}")
                    intConfigHosts1 = [
                        '',
                        f'interface range TenGigabitEthernet{stackNumber}/0/37 - 48',
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
                        'mab',
                        'snmp trap mac-notification change added',
                        'no snmp trap link-status',
                        'dot1x pae authenticator',
                        'dot1x timeout tx-period 4',
                        'service-policy input ingress-untrusted-20230615',
                        'service-policy output egress-queuing-20230615',
                        'ip dhcp snooping limit rate 50'
                    ]

                    addToList(validIPs, commandOutput, hostPortTxt, intConfigHosts, intConfigHosts1)

                print(f"INFO: Taking a \"{shIntBr}\" for device: {validIPs}")
                shIntBrOut = sshAccess.send_command(shIntBr)
                authLog.info(f"Automation successfully ran the command:{shIntBr}\n{shHostnameOut}{shIntBr}\n{shIntBrOut}")

                shRunVLANOut1Txt  = ' '.join(shRunVLANOut1)

                allowedVlansList = re.findall(vlanIDsPatt, shRunVLANOut1Txt)
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

                shIntMgmtVlan = f"show run interface vlan {mgmtVlan} | inc ip address"
                print(f"INFO: Taking a \"{shIntMgmtVlan}\" for device: {validIPs}")
                showRunMgmtVlanOut = sshAccess.send_command(shIntMgmtVlan)
                authLog.info(f"Automation successfully ran the command:{shIntMgmtVlan}\n{shHostnameOut}{shIntMgmtVlan}\n{showRunMgmtVlanOut}")

                mgmtIPMask = re.findall(ipPatt, showRunMgmtVlanOut)
                authLog.info(f"Automation successfully found the managment IP and mask for device: {validIPs}: {mgmtIPMask}")
                mgmtIP = mgmtIPMask[0]
                mgmtIPOut = mgmtIP.split('.')
                portChannelNumber = mgmtIPOut[3]
                authLog.info(f"Automation successfully found the last portion of the IP (Port Channel Number) for device: {validIPs}: {portChannelNumber}")

                portChannel = [
                    '',
                    f'interface Port-channel{portChannelNumber}',
                    f'description {site_code}-CORE-01 - PO{portChannelNumber}',
                    'switchport',
                    'switchport access vlan 1001',
                    'switchport trunk native vlan 998',
                    f'switchport trunk allowed vlan {allowedVlans}',
                    'switchport mode trunk',
                    'logging event link-status',
                    'logging event trunk-status',
                    'snmp trap link-status',
                    'spanning-tree portfast disable',
                    'spanning-tree bpduguard disable',
                    'ip dhcp snooping trust',
                    'no shutdown'
                ]

                trunkInt = [
                    '',
                    'interface TenGigabitEthernet3/1/1',
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

                mgmtVlanInt = [
                    '',
                    f'interface Vlan{mgmtVlan}',
                    f'description {site_code}-MGMT',
                    f'{showRunMgmtVlanOut}',
                    'no ip redirects',
                    'no ip proxy-arp',
                    'no shutdown',
                    '',
                    f'ip telnet source-interface Vlan{mgmtVlan}',
                    f'ip tftp source-interface Vlan{mgmtVlan}',
                    f'ip ftp source-interface Vlan{mgmtVlan}',
                    f'ip ssh source-interface Vlan{mgmtVlan}',
                    f'ip tacacs source-interface Vlan{mgmtVlan}',
                    f'ip radius source-interface Vlan{mgmtVlan}',
                    f'logging source-interface Vlan{mgmtVlan}',
                    f'snmp-server trap-source Vlan{mgmtVlan}',
                    f'ntp source Vlan{mgmtVlan}'
                ]

                addToList(validIPs, commandOutput, trunkPortTxt, portChannel, trunkInt, mgmtVlanTxt, mgmtVlanInt)

                print(f"INFO: Taking a \"{shRunDefaultGateway}\" for device: {validIPs}")
                shRunDefaultGatewayOut = sshAccess.send_command(shRunDefaultGateway)
                authLog.info(f"Automation successfully ran the command:{shRunDefaultGateway}\n{shHostnameOut}{shRunDefaultGateway}\n{shRunDefaultGatewayOut}")

                print(f"INFO: Taking a \"{shRunDefaultRoute}\" for device: {validIPs}")
                shRunDefaultRouteOut = sshAccess.send_command(shRunDefaultRoute)
                authLog.info(f"Automation successfully ran the command:{shRunDefaultRoute}\n{shHostnameOut}{shRunDefaultRoute}\n{shRunDefaultRouteOut}")

                addToList(validIPs, commandOutput, defaultGateTxt)

                commandOutput.append(shRunDefaultGatewayOut)
                authLog.info(f"The following strings were appended to list 'commandOutput':\n{shRunDefaultGatewayOut}")

                commandOutput.append(shRunDefaultRouteOut)
                authLog.info(f"The following strings were appended to list 'commandOutput':\n{shRunDefaultRouteOut}")

                print(f"INFO: Taking a \"{shRunSNMPLocation}\" for device: {validIPs}")
                shRunSNMPLocationOut = sshAccess.send_command(shRunSNMPLocation)
                authLog.info(f"Automation successfully ran the command:{shRunSNMPLocation}\n{shHostnameOut}{shRunSNMPLocation}\n{shRunSNMPLocationOut}")

                addToList(validIPs, commandOutput, snmpLocationTxt)

                commandOutput.append(shRunSNMPLocationOut)
                authLog.info(f"The following strings were appended to list 'commandOutput':\n{shRunSNMPLocationOut}")

                print(f"INFO: Taking a \"{shIntAP}\" for device: {validIPs}")
                shIntAPOut = sshAccess.send_command(shIntAP)
                authLog.info(f"Automation successfully ran the command:{shIntAP}\n{shHostnameOut}{shIntAP}\n{shIntAPOut}")
                shIntAPOut1 = re.findall(intPatt, shIntAPOut)
                authLog.info(f"Automation successfully found the AP Ports for device: {validIPs}:\n{shIntAPOut1}")

                for apInt in shIntAPOut1:
                    print(f"INFO: Taking a \"{shRunInt}{apInt}\" for device: {validIPs}")
                    apIntOut = sshAccess.send_command(f'{shRunInt}{apInt} | exc configuration|interface')
                    authLog.info(f"Automation successfully ran the command:{shRunInt}{apInt}\n{shHostnameOut}{shRunInt}{apInt}\n{apIntOut}")

                    newInt = re.sub("Gi", "", apInt)
                    authLog.info(f"Automation successfully replaced 'Gi' in {apInt}, now it's: {newInt} on device {validIPs}")
                    newIntBase = newInt.split('/')
                    newInt0 = newIntBase[0]
                    newInt1 = newIntBase[1]
                    authLog.info(f"Automation successfully assigned: {newIntBase} to newInt0: {newInt0}, and newInt1: {newInt1} on device {validIPs}")

                    if stackAmount == 5:
                        if newInt0 == "7":
                            authLog.info(f"Automation successfully found '7' in variable newInt0: {newInt0} on device {validIPs}")
                            newInt0 = "5"
                            authLog.info(f"Automation successfully replaced '7' to '5' for variable newInt0 on device: {validIPs}\n interface will be" \
                                            f"\ninterface range TenGigabitEthernet{newInt0}/0/{newInt1}")
                        elif newInt0 == "6":
                            authLog.info(f"Automation successfully found '4' in variable newInt0: {newInt0} on device {validIPs}")
                            newInt0 = "4"
                            authLog.info(f"Automation successfully replaced '6' to '4' for variable newInt0 on device: {validIPs}\n interface will be" \
                                            f"\ninterface range TenGigabitEthernet{newInt0}/0/{newInt1}")
                    elif stackAmount == 4:
                        if newInt0 == "7":
                            authLog.info(f"Automation successfully found '7' in variable newInt0: {newInt0} on device {validIPs}")
                            newInt0 = "4"
                            authLog.info(f"Automation successfully replaced '7' to '5' for variable newInt0 on device: {validIPs}\n interface will be" \
                                            f"\ninterface range TenGigabitEthernet{newInt0}/0/{newInt1}")
                        elif newInt0 == "6":
                            authLog.info(f"Automation successfully found '4' in variable newInt0: {newInt0} on device {validIPs}")
                            newInt0 = "3"
                            authLog.info(f"Automation successfully replaced '6' to '4' for variable newInt0 on device: {validIPs}\n interface will be" \
                                            f"\ninterface range TenGigabitEthernet{newInt0}/0/{newInt1}")
                    else:
                        if newInt0 == "7":
                            authLog.info(f"Automation successfully found '7' in variable newInt0: {newInt0} on device {validIPs}")
                            newInt0 = "3"
                            authLog.info(f"Automation successfully replaced '7' to '5' for variable newInt0 on device: {validIPs}\n interface will be" \
                                            f"\ninterface range TenGigabitEthernet{newInt0}/0/{newInt1}")
                        elif newInt0 == "6":
                            authLog.info(f"Automation successfully found '4' in variable newInt0: {newInt0} on device {validIPs}")
                            newInt0 = "2"
                            authLog.info(f"Automation successfully replaced '6' to '4' for variable newInt0 on device: {validIPs}\n interface will be" \
                                            f"\ninterface range TenGigabitEthernet{newInt0}/0/{newInt1}")
                            
                    apIntConfig = [
                        '',
                        f'interface TenGigabitEthernet{newInt0}/0/{newInt1}',
                        f'{apIntOut}'
                    ]

                    apIntConfigTxt1 = ''.join(apIntConfig)

                    authLog.info(f"Automation successfully generated config for interface: TenGigabitEthernet{newInt0}/0/{newInt1} on device {validIPs}" \
                                    f"\n {apIntConfigTxt1}")
                    
                    addToList(validIPs, commandOutput, apIntConfigTxt, apIntConfig)

                print(f"INFO: Taking a \"{shVlanFa}\" for device: {validIPs}")
                shVlanFaOut = sshAccess.send_command(shVlanFa)
                authLog.info(f"Automation successfully ran the command:{shVlanFa}\n{shHostnameOut}{shVlanFa}\n{shVlanFaOut}")
                shVlanFaOut1 = re.findall(intPatt, shVlanFaOut)
                authLog.info(f"Automation successfully found the Facilities Ports for device: {validIPs}:\n{shVlanFaOut1}")

                for faInt in shVlanFaOut1:
                    print(f"INFO: Taking a \"{shRunInt}{faInt}\" for device: {validIPs}")
                    faIntOut = sshAccess.send_command(f'{shRunInt}{faInt} | exc configuration|interface')
                    authLog.info(f"Automation successfully ran the command:{shRunInt}{faInt}\n{shHostnameOut}{shRunInt}{faInt}\n{faIntOut}")

                    newInt = re.sub("Gi", "", faInt)
                    authLog.info(f"Automation successfully replaced 'Gi' in {faInt}, now it's: {newInt} on device {validIPs}")
                    newIntBase = newInt.split('/')
                    newInt0 = newIntBase[0]
                    newInt1 = newIntBase[1]
                    authLog.info(f"Automation successfully assigned: {newIntBase} to newInt0: {newInt0}, and newInt1: {newInt1} on device {validIPs}")

                    if stackAmount == 5:
                        if newInt0 == "7":
                            authLog.info(f"Automation successfully found '7' in variable newInt0: {newInt0} on device {validIPs}")
                            newInt0 = "5"
                            authLog.info(f"Automation successfully replaced '7' to '5' for variable newInt0 on device: {validIPs}\n interface will be" \
                                            f"\ninterface range TenGigabitEthernet{newInt0}/0/{newInt1}")
                        elif newInt0 == "6":
                            authLog.info(f"Automation successfully found '4' in variable newInt0: {newInt0} on device {validIPs}")
                            newInt0 = "4"
                            authLog.info(f"Automation successfully replaced '6' to '4' for variable newInt0 on device: {validIPs}\n interface will be" \
                                            f"\ninterface range TenGigabitEthernet{newInt0}/0/{newInt1}")
                    elif stackAmount == 4:
                        if newInt0 == "7":
                            authLog.info(f"Automation successfully found '7' in variable newInt0: {newInt0} on device {validIPs}")
                            newInt0 = "4"
                            authLog.info(f"Automation successfully replaced '7' to '5' for variable newInt0 on device: {validIPs}\n interface will be" \
                                            f"\ninterface range TenGigabitEthernet{newInt0}/0/{newInt1}")
                        elif newInt0 == "6":
                            authLog.info(f"Automation successfully found '4' in variable newInt0: {newInt0} on device {validIPs}")
                            newInt0 = "3"
                            authLog.info(f"Automation successfully replaced '6' to '4' for variable newInt0 on device: {validIPs}\n interface will be" \
                                            f"\ninterface range TenGigabitEthernet{newInt0}/0/{newInt1}")
                    else:
                        if newInt0 == "7":
                            authLog.info(f"Automation successfully found '7' in variable newInt0: {newInt0} on device {validIPs}")
                            newInt0 = "3"
                            authLog.info(f"Automation successfully replaced '7' to '5' for variable newInt0 on device: {validIPs}\n interface will be" \
                                            f"\ninterface range TenGigabitEthernet{newInt0}/0/{newInt1}")
                        elif newInt0 == "6":
                            authLog.info(f"Automation successfully found '4' in variable newInt0: {newInt0} on device {validIPs}")
                            newInt0 = "2"
                            authLog.info(f"Automation successfully replaced '6' to '4' for variable newInt0 on device: {validIPs}\n interface will be" \
                                            f"\ninterface range TenGigabitEthernet{newInt0}/0/{newInt1}")

                    faIntConfig = [
                        '',
                        f'interface range TenGigabitEthernet{newInt0}/0/{newInt1}',
                        f'{faIntOut}'
                    ]

                    faIntConfigTxt1 = ''.join(faIntConfig)

                    authLog.info(f"Automation successfully generated config for interface: TenGigabitEthernet{newInt0}/0/{newInt1} on device {validIPs}" \
                                    f"\n {faIntConfigTxt1}")
                    
                    addToList(validIPs, commandOutput, faIntConfigTxt, faIntConfig)

                print(f"INFO: Taking a \"{shIntStatConn}\" for device: {validIPs}")
                shIntStatConnOut = sshAccess.send_command(shIntStatConn)
                authLog.info(f"Automation successfully ran the command:{shIntStatConn}\n{shHostnameOut}{shIntStatConn}\n{shIntStatConnOut}")

                shIntStatConnOut1 = re.findall(cutSheetPatt, shIntStatConnOut)
                authLog.info(f"Automation successfully found the following old interfaces on device: { validIPs}\n{shIntStatConnOut1}")

                for i, item in enumerate(shIntStatConnOut1, start=0):
                    oldInt.append(item[0].strip())
                    oldIntDesc.append(item[1].strip())
                    vlanIDList.append(item[3].strip())

                authLog.info(f"Automation found the following old interfaces on device {validIPs}:\n{oldInt}")
                authLog.info(f"Automation found the following old interfaces description on device {validIPs}:\n{oldIntDesc}")
                authLog.info(f"Automation found the following VLANs\trunk of previous mentioned interfaces on device: {validIPs}")

                for i, item in enumerate(vlanID):
                    if item == "trunk":
                        item1 = "Trunk"
                        oldIntStat.append(item1)
                    else:
                        item1 = "Auto/Auto"
                        oldIntStat.append(item1)

                authLog.info(f"Automation found the following interfaces settings of previous mentioned interfaces on deivce: {validIPs}")

                return commandOutput, oldInt, oldIntDesc, vlanIDList, oldIntStat
            
            except Exception as error:
                print(f"ERROR: An error occurred: {error}\n", traceback.format_exc())
                authLog.error(f"User {username} connected to {validIPs} got an error: {error}")
                authLog.debug(traceback.format_exc(),"\n")
        
    except Exception as error:
        print(f"ERROR: An error occurred: {error}\n\n2", traceback.format_exc())
        authLog.error(f"User {username} connected to {validIPs} got an error: {error}")
        authLog.debug(traceback.format_exc(),"\n")
        with open(f"failedDevices.txt","a") as failedDevices:
            failedDevices.write(f"User {username} connected to {validIPs} got an error.\n")
        os.system("PAUSE")