# see systemctl status supervisord 
# killall python3
# killall chromedriver

#https://selenium-python.readthedocs.io/waits.html
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
#from chromeWebDriver import chromeWebDriver
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
import requests

import csv
import random



if len(sys.argv) < 2:
  print('Usage: python3 run_search.py [process_number]')
#  exit()

PROCESS_NUMBER = int(sys.argv[1].strip())
print ('run_search.py : ', PROCESS_NUMBER)

MAX_PROCESSED_COUNT = 10

INPUT_PATH = os.path.dirname(os.path.abspath(__file__)) + '/DATA/input/'
PROCESS_PATH = os.path.dirname(os.path.abspath(__file__)) + '/DATA/processing/'
DONE_PATH = os.path.dirname(os.path.abspath(__file__)) + '/DATA/done/'
LOG_PATH =  os.path.dirname(os.path.abspath(__file__)) + '/DATA/logs/'

pid = str(os.getpid())

import os
import psutil


Dict = {}
with open(r'C:\Users\admin\Downloads\plate.tsv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter='\t')
    line_count = 0
    for row in csv_reader:
        Dict[row[2]] = row[3]  

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
  #emailList = []
  #with open('A.csv') as csv_file:
  #     csv_reader = csv.reader(csv_file, delimiter=',')
  #     for row in csv_reader:
  #         emailList.append(row)
  #randomChoice = random.choice(emailList)
  #email = randomChoice[0]
  #password = randomChoice[1]
  #recovery_email = randomChoice[2]
  #print(randomChoice)
  email = 'imd82915@gmail.com' # replace email
  password = '44EvF4Aelc95YBbvU4' # replace password
  recovery_email = 'dWhgYJGPENTN@outlook.com'
  chromeWebDriver.requestUrl('https://accounts.google.com/ServiceLogin')
  chromeWebDriver.WaitAndtypeCharacterByName('identifier', email, 20)
  chromeWebDriver.WaitAndtypeCharacterByName('Passwd', password, 20)
  recovery_emailXPath = "//*[@id='view_container']/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div/ul/li[3]/div/div[2]"
  chromeWebDriver.waitUntil(EC.presence_of_element_located((By.XPATH, recovery_emailXPath)), 20)
  chromeWebDriver.clickElementByXPath(recovery_emailXPath)
  chromeWebDriver.WaitAndtypeCharacterByName('knowledgePreregisteredEmailResponse', recovery_email, 20)
  time.sleep(5)
  print('SCREENSHOT: ', chromeWebDriver.saveScreenshot('gmailLoggedIn', True))

def LoadHomePage(proxy = None):
  proxy = None
  counter = 0
  while(proxy == None and counter < 3):
    try:
      respose = requests.get('http://pxymgr.vindb.org/getnextproxy?key=qulPjrM7f8&source=cf')
      p = respose.text
      proxy = p
      counter = counter + 1
    except Exception as ex:
      counter = counter + 1
      print(ex)

  try:
    #proxy = '196.51.175.134:8800'
    chromeWebDriver = ChromeWebDriver(PROCESS_NUMBER, proxy, 0)
    print('SELECTED PROXY::::', proxy)
    chromeWebDriver.requestUrl('http://checkip.instantproxies.com')
    time.sleep(1)
    print('SCREENSHOT: ', chromeWebDriver.saveScreenshot('proxy', True))
    licenseInputXPath = '//input[@name="plate"]'
    chromeWebDriver.requestUrl('https://www.cargurus.com/sell-car/',
      EC.visibility_of_element_located((By.XPATH, licenseInputXPath)), 5)
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

def SearchLicensePlate(chromeWebDriver, processingFile):
  print ('SearchLicensePlate ' + processingFile)
   
  plate = 'ASNFLU'
  state = 'CA'
  #plate, state = random.choice(list(Dict.items()))


  #with open(processingFile, 'r') as outfile:
  #    y = json.loads(outfile.readline())
  #    plate = y['plate']
  #    state = y['state']
  
  print ('Start searching plate: ' + plate + ' state: ' + state)

  if not plate or not state:
    return
    
  licenseInputXPath = '//*[@id="vinOrPlate"]'
  stateInputXPath = '//*[@id="state"]'

  
  #searchXPath = '//*[@id="root"]/div[1]/header/form/fieldset/button/div'
  searchXPath = '/html/body/main/div[1]/header/form/fieldset/button/div'
  errorXPath = '//*[@id="root"]/div[1]/header/form/fieldset/div[2]/div[1]/label/span[2]/span'
  #//*[@id="root"]/div[1]/header/form/fieldset/div[2]/div[1]/label/span[2]/span
  #/html/body/main/div[1]/header/form/fieldset/div[2]/div[1]/label/span[2]/span
  vinXpath= '//*[@id="root"]/div[1]/div[2]/aside/div/section[1]/ul/li[1]/p[2]'   
  print("Started entrying data ")   
  chromeWebDriver.typeCharacterByXPath(licenseInputXPath, plate)

  chromeWebDriver.typeTextByXPath(stateInputXPath, state)
  chromeWebDriver.clickElementByXPath(searchXPath)  
  print("clicked on GET STARTED")
  try :
    waitXPath =  '//*[@id="enter-vin"]/div/h2/span'
    chromeWebDriver.waitUntil(EC.presence_of_element_located((By.XPATH, waitXPath)), 30)
    data ={}
    vin_element = chromeWebDriver.getElementByXPath(vinXpath).text
    if vin_element:
        vin = vin_element.text
        print(vin)
        data['VIN'] = vin

    data['plate'] = plate
    data['state'] = state
    
    print (data)
    SaveResults(processingFile, data)
  except Exception as e:
      data['plate'] = plate
      data['state'] = state
      data['error'] = 'Capctha_Block'
      #pm = ProxyManager()
      #pm.markProxyBad(chromeWebDriver.proxy)
      errorOut = {'error' : 'permission_denied'}
      #SaveResults(processingFile, errorOut, False)    
      #chromeWebDriver.close()
      print(data)
      os._exit(0)
    


  

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


 
  if not chromeWebDriver:
    chromeWebDriver = LoadHomePage()
    if chromeWebDriver:
      print('SCREENSHOT: ', chromeWebDriver.saveScreenshot('load-page', True))

  if not chromeWebDriver:
 #   time.sleep(1)
    continue
  print('BEFORE *******************************************************');
    
  chromeWebDriver.ResetCookie()
  print('AFTER **********************************************************');
 
  # go back to home page
  try:
    print ('Going back to home page')
    licenseInputXPath = '//input[@name="plate"]'
    chromeWebDriver.requestUrl('https://www.cargurus.com/sell-car/',
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

  print('CAMEREREERERE******************') 
  getFileTryCount = 0
  #processingFile = '/home/licensesearch/HDK8663_OH'
  processingFile = r'C:\Users\admin\Downloads\HDK.txt'
  #processingFile = None
  

  if processingFile:
    processedCount = processedCount + 1
    print(processingFile)
    SearchLicensePlate(chromeWebDriver, processingFile)
  print ('Continue to next')


