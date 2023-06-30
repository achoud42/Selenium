# see systemctl status supervisord 
# killall python3
# killall chromedriver

#https://selenium-python.readthedocs.io/waits.html
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from chromewebdriver_uc import ChromeWebDriver
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




def removePrefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text   
  
# return full path to processing folder


def LoadHomePage(proxy = None):
  proxy = None
  counter = 0
  
    
  respose = requests.get('http://pxymgr.vindb.org/getnextproxy?key=qulPjrM7f8&source=cf')
  p = respose.text
  proxy = p
      
  try:
    #proxy = '196.51.175.134:8800'
    chromeWebDriver = ChromeWebDriver(PROCESS_NUMBER, proxy, 0)
    print('SELECTED PROXY::::', proxy)
    chromeWebDriver.requestUrl('http://checkip.instantproxies.com')
    time.sleep(1)
    print('SCREENSHOT: ', chromeWebDriver.saveScreenshot('proxy', True))
    licenseInputXPath = '//input[@name="licensePlate"]'
    chromeWebDriver.requestUrl('https://www.givemethevin.com/',EC.visibility_of_element_located((By.XPATH, licenseInputXPath)), 5)

    page = chromeWebDriver.getCurrentPage()
    if page.find('Page timeout') != -1:
      print('Loaded Time out:', chromeWebDriver.getCurrentPage())
      print('SCREENSHOT: ', chromeWebDriver.saveScreenshot('load-time-out', True))
      chromeWebDriver.close()
      return None

    page_source = chromeWebDriver.getSource()
    if str(page_source).__contains__("Request blocked") :
        print("Request blocked")
        chromeWebDriver.close()
        return None
    licenseInput = chromeWebDriver.waitUntil(EC.presence_of_element_located((By.XPATH,licenseInputXPath)),15)
    if not licenseInput:
      url = f'http://pxymgr.vindb.org/updateonfailure?ip={proxy}&source=cf&key=qulPjrM7f8'
      requests.get(url)
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
    
  licenseInputXPath = '//*[@id="license_plate"]'
  stateInputXPath = '//*[@id="vin-form"]/div[1]/div/div[2]/select'
  milesXpath ='//*[@id="miles"]'

  zipInputXPath = '//*[@id="zip"]'
  searchXPath = '//*[@id="vin-form"]/button'
  vinXpath= '//*[@id="details-form"]/div[1]/div[1]/fieldset/p[1]/span[1]'      
  chromeWebDriver.typeCharacterByXPath(licenseInputXPath, plate)
  chromeWebDriver.typeTextByXPath(stateInputXPath, state)
  miles = random.randint(1000,100000)
  zip = '98033'
  if(state in dictZips):
    zip = random.choice(dictZips[state])
  else:
    zip = random.choice(listofZips)
  print(zip)
  chromeWebDriver.typeTextByXPath(milesXpath,miles)
  chromeWebDriver.typeTextByXPath(zipInputXPath, zip)
  chromeWebDriver.clickElementByXPath(searchXPath)  
  print("clicked on sell car")


  # Connect to the MongoDB server
  client = MongoClient(mongo_host, mongo_port)
  db = client[database_name]
  collection = db[collection_name]
  gearmanWorker.stop()
  data = {}
  

  
  try :
    
    chromeWebDriver.waitUntil(EC.presence_of_element_located((By.XPATH,vinXpath )), 10)
    vin = chromeWebDriver.getElementByXPath(vinXpath).text
    print(vin)
    data['plate'] = plate
    data['state'] = state
    data['VIN'] = vin
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
    
  except Exception as e:
    if ('Unable to locate element:' in str(e)) :
      data['plate'] = plate
      data['state'] = state
      data['error'] = 'Capctha_Block'
      url = f'http://pxymgr.vindb.org/updateonfailure?ip={proxyVerified}&source=cf&key=qulPjrM7f8'
      requests.get(url)
      errorOut = {'error' : 'permission_denied'}
      chromeWebDriver.close()
      return errorOut
    else :
      data['plate'] = plate
      data['state'] = state
      data['error'] = 'no_data'
      print(data)
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
gearmanWorker.register_task('run_search', SearchLicensePlate)
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
  if not chromeWebDriver :
   try:
    print ('Going back to home page')
    licenseInputXPath = '//input[@name="plate"]'
    chromeWebDriver.requestUrl('https://www.givemethevin.com/',EC.visibility_of_element_located((By.XPATH, licenseInputXPath)), 5)

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

