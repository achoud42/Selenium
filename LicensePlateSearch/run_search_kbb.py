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
  with open('A.csv') as csv_file:
       csv_reader = csv.reader(csv_file, delimiter=',')
       for row in csv_reader:
           emailList.append(row)
  randomChoice = random.choice(emailList)
  email = randomChoice[0]
  password = randomChoice[1]
  recovery_email = randomChoice[2]
  print(randomChoice)
  
  chromeWebDriver.requestUrl('https://accounts.google.com/ServiceLogin')
  chromeWebDriver.WaitAndtypeCharacterByName('identifier', email, 20)
  chromeWebDriver.WaitAndtypeCharacterByName('Passwd', password, 20)
  recovery_emailXPath = "//*[@id='view_container']/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div/ul/li[3]/div/div[2]"
  chromeWebDriver.waitUntil(EC.presence_of_element_located((By.XPATH, recovery_emailXPath)), 20)
  chromeWebDriver.clickElementByXPath(recovery_emailXPath)
  chromeWebDriver.WaitAndtypeCharacterByName('knowledgePreregisteredEmailResponse', recovery_email, 20)
  time.sleep(5)
  print('SCREENSHOT: ', chromeWebDriver.saveScreenshot('gmailLoggedIn', True))


def LoadHomePage():
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
    proxy = '196.51.175.134:8800'
    chromeWebDriver = ChromeWebDriver(PROCESS_NUMBER, proxy,9)
    print ('Using Proxy %s' % proxy)
    print('***************************PROXY*******************************')
    print(proxy)
    print('******************************************************')

  
    chromeWebDriver.requestUrl('http://checkip.instantproxies.com')
    time.sleep(1)
    print('SCREENSHOT: ', chromeWebDriver.saveScreenshot('proxy', True))
    #emailLogin(chromeWebDriver)
    #chromeWebDriver.openNewTab()
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
    return chromeWebDriver
  except Exception as error: 
     print ('EXCEPTION', error)


def SearchLicensePlate(chromeWebDriver, processingFile):
  print ('SearchLicensePlate ' + processingFile)
   
  plate = '952GDH'
  state = 'MN'
  #plate, state = random.choice(list(Dict.items()))


  #with open(processingFile, 'r') as outfile:
  #    y = json.loads(outfile.readline())
  #    plate = y['plate']
  #    state = y['state']
  
  print ('Start searching plate: ' + plate + ' state: ' + state)

  if not plate or not state:
    return
  print("Started entrying data ") 

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

  #LicenceLabelXPath = '//div[text()="License Plate"]'
  #vinXpath ='//*[@id="BodyDivFlex"]/div[2]/div/div[1]/div'
  vinXpath = '//div[@class="css-90uzj3 edyetg22"]'
  
  time.sleep(10)
  data = {}
  expectedURL = '/ico/v1/plate2vin/lookup?stateCode='+ state +'&plateNumber='+plate 
  #+ '&api_key=kehj9w5vxkt4t8yugn5zkpey'
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
    #SaveResults(processingFile, data)
   
    


  

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


