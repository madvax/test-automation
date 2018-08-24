#!/usr/bin/env python

# This is the Utilities Library.
# This library holds classes and methods for basic utilities within a script.

# ==============================================================================
# STANDARD LIBRARY MPORTS
import os
from   sys           import stdout, stderr, exit, argv
import sys
import time

# ==============================================================================
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
EXIT_SUCCESS  = 0
# ==============================================================================
# Functions

# ------------------------------------------------------------------------------ now()
def _now(format = TIME_FORMAT):
   """ str now() returns a timestamp in the form defined by the 
       TIME_FORMAT variable. You may optionally supply your won format 
       string. See: https://docs.python.org/2/library/time.html        """
   return time.strftime(format, time.localtime()) 


# ------------------------------------------------------------------------------ pause()
def pause(prompt = PAUSE_PROMPT):
    """ pause() --> 0        Holds script execution for user response. Also 
                             takes an optional prompt argument. """
    raw_input(prompt)
    return EXIT_SUCCESS

# ------------------------------------------------------------------------------ showError()
def showError(message):
    """ showError() --> 0    Prints message passed to standard error """
    message = str(message) + os.linesep
    stderr.write("ERROR -- %s" %message)
    stderr.flush()
    return EXIT_SUCCESS

# ------------------------------------------------------------------------------ showWarning()
def showWarning(message):
    """ showWarning() --> 0  Prints message passed to standard error """
    message = str(message) + os.linesep
    stdout.write("WARNING -- %s" %message)
    stderr.flush()
    return EXIT_SUCCESS

# ------------------------------------------------------------------------------ showMessage()
def showMessage(message):
    """ showMessage() --> 0  Prints message passed to standard out """
    message = str(message) + os.linesep
    stdout.write("%s" %message)
    stdout.flush()
    return EXIT_SUCCESS

# ----------------------------------------------------------------------------- configFile2dictionary()
def configFile2dictionary(configFile, delimeter=' '):
   """ configFile2dictionary(configFile) --> {configurations...}
       Given a configuration file, this function returns a dictionary of
       key-value pairs from that file. """
   # TODO: Encrypt the configuration file . . . maybe 
   configurations = {}
   try:
      confFileData = open(configFile, 'r').read()
      for line in confFileData.split('\n'):
         line = line.strip()     # Clean up leading and trailing whitespace
         if len(line) < 1:
            pass                 # Skip blank lines
         elif line[FIRST] == '#':
            pass                 # Skip comment lines
         elif line.find(delimeter) == -1:
            pass                 # Skip mal-formed lines (lines without an equal sign character'=')
         else:
            line  = line.strip() # Clean up the whitespace
            key   = line.split(delimeter, 1)[FIRST].strip()
            value = line.split(delimeter, 1)[LAST].strip()
            configurations[key] = value
   except Exception as e:
      print "Unable to read from configurations file %s" %configFile
      configurations = {} # Trust no one. If there was a problem then flush the data
   return configurations
    
    
# ------------------------------------------------------------------ unitTests()   
def unitTests():
  # --- Unit tests 
  
   testCounter  = 0
   testsPassed  = 0 
   testsFailed  = 0
   testsSkipped = 0
   OK_TO_TEST   = True
   testLogFile  = "testLogFile.txt" 
   
   # ---------------------------------------------------------------
   # Test 1: Get the default timestamp
   testCounter += 1 
   if OK_TO_TEST:
      print "---------------------------------"
      print "Test %d: Get the default timestamp" %testCounter
      try:
         n = _now()
         print n
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
   # Test 2: Get a custom timestamp
   testCounter += 1 
   if OK_TO_TEST:
      print "---------------------------------"
      print "Test %d: Get a custom timestamp" %testCounter
      try:
         n = _now("%Y-%b-%d")
         print n
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
   
    
