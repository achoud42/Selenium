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
from urllib.parse import urlparse
import re
import requests



if len(sys.argv) < 2:
  print('Usage: python3 run_search.py [process_number]')
#  exit()

PROCESS_NUMBER = int(sys.argv[1].strip())
print ('run_search.py : ', PROCESS_NUMBER)

MAX_PROCESSED_COUNT = 10

INPUT_PATH = os.path.dirname(os.path.abspath(__file__)) + '/DATA_ed/input/'
PROCESS_PATH = os.path.dirname(os.path.abspath(__file__)) + '/DATA_ed/processing/'
DONE_PATH = os.path.dirname(os.path.abspath(__file__)) + '/DATA_ed/done/'
LOG_PATH =  os.path.dirname(os.path.abspath(__file__)) + '/DATA_ed/logs/'

pid = str(os.getpid())

import os
import psutil

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
def getNextFile():
  listFiles = filter( os.path.isfile,
                          glob.glob(INPUT_PATH + '*') )
          
  listFiles = sorted( listFiles,
                          key = os.path.getmtime)

  newPath = None
  if len(listFiles) > 0:
    origFullPath = listFiles[0]
    fname = os.path.basename(origFullPath)
    fnameNew = fname + '.' + pid
    newPath = PROCESS_PATH + fnameNew
    os.rename(origFullPath, newPath)
    if os.path.exists(newPath):
      print ('Moved ' + newPath)
  if not newPath:
    return None
  filename = os.path.basename(newPath)
  x = filename.split(".")  # file name formate is filename.process_id
  donePath = DONE_PATH + x[0]
  if os.path.exists(donePath):
    os.remove(newPath)
    print ('Has Result for ' + donePath)
    return None
  return newPath
  
# gotResult = Ture means got some result, can move on.
def SaveResults(processingFile, outputData, gotResult=True):
  filename = os.path.basename(processingFile)
   
  x = filename.split(".")  # file name formate is filename.process_id
  targetPath = DONE_PATH + x[0]
   
  if gotResult:
    with open(targetPath, 'w') as outfile:
      json.dump(outputData, outfile)  
    try:
      os.remove(processingFile)
    except Exception as error:
      print ('Exception remove processing:', error)
  else:
    inputPath = INPUT_PATH + x[0]
    # move back to input file.
    try:
      os.rename(processingFile, inputPath)
    except Exception as error:
      print ('Exception move to input:', error)


def emailLogin(chromeWebDriver) :
  emailList = []
  loginXPath = '/html/body/div[1]/div/div[1]/div/nav/div[3]/ul/li[2]/button/span[2]'
  googleLoginXpath = '/html/body/div[4]/div/div[1]/div/div/div[2]/div/div[2]/div/button[1]'
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
  recovery_email = 'mr456dsdfnv3ertyert6y9@linshiyou.com' #// for testing purpose
  
  #chromeWebDriver.requestUrl('https://accounts.google.com/ServiceLogin')  // for direct google login page
  chromeWebDriver.waitUntil(EC.element_to_be_clickable((By.XPATH, loginXPath)), 30)
  chromeWebDriver.clickElementByXPath(loginXPath)
  chromeWebDriver.waitUntil(EC.element_to_be_clickable((By.XPATH, googleLoginXpath)), 30)

  chromeWebDriver.clickElementByXPath(googleLoginXpath)

  chromeWebDriver.WaitAndtypeCharacterByName('identifier', email, 20)
  chromeWebDriver.WaitAndtypeCharacterByName('Passwd', password, 20)
  recovery_emailXPath = "//*[@id='view_container']/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div/ul/li[3]/div/div[2]"
  chromeWebDriver.waitUntil(EC.presence_of_element_located((By.XPATH, recovery_emailXPath)), 20)
  chromeWebDriver.clickElementByXPath(recovery_emailXPath)
  chromeWebDriver.WaitAndtypeCharacterByName('knowledgePreregisteredEmailResponse', recovery_email, 20)
  print('SCREENSHOT: ', chromeWebDriver.saveScreenshot('gmailLoggedIn', True))

def LoadHomePage(proxy = None):

  if(proxy == None):
    respose = requests.get('http://proxymanager.vindb.org/getnextproxy?key=qulPjrM7f8')
    p = respose.text
    p = p.replace('\"', '')
  else:
    p = proxy

  chromeWebDriver = ChromeWebDriver(PROCESS_NUMBER, p, 3)
  print ('Using Proxy %s' % p)   

  try:
    chromeWebDriver.requestUrl('http://checkip.instantproxies.com')
    time.sleep(1)
    #print('SCREENSHOT: ', chromeWebDriver.saveScreenshot('proxy', True))
    
    #  findValuePath = 
    licenseInputXPath = '//input[@name="license-plate"]'
    # edmunds = https://www.edmunds.com/sell-car/
    chromeWebDriver.requestUrl('https://www.edmunds.com/sell-car',
      EC.visibility_of_element_located((By.XPATH, licenseInputXPath)), 5)
    emailLogin(chromeWebDriver)
    page = chromeWebDriver.getCurrentPage()
    print('SCREENSHOT: ', chromeWebDriver.saveScreenshot('ED-car', True))
#    if page.find('Page timeout') != -1:
#      print('Loaded Time out:', chromeWebDriver.getCurrentPage())
#      print('SCREENSHOT: ', chromeWebDriver.saveScreenshot('load-time-out', True))
#      chromeWebDriver.close()
#      return None
    licenseInput = chromeWebDriver.getElementByXPath(licenseInputXPath)
    if not licenseInput:
#      LogBlockedProxy(p)    
      print('blocked:', chromeWebDriver.getCurrentPage())
      print('SCREENSHOT: ', chromeWebDriver.saveScreenshot('blocked', True))
      chromeWebDriver.close()
      return None
         
    print('Loaded:', chromeWebDriver.getCurrentPage())
    return chromeWebDriver
  except Exception as error: 
    print ('EXCEPTION', error)

def LookupStateName(stateShort):
  lookupMap = {
    "NY": "New York"
  }
  return lookupMap[stateShort]

def SearchLicensePlate(chromeWebDriver, processingFile):
  print ('SearchLicensePlate ' + processingFile)
   # Get plate and state
  plate = 'ASNFLU'
  state = 'CA'
  #proxy = ''
  #with open(processingFile, 'r') as outfile:
  #    y = json.loads(outfile.readline())
  #    plate = y['plate']
  #    state = y['state']

  
  print ('Start searching plate: ' + plate + ' state: ' + state)
  if not plate or not state:
    return
    
  licenseInputXPath = '//input[@name="license-plate"]'
  stateInputXPath = '//select[@name="state-code"]'
  searchXPath = "//button/span[contains(text(),'See your car')]"      
  chromeWebDriver.typeTextByXPath(licenseInputXPath, plate)
  #time.sleep(1)
  chromeWebDriver.typeTextByXPath(stateInputXPath, state)
  print ('Clicking Search')
  chromeWebDriver.clickElementByXPath(searchXPath)  
  print ('Done Clicking Search')

  waitForMultiOptions = "//button[contains(text(),'Continue with this vehicle')]"      
  if chromeWebDriver.waitUntil(EC.presence_of_element_located((By.XPATH, waitForMultiOptions)), 2):
    print('SCREENSHOT: ', chromeWebDriver.saveScreenshot('show-select', True))
    pickXPath = "//button[contains(text(),'Continue with this vehicle')]"      
    chromeWebDriver.clickElementByXPath(pickXPath)
    print('SCREENSHOT: ', chromeWebDriver.saveScreenshot('click-continue-with', True))
    print ('Select One and go to next step')
 
  waitXPath =  '//span[contains(text(), "Find Out")] | //div[contains(text(), "We could not find that license plate")] | //div[contains(text(), "We were unable to locate your license plate")] '
  if not chromeWebDriver.waitUntil(EC.presence_of_element_located((By.XPATH, waitXPath)), 10):
    print('SCREENSHOT: ', chromeWebDriver.saveScreenshot('no result', True))
    return

  print('SCREENSHOT: ', chromeWebDriver.saveScreenshot('ed-result', True))
  currentURL = chromeWebDriver.getCurrentUrl()
  print ('Current Url ', currentURL)

  data = {
      'plate': plate,
      'state': state
  }

  if currentURL == 'https://www.edmunds.com/sell-car/':
    print ('Not Found')
    data['error'] = 'no_data'
    SaveResults(processingFile, data)   
    return

  # Found URL = https://www.edmunds.com/mercedes-benz/c-class/2016/appraisal-value/?vin=WDDWF4KBXGR129955&styleIds=200773063,200773065,200773066
  
  o = urlparse(currentURL)
  if o.path and o.query:
    path = o.path
    makeModelYear = re.match(r'\/([^\/]+)\/(.+)\/(\d{4})\/appraisal-value', path)
    if makeModelYear:
      data['make'] = makeModelYear.group(1)
      data['model'] = makeModelYear.group(2)
      data['year'] = makeModelYear.group(3)
    query = o.query
    vin = re.match(r'vin=(\w{17})', query)
    if vin:
      data['VIN'] = vin.group(1)
      data['vin'] = vin.group(1)
      print ('Saving Data:', data)
      SaveResults(processingFile, data)
      return
   
  print ('Cannot Partse URL', currentURL)
  errorOut = {'error' : ' internal_error'}
  SaveResults(processingFile, errorOut)


processedCount = 0
chromeWebDriver = None




while True:
  TryFreeMemory()
  print ('Enter while loop')
  if processedCount >= MAX_PROCESSED_COUNT:
    print (pid + ' : finished ' + str(processedCount))
    if chromeWebDriver:
      chromeWebDriver.close()
    os._exit(0)

#  if chromeWebDriver:
#    chromeWebDriver.close()
 
  if not chromeWebDriver:
    chromeWebDriver = LoadHomePage()
    if chromeWebDriver:
      print('SCREENSHOT: ', chromeWebDriver.saveScreenshot('load-page', True))

  if not chromeWebDriver:
 #   time.sleep(1)
    continue

  chromeWebDriver.ResetCookie()
 
  # go back to home page
  try:
    currentURL = chromeWebDriver.getCurrentUrl()
    if 'sell-car' in currentURL:
      print ('already at home page:', currentURL)
    else:
      licenseInputXPath = '//input[@name="license-plate"]'
      # edmunds = https://www.edmunds.com/sell-car/
      chromeWebDriver.requestUrl('https://www.edmunds.com/sell-car/',
        EC.visibility_of_element_located((By.XPATH, licenseInputXPath)), 5)
    print ('Reloaded, ready for next search')
  except Exception as error: 
     print ('EXCEPTION', error)
     continue

 
  print('CAMEREREERERE******************') 
  getFileTryCount = 0
  #processingFile = '/home/licensesearch/HDK8663_OH'
  processingFile = r'C:\Users\admin\Downloads\HDK.txt'
  

  if processingFile:
    processedCount = processedCount + 1
    print(processingFile)
    SearchLicensePlate(chromeWebDriver, processingFile)
  print ('Continue to next')



#  time.sleep(1) 
    
#f = getNextFile()
#print (f)
#outputData = {'plate': 'asnflu', 'state': 'ca'}
#    
#SaveResults(f, outputData)

