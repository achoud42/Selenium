# see systemctl status supervisord 
# killall python3
# killall chromedriver

#https://selenium-python.readthedocs.io/waits.html
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from chromewebdriver import ChromeWebDriver
from selenium.webdriver.common.keys import Keys
from proxymanager import ProxyManager
from datetime import datetime
from stopablegearmanworker import StopableGearmanWorker
from pymongo import MongoClient
import queue
import os
import csv
import time
import traceback
import html
import glob
import os
import time
import json
import random
import sys
import requests

import csv
import random
import os
import psutil

mongo_host = "localhost"
mongo_port = 27017
database_name = "plate2vin"
collection_name = "plate2vinCollection"

file_csv = 'uszips.csv'


listofZips = []
dictZips = {}
with open(file_csv, 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
  # Do something with each row of the CSV file
        listofZips.append(row[4])
        if(row[4].strip() in dictZips and type(dictZips[row[4].strip()]) is list):
          dictZips[row[4].strip()].append(row[0])
        else:
          dictZips[row[4].strip()] = []
          dictZips[row[4].strip()].append(row[0])

if len(sys.argv) < 2:
  print('Usage: python3 run_search.py [process_number]')
#  exit()

PROCESS_NUMBER = int(sys.argv[1].strip())
print ('run_search_kbb.py : ', PROCESS_NUMBER)

LOG_PATH =  os.path.dirname(os.path.abspath(__file__)) + '/DATA_kbb/logs/'

pid = str(os.getpid())



def TryFreeMemory():
  percentMemoryAvailable = psutil.virtual_memory().available * 100 / psutil.virtual_memory().total
  print ('Current Available: ', percentMemoryAvailable)
  if percentMemoryAvailable < 30:
    os.system('/root/license_search_reset.sh')


def LogBlockedProxy(p):
  now = datetime.now()
  path = LOG_PATH + 'blocked_list.txt'
  file1 = open(path, "a")
  file1.writelines(now.strftime("%m/%d/%Y %H:%M:%S") + ',' + p)
  file1.writelines("\n")
  file1.close()

def removePrefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text   
  
# return full path to processing folder

def emailLogin(chromeWebDriver) :
  emailList = []
  
  with open(r'C:\Users\admin\Downloads\2023-gaccounts(3).csv') as csv_file:
       csv_reader = csv.reader(csv_file, delimiter=',')
       for row in csv_reader:
           emailList.append(row)
  randomChoice = random.choice(emailList)
  email = randomChoice[0]
  password = randomChoice[1]
  recovery_email = randomChoice[2]
  print(randomChoice)
  #email = 'ejfgyfjgfhfrjjfhyfxg@gmail.com' # replace email // for testing purpose
  #password = 'FJZ8mIlpf7NLWGj' # replace password  // for testing purpose
  #recovery_email = 'mr456dsdfnv3ertyert6y9@linshiyou.com'  // for testing purpose
  
  chromeWebDriver.requestUrl('https://accounts.google.com/ServiceLogin')  // for direct google login page
  

  chromeWebDriver.WaitAndtypeCharacterByName('identifier', email, 20)
  chromeWebDriver.WaitAndtypeCharacterByName('Passwd', password, 20)
  recovery_emailXPath = "//*[@id='view_container']/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div/ul/li[3]/div/div[2]"
  chromeWebDriver.waitUntil(EC.presence_of_element_located((By.XPATH, recovery_emailXPath)), 20)
  chromeWebDriver.clickElementByXPath(recovery_emailXPath)
  chromeWebDriver.WaitAndtypeCharacterByName('knowledgePreregisteredEmailResponse', recovery_email, 20)
  print('SCREENSHOT: ', chromeWebDriver.saveScreenshot('gmailLoggedIn', True))

def LoadHomePage(proxy = None):
  proxy = None
  counter = 0
  while(proxy == None and counter < 3):
    try:
      respose = requests.get('http://proxymanager.vindb.org/getnextproxy?key=qulPjrM7f8')
      p = respose.text
      p = p.replace('\"', '')
      if('shifter' not in p):
         checkurl = 'http://proxymanager.vindb.org/isproxyvalid?ip=' + p +  '&source=cf&key=qulPjrM7f8'
         response = requests.get(checkurl)
         if(response.text == 'PASS'):
            proxy = p
      else:
            proxy = p
      counter = counter + 1
    except Exception as ex:
      counter = counter + 1
      print(ex)

  try:
    if(proxy == None):
       respose = requests.get('http://lps-proxy-pool-t1m1.vindb.org/getproxy?key=a39ee16db0&source=cf')
       proxy = respose.text
       proxy = proxy.replace('\"', '')
    chromeWebDriver = ChromeWebDriver(PROCESS_NUMBER, proxy, 0)
    print('SELECTED PROXY::::', proxy)
    chromeWebDriver.requestUrl('http://checkip.instantproxies.com')
    time.sleep(1)
    print('SCREENSHOT: ', chromeWebDriver.saveScreenshot('proxy', True))
    #emailLogin(chromeWebDriver)   #comment it for removing gmail login

    licenseInputXPath = '//*[@id="BodyDivFlex"]/div[2]/div/ol/li[1]/div'
    chromeWebDriver.requestUrl('https://www.kbb.com/instant-cash-offer/',
      EC.visibility_of_element_located((By.XPATH, licenseInputXPath)), 5)
    page = chromeWebDriver.getCurrentPage()
    if page.find('Page timeout') != -1:
      print('Loaded Time out:', chromeWebDriver.getCurrentPage())
      print('SCREENSHOT: ', chromeWebDriver.saveScreenshot('load-time-out', True))
      chromeWebDriver.close()
      return None
    licenseInput = chromeWebDriver.getElementByXPath(licenseInputXPath)
    if not licenseInput:
      LogBlockedProxy(p)    
      print('blocked:', chromeWebDriver.getCurrentPage())
      print('SCREENSHOT: ', chromeWebDriver.saveScreenshot('blocked', True))
      chromeWebDriver.close()
      return None
         
    print('Loaded:', chromeWebDriver.getCurrentPage())
    return chromeWebDriver, proxy
  except Exception as error: 
     print ('EXCEPTION', error)

def SearchLicensePlate(gearmanWorker, gearman_job):
  print('STARTED.....................')
  inputJob = gearman_job.data
  print("proxy verified is :" + proxyVerified)
  print('SearchLicensePlate ' + inputJob)
  inputJob = eval(inputJob)
  plate = inputJob['plate']
  state = inputJob['state']
  #plate, state = random.choice(list(Dict.items()))
  print ('Start searching plate: ' + plate + ' state: ' + state)

  if not plate or not state:
    return
    
  clickonLP = '//*[@id="BodyDivFlex"]/div[2]/div/ol/li[1]'
  chromeWebDriver.clickElementByXPath(clickonLP)
   
  licenseInputXPath = '//input[@placeholder="License Plate"]'
  #stateInputXPath = '//div[@name="state"]'
  stateInputXPath = '//*[@id="state-entry"]'
  searchXPath = '//button[@data-testid="bi-btn-go"]'
  chromeWebDriver.typeCharacterByXPath(licenseInputXPath, plate)

  chromeWebDriver.typeTextByXPath(stateInputXPath, state)
  chromeWebDriver.clickElementByXPath(searchXPath)
  errorXPath = '//*[@id="vin-error"]'

  
  vinXpath = '//div[@class="css-90uzj3 edyetg22"]'

  time.sleep(10)
  data = {}
  expectedURL = '/ico/v1/plate2vin/lookup?stateCode='+ state +'&plateNumber='+plate + '&api_key=kehj9w5vxkt4t8yugn5zkpey'
  responseText = chromeWebDriver.getXhrReponse(expectedURL)
  print(responseText)
  o = json.loads(responseText)
  try :
    vin = o['data']['vins'][0]['vin']
    print(vin)
  except :
    vin = "no_data"
  #print(chromeWebDriver.getVinFromRaw())
  
 
  
  
  #vin = chromeWebDriver.getElementByXPath(vinXpath).text
  
  data['VIN'] = vin
  data['plate'] = plate
  data['state'] = state
  
  print (data)
  search_criteria = {  "plate" : plate , "state" : state ,"vin" : data['VIN'] }
  result = collection.find_one(search_criteria)
  if result:
     print("Document with key-value pair exists!")
  else :
     collection.insert_one(data)
     print("Inserted new document.")
  chromeWebDriver.close()
  return json.dumps(data)


 
 

chromeWebDriver = None
gearmanWorker = StopableGearmanWorker(['localhost:4730'])
gearmanWorker.register_task('run_search_cf', SearchLicensePlate)
while True:
  TryFreeMemory()
  print ('Enter while loop')
 
 
  if not chromeWebDriver:
    chromeWebDriver, proxyVerified = LoadHomePage()
    if chromeWebDriver:
      print('SCREENSHOT: ', chromeWebDriver.saveScreenshot('load-page', True))

  if not chromeWebDriver:
 #   time.sleep(1)
    continue
    
  chromeWebDriver.ResetCookie()
 
  # go back to home page
  try:
    print ('Going back to home page')
    licenseInputXPath = '//*[@id="BodyDivFlex"]/div[2]/div/ol/li[1]/div'
    chromeWebDriver.requestUrl('https://www.kbb.com/instant-cash-offer/',
      EC.visibility_of_element_located((By.XPATH, licenseInputXPath)), 5)
    page = chromeWebDriver.getCurrentPage()
    if page.find('Page timeout') != -1:
      print('ReLoaded Time out:', chromeWebDriver.getCurrentPage())
      chromeWebDriver.close()
      chromeWebDriver = None
      continue
    print('ReLoaded:', chromeWebDriver.getCurrentPage())
  except Exception as error: 
     print ('EXCEPTION', error)
     continue

  print('Working...')
  gearmanWorker.work()
  if chromeWebDriver :
     chromeWebDriver.close()
     print("close recent chrome session")
  chromeWebDriver = None
  print ('Continue to next')

