import os


def greetingString():
        os.system("CLS")
        print('  ------------------------------------------------------------------------- ')
        print("    Welcome to the automated Tier 2-Implementation Plan generation program ")
        print('  ------------------------------------------------------------------------- ')

def menuString():
        print('  -------------------------------------------------------------- ')
        print('\t\tMenu - Please choose an option')
        print('\t\t  Only numbers are accepted')
        print('  -------------------------------------------------------------- ')
        print('  >\t\tPlease choose the current Model:\t       <')  
        print('  >\t\t\t Option 1: vEdge\t\t       <')
        print('  >\t\t\t Option 2: ISR\t\t\t       <')
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