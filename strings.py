import os


def greetingString():
        os.system("CLS")
        print('  -------------------------------------------------- ')
        print("    Welcome to the automated Switch Refresh Program ")
        print('  -------------------------------------------------- ')

def menuString(deviceIP, username):
        os.system("CLS")
        print(f"Connected to: {deviceIP} as {username}\n")
        print('  -------------------------------------------------------------- ')
        print('\t\tMenu - Please choose an option')
        print('\t\t  Only numbers are accepted')
        print('  -------------------------------------------------------------- ')
        print('  >\t\tPlease choose:\t\t\t\t       <')  
        print('  >\t\tOption 1: Switch Refresh\t\t       <')
        print('  >\t\tOption 2: To exit\t\t\t       <')
        print('  -------------------------------------------------------------- \n')

def inputErrorString():
        os.system("CLS")
        print('  ------------------------------------------------- ')  
        print('>      INPUT ERROR: Only numbers are allowed       <')
        print('  ------------------------------------------------- ')

def menuStringEnd():
        print('  -------------------------------------------------------------- ')
        print('\t\tMenu - Please choose an option')
        print('\t\t  Only numbers are accepted')
        print('  -------------------------------------------------------------- ')
        print('  >\t\tPlease choose the current Model:\t       <')  
        print('  >\t\t\t Option 1: vEdge\t\t       <')
        print('  >\t\t\t Option 2: ISR\t\t\t       <')
        print('  -------------------------------------------------------------- \n')
        print('  -------------------------------------------------------------- ')
        print('     The code has finished, please choose option 3 to exit')
        print('  Or choose another option to generate a new Implementation Plan')
        print('  -------------------------------------------------------------- ')
        print('  >\t\t\t Option 3: Exit\t\t\t       <')
        print('  -------------------------------------------------------------- \n')

hostnameTxt = [
        '! The configuration below is for the hostname'
]

ipDomainLookTxt = [
        '',
        '! The configuration below is for the ip domain lookup'
]

vtpDomainTxt = [
        '',
        '! The configuration below is for the vtp domain'
]

vlanTxt = [
        '',
        '! The configuration below is for the Layer 2 VLANs'
]

hostPortTxt = [
        '',
        '! For ISE monitor offices, update the ip access group to ACL-DEFAULT and the',
        '! dot1x timeout tx-period to 10.'
]

trunkPortTxt = [
        '',
        '! The configuration below is for trunking the switch to a single core switch',
        '! Match the port channel number with the last octect in the IDF management IP.'
]

mgmtVlanTxt = [
        '',
        '! The configuation below is for the Management VLAN 1500'
]

defaultGateTxt = [
        '',
        '! The configuration below is for the default gateway and route'
]

snmpLocationTxt = [
        '',
        '! The configuration below is for the SNMP location'
]