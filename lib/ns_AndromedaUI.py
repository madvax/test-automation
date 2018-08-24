#!/usr/bin/env python

# This is the Andromeda UI .
# This library holds classes and methods for basic utilities within a script.

# =============================================================================
# STANDARD LIBRARY MPORTS
import os
from   sys           import stdout, stderr, exit, argv
import sys
import time

# =============================================================================
# DICTIONARY
VERSION       = "1.0.0"              # Version for this library
DEBUG         = False                # Flag for debug operation
VERBOSE       = False                # Flag for verbose operation
LOGGING       = True                 # Flag for logging
FIRST         = 0                    # First list index
LAST          = -1                   # Last list index
ME            = os.path.split(sys.argv[FIRST])[LAST]        # Name of this file
MY_PATH       = os.path.dirname(os.path.realpath(__file__)) # Path to this file
TIME_FORMAT   = "%Y-%b-%d, %H:%M:%S"                        # Format for date time stamp
PAUSE_PROMPT  = "Press <Enter> to continue."                # Default pause prompt
SERIAL_NUMBER = 'emulator-5554' # Serial number of the Android device
DELAY         = 3
EXIT_SUCCESS  = 0

# =============================================================================
# === Import uiautomator library
try:
   os.environ['ANDROID_HOME']
except:
   os.environ['ANDROID_HOME'] = '/home/test/Android/Sdk'
from uiautomator import Device


# =============================================================================
# Generic I/O and Support Functions
# ----------------------------------------------------------------------------- now()
def _now(format = TIME_FORMAT):
   """ str now() returns a timestamp in the form defined by the 
       TIME_FORMAT variable. You may optionally supply your won format 
       string. See: https://docs.python.org/2/library/time.html        """
   return time.strftime(format, time.localtime()) 

# ----------------------------------------------------------------------------- delay()
def delay(secondsToDelay = DELAY):
    time.sleep(secondsToDelay)
    return EXIT_SUCCESS


# =============================================================================
# Andromeda UI Widget functions 
# ----------------------------------------------------------------------------- navDrawerWidgets()
def navDrawerWidgets(activeDevice):
  """ navDrawer(activeDevice) --> Dictionary of Naviation Drawer top-level objects 
                                  referenced by text."""
  widgetDirectory   = {}
  resource_id_text  = "com.netscout.andromedaprototype:id/text_view"
  class_name_text   = "android.widget.TextView"
  topLevelItems     = ["AutoTest", "Device Discovery", "Network Map", "Wi-Fi Analysis", "Traffic Analysis", "Tools", "Settings", "Help"]
  wifiAnalysisItems = ["Channel Map", "Channels", "Networks", "Access Points", "Clients", "Interferers"]
  toolsItems        = ["Path Analysis", "Network Performance", "Capture", "Spectrum", "Other Troubleshooting", "File Manager", "Export Logs", "Browser", "TELNET/SSH"]
  settingsItems     = ["Profile", "Developer"]  
  fullListItems     = [topLevelItems, wifiAnalysisItems, toolsItems, settingsItems ] 

  for widgetList in fullListItems:
     for item in widgetList: 
        # print "   Adding %s ... " %item,
        widgetDirectory[item] = activeDevice(textStartsWith = item             ,
                                             resourceId     = resource_id_text ,
                                             className      = class_name_text  )
        # print "done."   
  return widgetDirectory

# ----------------------------------------------------------------------------- get_navDrawerIcon()
def get_navDrawerIcon(activeDevice):
   """ navDrawer(activeDevice) --> Andromeda Navigation Drawer Icon Widget reference """
   returnMe = None
   try:
      returnMe = activeDevice(className="android.widget.ImageButton", description="Navigate up")
   except:
      print "ERROR -- %s Unalbe to loacte the Navigation Drawer Icon" %ME
   return returnMe

    
# ----------------------------------------------------------------------------- get_webBrowser()
def get_webBrowser(activeDevice):
   """ get_webBrowser(activeDevice) --> Android Chrome Web Browser reference """
   returnMe = None
   try:
      returnMe = activeDevice(className   = "android.widget.FrameLayout"              , 
                              resourceId  = "com.android.chrome:id/toolbar_container" ,
                              packageName = "com.android.chrome"                      )
   except:
      print "ERROR -- %s Unalbe to loacte the Chrome Web Browser" %ME
   return returnMe


# ----------------------------------------------------------------------------- pressAutotestLeftFAM()
def pressAutotestLeftFAM(activeDevice):
   """ pressAutotestLeftFAM(activeDevice) --> None  
       uses x,y coordinates to press the left side FAM on the Autotest Screen."""
   x = 700 
   y = 1070
   activeDevice.click(x,y)
   return None

# ----------------------------------------------------------------------------- pressAutotestRightFAM()
def pressAutotestRightFAM(activeDevice):
   """ pressAutotestRightFAM(activeDevice) --> None  
       uses x,y coordinates to press the right side FAM on the Autotest Screen."""
   x = 1850 
   y = 1070
   activeDevice.click(x,y)
   return None
    
# ----------------------------------------------------------------------------- unitTests()   
def unitTests():
  # --- Unit tests 
  
   testCounter  = 0
   testsPassed  = 0 
   testsFailed  = 0
   testsSkipped = 0
   OK_TO_TEST   = True
   testLogFile  = "testLogFile.txt" 
   
   
   # ---------------------------------------------------------------
   # Test 1: Connect to Android Device
   testCounter += 1 
   if OK_TO_TEST:
      print "---------------------------------"
      print "Test %d: Connect to Android Device" %testCounter
      try:
         print "Connecting to Android Device \"%s\"" %SERIAL_NUMBER
         testDevice  = Device(SERIAL_NUMBER)
         print "CONNECTED to \"%s\" !" %SERIAL_NUMBER
         print testDevice.info 
         testsPassed += 1
         print "Test %d Passed" %testCounter
      except Exception as e:
         print "Test %d: FAILED" %testCounter
         print e
         testsFailed += 1
         OK_TO_TEST = False            
   else:
      print "Test %d: Skipped" %testCounter
      testsSkipped += 1      



   # ---------------------------------------------------------------
   # Test 2: Get the Andromeda Main Menu Buttons
   testCounter += 1 
   if OK_TO_TEST:
      print "---------------------------------"
      print "Test %d: Get the Andromeda Main Menu Buttons" %testCounter
      try:
         print "Opening Nav Drawer"
         navDrawer = testDevice(className = "android.widget.ImageButton", description = "Navigate up")
         navDrawer.click()
         print "Nav Drawer opened" 
         delay()
         print "Calling navDrawerWidgets()"
         nd =  navDrawerWidgets(testDevice) 
         print "Found:"
         print nd.keys()
         missingCounter = 0
         for button in nd.keys():
            print "   Checking %s" %button
            if nd[button].exists:
               print "   %s exists" %button
            else:
               print "   %s MISSING" %button
               missingCounter += 1
         if missingCounter == 0:  
            testsPassed += 1
            print "Test %d Passed" %testCounter
         else: 
            raise ValueError('%d Nav Drawer Widgets missing' %missingCounter)          
      except Exception as e:
         print "Test %d: FAILED" %testCounter
         print e
         testsFailed += 1
         OK_TO_TEST = False            
   else:
      print "Test %d: Skipped" %testCounter
      testsSkipped += 1      
      


   # ---------------------------------------------------------------
   # Test 2: Test the last widget in the lsit 
   testCounter += 1 
   if OK_TO_TEST:
      print "---------------------------------"
      print "Test %d: Test the last button the list, the 'help' button." %testCounter
      try:
         widgetText = 'Help' 
         print "Selecting the '%s' button" %widgetText
         nd[widgetText].click()
         delay()
         print "Checking '%s' page title" %widgetText
         helpPageTitle = testDevice(textStartsWith = widgetText                                        , 
                                    resourceId     = "com.netscout.andromedaprototype:id/titleTextView",
                                    className      = "android.widget.TextView"                         )
         if helpPageTitle.exists:
            print "   %s button passed" %widgetText
            testsPassed += 1
            print "Test %d Passed" %testCounter
            testDevice.press.back()
            delay() 
         else:
            print "   %s vutton FAILED" %helpPageTitle
            raise ValueError('%s button failed to navigate to the %s page'%(widgetText,widgetText) )          
      except Exception as e:
         print "Test %d: FAILED" %testCounter
         print e
         testsFailed += 1
         OK_TO_TEST = False            
   else:
      print "Test %d: Skipped" %testCounter
      testsSkipped += 1      

      
   
   print "=================="   
   print " Unit Test Report "
   print "=================="
   print ""
   print "Tests          = %d" %testCounter 
   print "Tests Passed   = %d" %testsPassed
   print "Tests Failed   = %d" %testsFailed
   print "Tests Skipped  = %d" %testsSkipped
 
 
   if testCounter == testsPassed:
      print "All Unit Tests passed"
      returnValue = 0
   else:
      returnValue = testsFailed + testsSkipped
   return returnValue              

   
   
   
if __name__ == "__main__":
    print "Executing Unit Tests ..." 
    unitTests()
    print "Unit Tests Complete"
    sys.exit(0)
else:
    pass
   
    
