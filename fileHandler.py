from log import authLog
from docx import Document
from docx.shared import RGBColor, Pt
from auth import Auth
from commandsCLI import shCoreInfo, shIntDesSDW

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

def docxIDF(validIPs, username, netDevice):
    commandOutput = []
    commandOutput, site_code = shCoreInfo(validIPs, username, netDevice)

    try: 
        wordFile = "Template 9300 Layer 2 IDF Config 2.docx"
        wordDOC = Document(wordFile)
        authLog.info(f"file successfully found: {wordFile}")
        print(f"INFO: file successfully found: {wordFile}.")

        tittle = wordDOC.add_heading('Below is the configuration added by the script', level=0)
        tittle.alignment = 1
        tittleRun = tittle.runs[0]
        tittleRun.font.size = Pt(24)
        tittleRun.font.bold = True
        tittleRun.font.color.rgb = RGBColor(255, 0, 0)

        for command in commandOutput:
            docPara = wordDOC.add_paragraph()
            paraRun = docPara.add_run(command)
            paraRun.bold = True
        
        wordDOC.save(f'IDF Refresh for {site_code}.docx')

    except Exception as error:
        print(f"ERROR: {error}\n", traceback.format_exc())
        authLog.error(f"Wasn't possible to choose the DOCX file, error message: {error}\n{traceback.format_exc()}")