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

#mongo connection details

mongo_host = "localhost"
mongo_port = 27017
database_name = "plate2vin"
collection_name = "plate2vinCollection"


if len(sys.argv) < 2:
  print('Usage: python3 run_search.py [process_number]')
#  exit()

PROCESS_NUMBER = int(sys.argv[1].strip())
print ('run_search.py : ', PROCESS_NUMBER)



LOG_PATH =  os.path.dirname(os.path.abspath(__file__)) + '/DATA_ac/logs/'

pid = str(os.getpid())

import os
import psutil
import requests

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
  
  
# return full path to processing folder

  
# gotResult = Ture means got some result, can move on.
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
  #email = 'ejfgyfjgfhfrjjfhyfxg@gmail.com' # replace email  //for testing purpose
  #password = 'FJZ8mIlpf7NLWGj' # replace password   //for testing purpose
  #recovery_email = 'mr456dsdfnv3ertyert6y9@linshiyou.com'   //for testing purpose
  
  chromeWebDriver.requestUrl('https://accounts.google.com/ServiceLogin')
  chromeWebDriver.WaitAndtypeCharacterByName('identifier', email, 20)
  chromeWebDriver.WaitAndtypeCharacterByName('Passwd', password, 20)
  recovery_emailXPath = "//*[@id='view_container']/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div/ul/li[3]/div/div[2]"
  chromeWebDriver.waitUntil(EC.presence_of_element_located((By.XPATH, recovery_emailXPath)), 20)
  chromeWebDriver.clickElementByXPath(recovery_emailXPath)
  chromeWebDriver.WaitAndtypeCharacterByName('knowledgePreregisteredEmailResponse', recovery_email, 20)
  print('SCREENSHOT: ', chromeWebDriver.saveScreenshot('gmailLoggedIn', True))



def removePrefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text 

def LoadHomePage(proxy = None):
  proxy = None
  counter = 0

  while(proxy == None and counter < 3):
    try:
      respose = requests.get('http://proxymanager.vindb.org/getnextproxy?key=qulPjrM7f8')
      p = respose.text
      p = p.replace('\"', '')
      if('shifter' not in p):
         checkurl = 'http://proxymanager.vindb.org/isproxyvalid?ip=' + p +  '&source=ac&key=qulPjrM7f8'
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
    chromeWebDriver = ChromeWebDriver(PROCESS_NUMBER, proxy, 13)
    chromeWebDriver.requestUrl('http://checkip.instantproxies.com')
    time.sleep(1)
    print('SCREENSHOT: ', chromeWebDriver.saveScreenshot('proxy', True))
    #emailLogin(chromeWebDriver)   // uncomment this for add gmail login before autocheck url opens
    print('SELECTED *********************', proxy)
    licenseInputXPath = '//input[@name="plate"]'
    chromeWebDriver.requestUrl('https://www.autocheck.com/vehiclehistory/search-by-license-plate',
      EC.visibility_of_element_located((By.XPATH, licenseInputXPath)), 10)
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
  
   # Get plate and state
  inputJob = gearman_job.data
  print('SearchLicensePlate ' + inputJob)
  print("verified proxy is : " + proxyVerified)
  inputJob = eval(inputJob)
  plate = inputJob['plate']
  state = inputJob['state']
  print ('Start searching plate: ' + plate + ' state: ' + state)
  gearmanWorker.stop()
  if not plate or not state:
    return
    
  licenseInputXPath = '//input[@name="plate"]'
  stateInputXPath = '//select[@name="plateState"]'
  searchXPath = '//button[@type="submit"]'
  chromeWebDriver.typeTextByXPath(licenseInputXPath, plate)
  #time.sleep(1)
  chromeWebDriver.typeTextByXPath(stateInputXPath, state)
  chromeWebDriver.clickElementByXPath(searchXPath)  


  waitXPath =  '//p[contains(text(), "VINs with that license")] | //div[contains(@class, "vehicle-search_error_3dLuA") or contains(@class, "vehicle-search_records")]'
  if not chromeWebDriver.waitUntil(EC.presence_of_element_located((By.XPATH, waitXPath)), 10):
    print('No Result')
    print('SCREENSHOT: ', chromeWebDriver.saveScreenshot('no result', True))
    return "NO_RESULT"

  expectedURL = 'consumer-api/meta/v1/summary/plate/'+ plate
  responseText = chromeWebDriver.getXhrReponse(expectedURL)

  #Connect to the MongoDB server
  client = MongoClient(mongo_host, mongo_port)
  db = client[database_name]
  collection = db[collection_name]

  if responseText:  
    print (responseText)
    o = json.loads(responseText)
    print (o)
    if type(o) is list and o[0] and o[0]['vin']:
      data = o[0]
      data['plate'] = plate
      data['state'] = state
      data['VIN'] = o[0]['vin']
      if 'timestamp' in data:
        del data['timestamp']
      if 'path' in data:
        del data['path']


     # data = {'plate': plate, 'state': state, 'VIN': o[0]['vin']}
     # print ('Found :')
      print (data)
      search_criteria = {  "plate" : plate , "state" : state ,"vin" : data['VIN'] }
      result = collection.find_one(search_criteria)
      if result:
         print("Document with key-value pair exists!")
      else :
         collection.insert_one(data)
         print("Inserted new document.")
      if('shifter' not in proxyVerified):
         try:
           requests.get('http://proxymanager.vindb.org/updateonsuccess?ip='+ proxyVerified +'&source=ac&key=qulPjrM7f8')
         except Exception as ex:
           print(ex)
      return json.dumps(data)
    elif 'error' in o and o['error'] == 'Not Found':
      data = o
      data['plate'] = plate
      data['state'] = state
      data['error'] = 'no_data'
      search_criteria = {  "plate" : plate , "state" : state ,"vin" : data['error'] }
      result = collection.find_one(search_criteria)
      if result:
         print("Document with key-value pair exists!")
      else :
         collection.insert_one(data)
         print("Inserted new document.")
      return json.dumps(data)
    #elif 'message' in o and (o['message'] == 'reCaptcha score is too low' || o['message'] == 'reCaptcha') :      
    elif 'error' in o and o['error'] == 'Bad Request' :      
      print (o['message'])
      pm = ProxyManager()
      pm.markProxyBad(chromeWebDriver.proxy)
      errorOut = {'error' : 'permission_denied'}
      if('shifter' not in proxyVerified):
        try:
           requests.get('http://proxymanager.vindb.org/updateonfailure?ip='+ proxyVerified +'&source=ac&key=qulPjrM7f8')
        except Exception as ex:
           print(ex)
      chromeWebDriver.close()
      #os._exit(0)
      return json.dumps(errorOut)
    else:
      print ('error:', o)
      errorOut = {'error' : ' internal_error'}
      chromeWebDriver.close()
      return json.dumps(errorOut)




gearmanWorker = StopableGearmanWorker(['localhost:4730'])
gearmanWorker.register_task('run_search_ac', SearchLicensePlate)


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
    licenseInputXPath = '//input[@name="plate"]'
    chromeWebDriver.requestUrl('https://www.autocheck.com/vehiclehistory/search-by-license-plate',
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
  chromeWebDriver = None
  print ('Continue to next')




