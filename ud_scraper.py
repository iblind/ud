import paramiko
import logging
import requests
from bs4 import BeautifulSoup
import string
import json
import re
import time
import random
import dataset
import smtplib
from datetime import datetime
#from TorCtl import TorCtl
from stem import Signal
from stem.control import Controller
import urllib2
import socket

name_of_server = socket.gethostname()

#function defs for ip change

#setting up user agent headers
chrome_49="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36"
chrome_NF="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36"
chrome_41="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36"
chrome_37="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36"
safari_9="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/601.5.17 (KHTML, like Gecko) Version/9.1 Safari/601.5.17"
safari_7="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A"
safari_5="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2"
ie_11="Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko"
ie_106="Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727) 3gpp-gba UNTRUSTED/1.0"
firefox_41="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:41.0) Gecko/20100101 Firefox/41.0"
firefox_40="Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1"

all_user_agents=[chrome_49,chrome_NF,chrome_41,chrome_37,safari_9,safari_7,safari_5,ie_11,ie_106,firefox_40, firefox_41]


user_agent = random.choice(all_user_agents)
headers={'User-Agent':user_agent}

#configuring the tor connection + the request functions
def request(url):
    def _set_urlproxy():
        proxy_support = urllib2.ProxyHandler({"http" : "127.0.0.1:8118"})
        opener = urllib2.build_opener(proxy_support)
        urllib2.install_opener(opener)
    _set_urlproxy()
    request=urllib2.Request(url, None, headers)
    return urllib2.urlopen(request).read()



#Stem used as Tor controller.
def renew_connection():
   with Controller.from_port(port = 9051) as controller:
     controller.authenticate()
     controller.signal(Signal.NEWNYM)
     user_agent=random.choice(all_user_agents)



#checking the time

#setting time variables
time_atm = datetime.now()
timetostart = time_atm.replace(hour=23, minute=0, second=0, microsecond=0)
timetostop = time_atm.replace(hour=8, minute=0, second=0, microsecond=0)

#setting time function
def check_time():
    if (time_atm > timetostart) and (time_atm < timetostop):
        return random.randrange(6,12,1) ##Nighttime, so speed up
    else:
        return random.randrange(15,30,1) ## Daytime, so slow down

error_boolean=0

startTime = datetime.now()

#load letters list
with open('shuffled_all_words_90k.txt', 'r') as infile:
    list_of_letter_terms = infile.read().splitlines()


#Getting last written word. If last_called_index.txt exists, use the index number therein to
try:
    with open('last_called_index.txt', 'r') as infile:
        overall_counter = int(infile.read())
except:
    overall_counter=0

pages_per_term_objects=[]
db = dataset.connect('sqlite:///pages_per_word.db')

iterations_counter=0
exception_counter=0
#Select number of words to go through before we reset the IP address.
iterations_before_ip_change= random.randrange(10,50,1)



for term in list_of_letter_terms[overall_counter:]:

    #Save the index of the term that you're about to work on
    with open('last_called_index.txt', 'w') as outfile:
        outfile.write(str(overall_counter))




    #Increment overall counter by one; this actually indicates being a word ahead of where we really
    #are, but I'm incrememnting it early on instead of at the end of the script because it's easier.
    overall_counter+=1


    #If the number of interations
    if iterations_counter==iterations_before_ip_change:
        while True:
            try:
                renew_connection()
                time.sleep(10)
                user_agent = random.choice(all_user_agents)
                headers={'User-Agent':user_agent}
                iterations_counter=0
                iterations_before_ip_change= random.randrange(10,50,1)
                break
            except:
                time.sleep(20)
                exception_counter+=1
                if exception_counter==25:
                    duration =  ((datetime.now() - startTime).total_seconds())/60
                    list_size = str(len(list_of_letter_terms))
                    list_location = str(list_of_letter_terms.index(term))

                    #SSH into server that'll connect to gmail and pass it the appropriate arguments to send
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(
                        paramiko.AutoAddPolicy())
                    ssh.connect('IP_ADDRESS', username='USERNAME',
                        password='PASSWORD')
                    stdin, stdout, stderr = ssh.exec_command(
                        "python email_connection_error.py " + str(list_location)+" "+str(list_size)+" "+term+" "+str(duration)+" "+name_of_server)
                    error_boolean = 1
                    break
                else:
                    continue



    iterations_counter+=1
    time.sleep(check_time())
    url ="http://www.urbandictionary.com/define.php?term="+term
    try:
        html_str = request(url)
        document = BeautifulSoup(html_str)

        temp_term_obj={}
        temp_term_obj['term']=term

        temp_ul= document.find('ul', attrs={'class':'pagination'})

        if temp_ul is None:
            temp_term_obj['pages']=1
            db['words'].upsert(temp_term_obj, ['term'])
            continue

        else:
            temp_a=temp_ul.find_all('a')

            if temp_a[-1:][0].string[0:4]=="Last":
                temp_var = temp_a[-1:][0]['href'][-3:]
                temp_var = re.sub('[=e]', '', temp_var)
                temp_term_obj['pages']= temp_var
                db['words'].upsert(temp_term_obj, ['term'])
            else:
                db['error_urls'].upsert(temp_term_obj, ['term'])

    except Exception as e:

        duration =  ((datetime.now() - startTime).total_seconds())/60
        list_size = str(len(list_of_letter_terms))
        list_location = str(list_of_letter_terms.index(term))

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())
        ssh.connect('IP_ADDRESS', username='USERNAME',
            password='PASSWORD')
        stdin, stdout, stderr = ssh.exec_command(
            "python email_word_error.py " + str(list_location)+" "+str(list_size)+" "+term+" "+str(duration)+" " + name_of_server)
        error_boolean = 1
        break

#Sending email on completion
if error_boolean==0:
    duration =  ((datetime.now() - startTime).total_seconds())/60
    list_size = str(len(list_of_letter_terms))
    list_location = str(list_of_letter_terms.index(term))

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(
        paramiko.AutoAddPolicy())
    ssh.connect('IP_ADDRESS', username='USERNAME',
        password='PASSWORD')
    stdin, stdout, stderr = ssh.exec_command(
        "python email_completion.py " + str(list_location)+" "+str(list_size)+" "+term+" "+str(duration)+ " "+name_of_server)

else:
    print "ERROR, DAWG"
