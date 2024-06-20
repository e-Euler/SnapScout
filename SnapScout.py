from selenium import webdriver
from PIL import Image
import requests
import json
import socket
import os 
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("domain", help="Domain that you wish to enumerate and take screenshots", type=str)
args = parser.parse_args()

common_web_ports = [80,443,8080,8443]
sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
options = webdriver.ChromeOptions()
options.add_argument('--ignore-ssl-errors')
options.add_argument('--ignore-certificate-errors')
driver = webdriver.Chrome(options=options)
driver.set_page_load_timeout(2)

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


def take_screenshot(url,subdomain,port):
    driver.get(url)
    driver.save_screenshot("screenshots/%s_%s.png" % (subdomain,str(port)))
    return

crt_query = requests.get("http://crt.sh/?q=%s&output=json" % args.domain)
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
                    take_screenshot("http://%s:%s/" % (subdomain, str(port)),subdomain,port)
                    take_screenshot("https://%s:%s/" % (subdomain, str(port)),subdomain,port)
                sock.close()
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)
     