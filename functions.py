from log import authLog
from netmiko.exceptions import NetMikoAuthenticationException, NetMikoTimeoutException

import os
import csv
import socket
import getpass
import openpyxl
import traceback

def checkIsDigit(input_str):
    try:
        authLog.info(f"String successfully validated selection number {input_str}, from checkIsDigit function.")
        return input_str.strip().isdigit()
    
    except Exception as error:
        authLog.error(f"Invalid option chosen: {input_str}, error: {error}")
        authLog.error(traceback.format_exc())
                
def validateIP(deviceIP):
    hostnamesResolution = [
        f'{deviceIP}.mgmt.internal.das',
        f'{deviceIP}.cm.mgmt.internal.das'
    ]
        
    def checkConnect22(ipAddress, port=22, timeout=3):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connectTest:
                connectTest.settimeout(timeout)
                connectTestOut = connectTest.connect_ex((ipAddress, port))
                return connectTestOut == 0
        except socket.error as error:
            authLog.error(f"Device {ipAddress} is not reachable on port TCP 22.")
            authLog.error(f"Error:{error}\n", traceback.format_exc())
            return False

    def validIP(ip):
        try:
            socket.inet_aton(ip)
            authLog.info(f"IP successfully validated: {deviceIP}")
            return True
        except socket.error:
            authLog.error(f"IP: {ip} is not an IP Address, will attempt to resolve hostname.")
            return False

    def resolveHostname(hostname):
        try:
            hostnameOut = socket.gethostbyname(hostname)
            authLog.info(f"Hostname successfully validated: {hostname}")
            return hostnameOut
        except socket.gaierror:
            authLog.error(f"Was not posible to resolve hostname: {hostname}")
            return None

    if validIP(deviceIP):
        if checkConnect22(deviceIP):
            authLog.info(f"Device IP {deviceIP} is reachable on Port TCP 22.")
            print(f"INFO: Device IP {deviceIP} is reachable on Port TCP 22.")
            return deviceIP

    for hostname in hostnamesResolution:
        resolvedIP = resolveHostname(hostname)
        if resolvedIP and checkConnect22(resolvedIP):
            authLog.info(f"Device IP {hostname} is reachable on Port TCP 22.")
            print(f"INFO: Device IP {hostname} is reachable on Port TCP 22.")
            return hostname    

    hostnameStr = ', '.join(hostnamesResolution)  
    
    authLog.error(f"Not a valid IP address or hostname: {hostnameStr}")
    authLog.error(traceback.format_exc())
    print(f"ERROR: Invalid IP address or hostname: {hostnameStr}")

    with open('invalidDestinations.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([hostnameStr])
    
    return None

def requestLogin(validIPs):
    while True:
        try:
            username = input("Please enter your username: ")
            password = getpass.getpass("Please enter your password: ")
            # execPrivPassword = getpass.getpass("Please input your enable password: ")

            for deviceIP in validIPs:
                netDevice = {
                    'device_type': 'cisco_xe',
                    'ip': deviceIP,
                    'username': username,
                    'password': password,
                    'secret': password
                }
                # print(f"This is netDevice: {netDevice}\n")
                # print(f"This is deviceIP: {deviceIP}\n")

                # sshAccess = ConnectHandler(**netDevice)
                # print(f"Login successful! Logged to device {deviceIP} \n")
                authLog.info(f"Successful saved credentials for username: {username}")

            return validIPs, username, netDevice

        except NetMikoAuthenticationException:
            print("\n Login incorrect. Please check your username and password")
            print(" Retrying operation... \n")
            authLog.error(f"Failed to authenticate - remote device IP: {deviceIP}, Username: {username}")
            authLog.debug(traceback.format_exc())

        except NetMikoTimeoutException:
            print("\n Connection to the device timed out. Please check your network connectivity and try again.")
            print(" Retrying operation... \n")
            authLog.error(f"Connection timed out, device not reachable - remote device IP: {deviceIP}, Username: {username}")
            authLog.debug(traceback.format_exc())

        except socket.error:
            print("\n IP address is not reachable. Please check the IP address and try again.")
            print(" Retrying operation... \n")
            authLog.error(f"Remote device unreachable - remote device IP: {deviceIP}, Username: {username}")
            authLog.debug(traceback.format_exc())

def checkYNInput(stringInput):
    return stringInput.lower() == 'y' or stringInput.lower() == 'n'


def logInCSV(validDeviceIP, filename="", *args):
    print(f"INFO: File created: {filename}")
    with open(f'Outputs/{filename}.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([validDeviceIP, *args])
        authLog.info(f"Appended device: {validDeviceIP} to file {filename}")

def genTxtFile(validDeviceIP, username, filename="", *args):
    with open(f"Outputs/{validDeviceIP} {filename}.txt","a") as failedDevices:
        failedDevices.write(f"User {username} connected to {validDeviceIP}\n\n")
        for arg in args:
            if isinstance(arg, dict):
                for key,values in arg.items():
                    failedDevices.write(f"{key}: ")
                    failedDevices.write(", ".join(str(v) for v in values))
                    failedDevices.write("\n")
            
            elif isinstance(arg, list):
                for item in arg:
                    failedDevices.write(item)
                    failedDevices.write("\n")

            elif isinstance(arg, str):
                failedDevices.write(arg + "\n")

def addToList(deviceIP, generalList, *args):
    for item in args:
        if isinstance(item,list):
            generalList.extend(item)
            authLog.info(f"Item: {item} appended to list 'commandOutput' for device: {deviceIP}")
        else:
            print(f"ERROR: A list wasn't received.")
            authLog.info(f"A list wasn't received.")

def cutSheet(validIPs, *args):
    cutSheetFile = "cutSheet Base.xlsx"
    outputFolder = "Outputs"

    CutSheetBase = openpyxl.load_workbook(cutSheetFile)
    CutSheetSheet = CutSheetBase.active

    newCutSheetFile = f'{validIPs} CutSheet'
    CutSheetSheet['A1'] = f'{validIPs} CutSheet'
    authLog.info(f"Automation Successfully generated the filename: {newCutSheetFile} for the site Cut Sheet")

    columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    
    # Iterate over the arguments (lists) and the columns (A, B, C, D)
    for i, dataList in enumerate(args):
        authLog.info(f"Automation is working on the column: {i}")
        column = columns[i]  # Get the corresponding column (A, B, C, D, etc.)
        for row, value in enumerate(dataList, start=3):  # Start from row 3
            authLog.info(f"Automation is working on the row: {row}")
            cell = f'{column}{row}'  # Create the cell reference (e.g., A3, B3, etc.)
            CutSheetSheet[cell] = value  # Paste the data in the cell
            authLog.info(f"Item: {value} appended to XLSX {newCutSheetFile} for device: {validIPs}")

    newCutSheet = os.path.join(outputFolder, newCutSheetFile)
    CutSheetBase.save(newCutSheet)