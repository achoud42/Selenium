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
print ('run_search_cf.py : ', PROCESS_NUMBER)

LOG_PATH =  os.path.dirname(os.path.abspath(__file__)) + '/DATA_cf/logs/'

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
  loginXPath = '//*[@id="nav-secondary"]/div[3]/div/div[2]/button/span'
  googleLoginXpath = '//*[@id="modalContent"]/section/button[1]'
  with open(r'C:\Users\admin\Downloads\2023-gaccounts(3).csv') as csv_file:
       csv_reader = csv.reader(csv_file, delimiter=',')
       for row in csv_reader:
           emailList.append(row)
  randomChoice = random.choice(emailList)
  email = randomChoice[0]
  password = randomChoice[1]
  recovery_email = randomChoice[2]
  print(randomChoice)
  email = 'ejfgyfjgfhfrjjfhyfxg@gmail.com' # replace email // for testing purpose
  password = 'FJZ8mIlpf7NLWGj' # replace password  // for testing purpose
  recovery_email = 'mr456dsdfnv3ertyert6y9@linshiyou.com'  #// for testing purpose
  
  #chromeWebDriver.requestUrl('https://accounts.google.com/ServiceLogin')  // for direct google login page
  chromeWebDriver.waitUntil(EC.presence_of_element_located((By.XPATH, loginXPath)), 10)
  chromeWebDriver.clickElementByXPath(loginXPath)
  chromeWebDriver.waitUntil(EC.presence_of_element_located((By.XPATH, googleLoginXpath)), 30)

  chromeWebDriver.clickElementByXPath(googleLoginXpath)

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
    licenseInputXPath = '//*[@id="plateNumberInput"]'
    chromeWebDriver.requestUrl("https://www.driveway.com/sell-your-car/",
      EC.visibility_of_element_located((By.XPATH, licenseInputXPath)), 10)
    #emailLogin(chromeWebDriver)   #comment it for removing gmail login
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
    
  licenseInputXPath = '//*[@id="plateNumberInput"]'
  cookiesXPath = "/html/body/div[2]/div[2]/a[1]"

  #stateInputXPath = f'//li[@class="MuiButtonBase-root MuiMenuItem-root tss-izfcuh-DWLicensePlateForm-menuItem mui-1pde8y"][@data-value="{state}"]'
  #//*[@id="menu-"]/div[3]/ul/li[1]
  stateInputXPath = f'//*[@id="menu-"]/div[3]/ul/li[@data-value="{state}"]'
  errorXPath = '//*[@id="maincontent"]/div/div[1]/div[1]/div/div[2]/div/div[2]/div[3]/div/p'
  vinXpath= '//*[@id="maincontent"]/div[2]/div/div/div/div/div/div/div[3]/p'
  searchXPath= '//button[@id="sellhome-getstarted-cta"]/span[@class="button-text"]'
  stateDropdownXpath ='//div[@id="stateSelect"]'
  print("Started entrying data ") 
 
  #chromeWebDriver.clickElementByXPath(LicenceLabelXPath)

  chromeWebDriver.typeCharacterByXPath(licenseInputXPath, plate)
  chromeWebDriver.waitUntil(EC.element_to_be_clickable((By.XPATH, cookiesXPath)),15)
  chromeWebDriver.clickElementByXPath(cookiesXPath)  
  chromeWebDriver.clickElementByXPath(stateDropdownXpath) 

  chromeWebDriver.waitUntil(EC.element_to_be_clickable((By.XPATH, stateInputXPath)),15)
  chromeWebDriver.clickElementByXPath(stateInputXPath)
  

  print("entered state")
  #chromeWebDriver.clickElementByXPath(stateInputXPath) 
  chromeWebDriver.waitUntil(EC.element_to_be_clickable((By.XPATH, searchXPath)),10)

  chromeWebDriver.clickElementByXPath(searchXPath)  
  print("clicked on GET STARTED")
  noResult =chromeWebDriver.waitUntil(EC.presence_of_element_located((By.XPATH, errorXPath)),5)
  data ={}
  expectedURL = f'/sell/v8/vehicle?plateNumber={plate}&stateCode={state}&key=e6c1852eb5124b1890fbd17ad53e870a'
  try :
    responseText = chromeWebDriver.getXhrReponse_da(expectedURL)
    print(responseText)
    #print(responseText['vin'])

    if(noResult) :
      data['VIN'] = 'no_data'
      data['plate'] = plate
      data['state'] = state
      print (data)
      chromeWebDriver.close()
      search_criteria = {  "plate" : plate , "state" : state ,"vin" : data['error'] }
      result = collection.find_one(search_criteria)
      if result:
         print("Document with key-value pair exists!")
      else :
         collection.insert_one(data)
         print("Inserted new document.")
      return json.dumps(data)
 
    else :
      data['VIN'] = responseText['vin']
      data['plate'] = plate
      data['state'] = state
      chromeWebDriver.close()
      search_criteria = {  "plate" : plate , "state" : state ,"vin" : data['VIN'] }
      result = collection.find_one(search_criteria)
      if result:
         print("Document with key-value pair exists!")
      else :
         collection.insert_one(data)
         print("Inserted new document.")
      return json.dumps(data)
      
  except :
    data['VIN'] = 'no_data'
    data['plate'] = plate
    data['state'] = state
    print (data)
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
    licenseInputXPath = '//*[@id="plateNumberInput"]'
    chromeWebDriver.requestUrl("https://www.driveway.com/sell-your-car/",
      EC.visibility_of_element_located((By.XPATH, licenseInputXPath)), 10)
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

