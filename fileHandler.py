from log import authLog
from docx import Document
from docx.shared import RGBColor, Pt
from auth import Auth
from commandsCLI import shCoreInfo

import re
import os
import csv
import json
import traceback
import ipaddress

def docxWorkstationsCore(validIPs, username, netDevice):
    commandOutput = shCoreInfo(validIPs, username, netDevice)

    try: 
        wordFile = "Template 9300 Layer 3 Core with Workstations, Phones or Printers Config.docx"
        wordDOC = Document(wordFile)
        authLog.info(f"file successfully found: {wordFile}")
        print(f"INFO: file successfully found: {wordFile}.")

        


    except Exception as error:
        print(f"ERROR: {error}\n", traceback.format_exc())
        authLog.error(f"Wasn't possible to choose the DOCX file, error message: {error}\n{traceback.format_exc()}")

def docxCore(validIPs, username, netDevice):
    commandOutput = shCoreInfo(validIPs, username, netDevice)

    try: 
        wordFile = "Template 9300 Layer 3 Core without Workstations, Phones or Printers Config.docx"
        wordDOC = Document(wordFile)
        authLog.info(f"file successfully found: {wordFile}")
        print(f"INFO: file successfully found: {wordFile}.")

    except Exception as error:
        print(f"ERROR: {error}\n", traceback.format_exc())
        authLog.error(f"Wasn't possible to choose the DOCX file, error message: {error}\n{traceback.format_exc()}")

def docxIDF(validDeviceIPs, username, netDevice):

    try: 
        for validIPs in validDeviceIPs:
            commandOutput = []
            commandOutput = shCoreInfo(validIPs, username, netDevice)
            wordFile = "Template 9300 Layer 2 IDF Config.docx"
            wordDOC = Document(wordFile)
            authLog.info(f"file successfully found: {wordFile}")
            print(f"INFO: file successfully found: {wordFile}.")

            for command in commandOutput:
                docPara = wordDOC.add_paragraph()
                paraRun = docPara.add_run(command)
                paraRun.bold = True
                authLog.info(f"The string {command} was appended to the file {wordFile} for device {validIPs}")
            
            validIPsStr = ''.join(validIPs)
            wordDOC.save(f'Outputs/IDF Refresh for {validIPsStr}.docx')

    except Exception as error:
        print(f"ERROR: {error}\n", traceback.format_exc())
        authLog.error(f"Wasn't possible to choose the DOCX file, error message: {error}\n{traceback.format_exc()}")