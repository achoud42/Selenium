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
  emailList = []
  loginXPath = '//*[@id="nav-secondary"]/div[3]/div/div[2]/button/span'
  googleLoginXpath = '//*[@id="modalContent"]/section/button[1]'
  #C:\Users\admin\Downloads\2023-gaccounts (3).csv
  with open(r'C:\Users\admin\Downloads\2023-gaccounts(3).csv') as csv_file:
       csv_reader = csv.reader(csv_file, delimiter=',')
       for row in csv_reader:
           emailList.append(row)
  randomChoice = random.choice(emailList)
  email = randomChoice[0]
  password = randomChoice[1]
  recovery_email = randomChoice[2]
  print(randomChoice)
  email = 'ejfgyfjgfhfrjjfhyfxg@gmail.com' # replace email
  password = 'FJZ8mIlpf7NLWGj' # replace password
  recovery_email = 'mr456dsdfnv3ertyert6y9@linshiyou.com'
  
  chromeWebDriver.requestUrl('https://accounts.google.com/ServiceLogin')
  #chromeWebDriver.waitUntil(EC.presence_of_element_located((By.XPATH, loginXPath)), 10)
  #chromeWebDriver.clickElementByXPath(loginXPath)
  #chromeWebDriver.waitUntil(EC.presence_of_element_located((By.XPATH, googleLoginXpath)), 30)

  #chromeWebDriver.clickElementByXPath(googleLoginXpath)

  chromeWebDriver.WaitAndtypeCharacterByName('identifier', email, 20)
  chromeWebDriver.WaitAndtypeCharacterByName('Passwd', password, 20)
  recovery_emailXPath = "//*[@id='view_container']/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div/ul/li[3]/div/div[2]"
  chromeWebDriver.waitUntil(EC.presence_of_element_located((By.XPATH, recovery_emailXPath)), 20)
  chromeWebDriver.clickElementByXPath(recovery_emailXPath)
  chromeWebDriver.WaitAndtypeCharacterByName('knowledgePreregisteredEmailResponse', recovery_email, 20)
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
    licenseInputXPath = '//*[@id="plateNumberInput"]'
    chromeWebDriver.requestUrl("https://www.driveway.com/sell-your-car/",
      EC.visibility_of_element_located((By.XPATH, licenseInputXPath)), 10)
    #emailLogin(chromeWebDriver)
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

def SearchLicensePlate( ):
  #print ('SearchLicensePlate ' + processingFile)
   
  plate = 'RTC0093'
  state = 'WY'
  #plate, state = random.choice(list(Dict.items()))


  #with open(processingFile, 'r') as outfile:
  #    y = json.loads(outfile.readline())
  #    plate = y['plate']
  #    state = y['state']
  
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
    responseText = chromeWebDriver.getXhrReponse(expectedURL)
    print(responseText)
    #print(responseText['vin'])

    if(noResult) :
      data['VIN'] = 'no_data'
      data['plate'] = plate
      data['state'] = state
      print (data)
      chromeWebDriver.close()
      return data
    #SaveResults(processingFile, data)
    else :
      data['VIN'] = responseText['vin']
      data['plate'] = plate
      data['state'] = state
      chromeWebDriver.close()
      return data
  except :
    data['VIN'] = 'no_data'
    data['plate'] = plate
    data['state'] = state
    print (data)
    chromeWebDriver.close()
    return data

  #chromeWebDriver.close()
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
  #try:
  #  print ('Going back to home page')
  #  licenseInputXPath = '//*[@id="plateNumberInput"]'
  #  chromeWebDriver.requestUrl("https://www.driveway.com/sell-your-car/",
  #    EC.visibility_of_element_located((By.XPATH, licenseInputXPath)), 10)
  #  page = chromeWebDriver.getCurrentPage()
  #  if page.find('Page timeout') != -1:
  #    print('ReLoaded Time out:', chromeWebDriver.getCurrentPage())
  #    chromeWebDriver.close()
  #    chromeWebDriver = None
  #    continue
  #  print('ReLoaded:', chromeWebDriver.getCurrentPage())
  #except Exception as error: 
  #   print ('EXCEPTION', error)
  #   continue

  print('CAMEREREERERE******************') 
  getFileTryCount = 0
  #processingFile = '/home/licensesearch/HDK8663_OH'
  processingFile = r'C:\Users\admin\Downloads\HDK.txt'
  #processingFile = None
  

  if processingFile:
    processedCount = processedCount + 1
    print(processingFile)
    SearchLicensePlate()
  #chromeWebDriver.close
  chromeWebDriver = None
  print ('Continue to next')


