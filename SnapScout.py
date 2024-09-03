#!/usr/bin/env python3
from selenium import webdriver
from PIL import Image
import requests
import json
import socket
import os 
import argparse

parser = argparse.ArgumentParser(
    description="""An alternative to eyewitness. This tool is python based and takes either a domain or a list of urls as a source of information. 
    If a domain is given as an argument, crt.sh will be queried for the domain and a list of subdomains will be generated. If a list
    is given as an argument, the list will be taken as literal values (no dns). The timeout options is available so that a page with a long load time
    can be captured. The timeout will not complete if the page loaded before the timout completed.""",
    epilog="Package requirements include pillow requests socket and argparse.")
parser.add_argument('-d', "--domain", help="Domain that you wish to enumerate and take screenshots", type=str)
parser.add_argument('-iL', '--inlist', help='List of urls to take a snapshot of')
parser.add_argument('-t','--timeout', type=int, help="Timeout to wait for the page to load or connection",default=15 )
args = parser.parse_args()

common_web_ports = [80,443,8080,8443]
sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
options = webdriver.ChromeOptions()
options.add_argument('--ignore-ssl-errors')
options.add_argument('--ignore-certificate-errors')
driver = webdriver.Chrome(options=options)
driver.set_page_load_timeout(args.timeout)

print("""
      SnapScout running config
      ------------------------
      Domain enumeration: %s
      List enumeration:   %s
      Timeout (sec):      %s 
      """ % (args.domain,args.inlist,args.timeout))

try:
    path = "./screenshots"
    os.mkdir(path)
except FileExistsError:
    print("Screenshot directory already exists. Using it now.")
try:
    path = "./Enumeration_Files"
    os.mkdir(path)
except FileExistsError:
    print("Enumeration_Files directory already exists. Using it now.")


def take_screenshot(url,x):
    driver.get(url)
    driver.save_screenshot("screenshots/%s.png" % (str(x)))
    return

def recon_shot(url,subdomain,port):
    driver.get(url)
    driver.save_screenshot("screenshots/%s_%s.png" % (subdomain,str(port)))
    return

if args.inlist:
    x=0
    with open(args.inlist) as inlist:
        url = inlist.read()
        #print(str(url))
        take_screenshot(str(url),x)
elif args.domain:
    crt_query = requests.get("http://crt.sh/?q=%s&output=json" % args.domain,verify=False)
    raw_data = crt_query.content
    refined_data = json.loads(raw_data)
    subdomain_list = []
    unique_subdomains = []
    for x in refined_data:
        subdomain_list.append(x['common_name'])
    for x in subdomain_list:
        if x not in unique_subdomains:
            if "*" not in x:
                unique_subdomains.append(x)
    with open("./Enumeration_files/subdomains.txt", "w") as enumfile:
        for x in unique_subdomains:
            enumfile.write(x + "\n")  
    for x in unique_subdomains:
        subdomain = x
        try:
            ip_of_host = socket.gethostbyname(subdomain)
            for port in common_web_ports:
                portstate = sock.connect_ex((ip_of_host,port))
                try:
                    if portstate == 0 or portstate == 10056 or portstate == 10038:
                        recon_shot("http://%s:%s/" % (subdomain, str(port)),subdomain,port)
                        recon_shot("https://%s:%s/" % (subdomain, str(port)),subdomain,port)
                    sock.close()
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)
     
