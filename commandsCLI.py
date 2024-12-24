from netmiko import ConnectHandler
from log import authLog
from functions import genTxtFile

import traceback
import ipaddress
import re
import os

shRun = "show run"
shIntStat = "show interface status | inc connected"
showVlanMGMT = "show vlan br | inc mgmt|MGMT"
shRunVLAN = "show run | sec vlan|VLAN"

commandOutput = []

intPatt = r'[a-zA-Z]+\d+\/(?:\d+\/)*\d+'
mgmtVlanPatt = r'[0-9]{4}'
idfPatt = r'-idf.*'
vlanPatt = r'vlan\s+\d+\s+name\s+[^\n]+'

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
                genTxtFile(validIPs, username, filename=f"Show run before refresh for {shHostnameOutDoc}")

                print(f"INFO: Taking a \"{shIntStat}\" for device: {validIPs}")
                shIntStatOut = sshAccess.send_command(shIntStat)
                authLog.info(f"Automation successfully ran the command:{shIntStat}\n{shHostnameOut}{shIntStat}\n{shIntStatOut}")

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