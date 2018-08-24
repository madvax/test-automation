#!/usr/bin/env python
import  subprocess
import  sys
import  os
import  time
from    getopt    import getopt

# ==============================================================================
# DICTIONARY
VERSION       = "1.1.0"     # Version of the agent
DEBUG         = False       # Flag for debug operation
VERBOSE       = False       # Flag for verbose operation 
FIRST         = 0           # first element in a list 
LAST          = -1          # last element in a list
ME            = os.path.split(sys.argv[FIRST])[LAST]        # Name of this file
MY_PATH       = os.path.dirname(os.path.realpath(__file__)) # Path for this file
PAUSE_PROMPT  = "Please press <Enter> to continue ..." 

# ==============================================================================
# Native Methods

# ---------------------------------------------------------------------- usage()
def usage():
   """usage() - Prints the usage message on stdout. """
   print "\n\n%s, Version %s, This library holds the Command class."  %(ME,VERSION)
   print "                                                         "
   print "\nUSAGE: %s [OPTIONS]                                    " %ME
   print "                                                         "
   print "OPTIONS:                                                 "
   print "   -h --help       Display this message.                 "
   print "   -v --verbose    Runs the program in verbose mode, default: %s.        " %VERBOSE
   print "   -d --debug      Runs the program in debug mode (implies verbose)      "
   print "                                                         "
   print "EXIT CODES:                                              "
   print "        0 - Successful Unit Tests.                       "
   print " Non-Zero - One or more unit test failures.              "
   print "                                                         "   
   print "EXAMPLES:                                                " 
   print "    TODO - I'll make some examples up later.             "
   print "                                                         "

# ---------------------------------------------------------------------- pause()
def pause():
   """pause() Holds script execution until the user responds. """
   raw_input(PAUSE_PROMPT)
   return 

# ------------------------------------------------------------------------ now()
def now():
   """now() returns a timestamp string of the form "YYYY-MM-DD, HH:MM:SS"  """
   return time.strftime("%Y-%b-%d, %H:%M:%S", time.localtime())

# ------------------------------------------------------------------ timeStamp()
def timeStamp():
   """ timeStamp() returns a timestamp string of the form "YYYY-MM-DD, HH:MM:SS"  """
   return time.strftime("%Y-%b-%d, %H:%M:%S", time.localtime())

# ------------------------------------------------------------------ showError()
def showError(message):
   """showError(str message) write error message to stderr"""
   message = str(message)
   sys.stderr.write("\n\nERROR -- %s\n\n" %message)
   sys.stderr.flush()
   return 

# ---------------------------------------------------------------- showWarning()
def showWarning(message):
   """showWarning(str message) write error message to stderr"""
   message = str(message)
   sys.stderr.write("\n\nWARNING -- %s\n\n" %message)
   sys.stderr.flush()
   return 

# ---------------------------------------------------------------- showMessage()
def showMessage(message):
   message = str(message)
   sys.stdout.write("\n%s\n" %message)
   sys.stdout.flush()
   return 

# ----------------------------------------------------------------------- main()   
def main():
  # --- Unit tests 
  
   testCounter  = 0
   testsPassed  = 0 
   testsFailed  = 0
   testsSkipped = 0
   OK_TO_TEST   = True

   # ---------------------------------------------------------------
   # Test 1: Crate an object of type Command
   testCounter += 1 
   if OK_TO_TEST:
      print "---------------------------------"
      print "Test %d: Create an object of type Command" %testCounter
      try:
         c = Command("C:\\Python27\Python.exe --version")
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
   # Test 2: Execute the command
   testCounter += 1 
   if OK_TO_TEST:
      print "---------------------------------"
      print "Test %d: Execute the command " %testCounter
      try:
         c.run()
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
   # Test 3: See the results 
   testCounter += 1 
   if OK_TO_TEST:
      print "---------------------------------"
      print "Test %d: See the results " %testCounter
      try:
         c.showResults()
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
   # Test 3: Return the results 
   testCounter += 1 
   if OK_TO_TEST:
      print "---------------------------------"
      print "Test %d: Return the results " %testCounter
      try:
         results = c.returnResults()
         if results["returnCode"] == 0:
            testsPassed += 1
            print "Test %d Passed" %testCounter
         else:
            testsFailed += 1
            print "Test %d Failed" %testCounter
         
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





   
# ==============================================================================
# CLASSES
class Command:
   """ Command() --> Command Object """
   #--------------------------------------------------------- Command.__init__()
   def __init__(self, command):
      """ Creates an instance of an object of type Command. """
      self.command    = str(command).strip()   # The command to execute 
      self._stdout    = subprocess.PIPE        # Standard Output PIPE 
      self._stderr    = subprocess.PIPE        # Standard Error PIPE 
      self.output     = "Command not executed" # Output from command 
      self.error      = "Command not executed" # Error from command
      self.returnCode = 127                    # Default return code from command                
   
   # ------------------------------------------------------------- Command.run()
   def run(self): 
      """ Executes the command in the specified shell. """
      try:
         results = subprocess.Popen(self.command          , 
                                    stdout = self._stdout , 
                                    stderr = self._stderr ,
                                    shell = True          ) # Execute the command 
 
         self.output, self.error = results.communicate()   # Get output and error 
         self.returnCode         = results.returncode      # Get Return Code
      except Exception, e:
         self.output      = str(e) 
         self.error       = "Unable to execute: \"%s\"" %self.command 
         self.returnCode  = 113

   # ----------------------------------------------------- Command.showResults()
   def showResults(self):
      """ Prints original command and resutls to stdout. """
      print "COMMAND     : \"%s\"" %self.command
      print "OUTPUT      : \"%s\"" %self.output.strip()
      print "ERROR       : \"%s\"" %self.error.strip()
      print "RETURN CODE : %d"     %self.returnCode 

   # ---------------------------------------------------- Command.returnResuls()   
   def returnResults(self):
      """ Returns a dictionary containing the original command  and results. """
      results = {"command"    : self.command.strip() ,
                 "output"     : self.output.strip()  ,
                 "error"      : self.error.strip()   ,
                 "returnCode" : self.returnCode      }
      return results    

   
# ==============================================================================      
if __name__ == "__main__":

   try: 
      arguments = getopt(sys.argv[1:]        , 
                         'hvd'               ,
                         ['help'       ,
                          'verbose'    , 
                          'debug'      ]     )   
   except:
      showError("Bad command line argument(s)")
      usage()
      sys.exit(2)         
   # --- Check for a help option
   for arg in arguments[0]:
      if arg[0]== "-h" or arg[0] == "--help":
         usage()
         sys.exit(EXIT_SUCCESS)
   # --- Check for a verbose option
   for arg in arguments[0]:
      if arg[0]== "-v" or arg[0] == "--verbose":
         VERBOSE = True                  
   # --- Check for a debug option
   for arg in arguments[0]:
      if arg[0]== "-d" or arg[0] == "--debug":
         DEBUG   = True
         VERBOSE = True

   # --- Call to main()   
   sys.exit(main())
