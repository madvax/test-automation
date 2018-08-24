#!/usr/bin/env python
"""
This is the library for using Telnet sessions in your Python applications.
It is specificaly tailored for using telnet to access an Access Point.
 
"""


"""
REVISION HISTORY
|     Name    |     Date    |        Revision                                  | 
|=============|=============|==================================================|
|  H. Wilson  | 2015-Jan-13 | Version 1.0.0 - Initial Script                   |
|-------------+-------------+--------------------------------------------------|
|  H. Wilson  | 2017-Nov-07 | Version 1.2.0 - ported to DD-WRT Telent          |
|             |             |                                                  |
|-------------+-------------+--------------------------------------------------|
|             |             |                                                  |
|-------------+-------------+--------------------------------------------------|
|             |             |                                                  |
|===============================================================================
"""

# ==============================================================================
# STANDARD LIBRARY IMPORTS

from    telnetlib import Telnet
import  time 
import  sys
import  os
from    getopt    import getopt

# ==============================================================================
# DICTIONARY
VERSION       = "1.2.0"  # Version of the library
DEBUG         = False    # Flag for debug operation
VERBOSE       = False    # Flag for verbose operation 
FIRST         = 0        # first element in a list 
LAST          = -1       # last element in a list
ME            = os.path.split(sys.argv[FIRST])[LAST]        # Name of this file
MY_PATH       = os.path.dirname(os.path.realpath(__file__)) # Path for this file
EXIT_SUCCESS  = 0         
# ==============================================================================
# CLASSES         
         
class TelnetSession:
   """ TelnetSession - Provides a custome telnet session object for telnet 
       control of the Wireless AP. It assuems that you have telnet enabled
       on your router and that you can establish a TCP connection.  """
       
   # --------------------------------------------------------------------------- TelnetSession.__init__()
   def __init__(self                                              , 
                ipAddress      = "192.168.1.1"                    , 
                user           = "root"                           , 
                password       = "testtest"                       , 
                userPrompt     = "login:"                         , 
                passwordPrompt = "Password:"                      ,  
                cmdPrompt      = "#"                              ,
                timeout        = 30                               ,                   
                portNumber     = 23                               ):
      self.userName   = user              # Username for the Telnet Connection 
      self.password   = password          # Password for the Telnet Connection 
      self.ipAddress  = ipAddress         # IP Address for the Telnet Server 
      self.port       = portNumber        # Port number for the Telnet Server 
      self.routerVer  = "4.4.23"          # Router OS Version number:" "uname -r"      
      self.connected  = False             # True if connected to Telnet Server 
      self.session    = None              # When connected, holds an abject of type Telnet Session 
      self.userPrompt = userPrompt        # Telnet Server's Username prompt
      self.passPrompt = passwordPrompt    # Telnet Server's Password prompt
      self.cmdPrompt  = cmdPrompt         # Telnet Server's command prompt 
      self.timeout    = timeout           # Time in seconds to wait before giving up on comms.
      self.loginEOL   = '\n'              # Telnet Server's login end-of-line character
      self.commandEOL = '\n'              # Telnet Server's command end-of-line character
      self.DEBUG      = False             # Set to True for DEBUG operation
      # self._connect()
      
   # --------------------------------------------------------------------------- TelnetSession._sendLogin()      
   def _sendLogin(self, message):
      message +=  self.loginEOL
      self.session.write(message)

   # --------------------------------------------------------------------------- TelnetSession._sendCommand()      
   def _sendCommand(self, message):
      if self.DEBUG: print "TelnetSession._sendCommand(\"%s\")" % message
      message +=  self.commandEOL
      self.session.write(message)
      if self.DEBUG: print "TelnetSession._sendCommand() returning"      
      
   # --------------------------------------------------------------------------- TelnetSession.connect()            
   def connect(self):
      try:
         if self.DEBUG: print "TelnetSession.connect() --> Connecting ..."
         if self.DEBUG: print "   -- Connecting to %s" %self.ipAddress
         self.session = Telnet(self.ipAddress)
         self.session.read_until(self.userPrompt, self.timeout)
         if self.DEBUG: print "   -- Sending Username %s" %self.userName         
         self._sendLogin(self.userName)
         self.session.read_until(self.passPrompt, self.timeout)
         if self.DEBUG: print "   -- Sending Password ********"         
         self._sendLogin(self.password)
         if self.DEBUG: print "   -- Looking for prompt \'%s\'" %self.cmdPrompt                  
         self.session.read_until(self.cmdPrompt, self.timeout)
         if self.DEBUG: print "   -- Get router OS version string"
         routerVersion  = self.send("uname -r")
         if self.DEBUG: print "   -- Comparing: \'%s\' \'%s\'" %(routerVersion, self.routerVer )
         if routerVersion == self.routerVer:
            if self.DEBUG: print "TelnetSession.connect() --> CONNECTED !"
            self.connected = True 
      except Exception as e:
         print "TelnetSession.connect() error"
         print e         

   # --------------------------------------------------------------------------- TelnetSession.close()      
   def close(self):
      try:
         self.session.close()
         self.connecte = False
      except Exceptions as e:
         print "TelnetSession.close() error, Unable to close connection"
         print e
         
   # --------------------------------------------------------------------------- TelnetSession.send()      
   def send(self, message):
      """ Sends a message to the Telnet server and returns the response.
          The original command, the new prompt, and any leading or trailing 
          whitespace is removed from the response. 
          Note: Uses helper function self._sendCommand() to format the message 
                for the Telnet server.                                       """
      response = ""
      if message == "exit" or message == "quit":
         self.close()
      else:   
         self._sendCommand(message)
         response = self.session.read_until(self.cmdPrompt, self.timeout)
         #
         # The response buffer holds the original command, a new line, the 
         # response, and the new command prompt. The actual response needs to 
         # have the original command and the new command prompt stripped off. 
         response = response.split('\n', 1)[LAST]    # strip original command
         response = response.rsplit('\n', 1)[FIRST]  # strip new prompt  
         response = response.strip()                 # final clean up
      return response

   # --------------------------------------------------------------------------- TelnetSession.showParams()      
   def showParams(self):
      returnValue = True
      try:
         print "Telnet Server Parameters"
         print "IP Address      %s" % self.ipAddress
         print "Username        %s" % self.userName      
         print "Password        %s" % self.password   
         print "Port            %d" % self.port   
         print "Username Prompt %s" % self.userPrompt
         print "Password Prompt %s" % self.passPrompt 
         print "Command Prompt  %s" % self.cmdPrompt  
         print "Timeout         %d" % self.timeout 
      except Exception as e:
         print "TelnetSession.showParams() error"
         print e
         returnValue = False
      return returnValue
      
      
      
# ==============================================================================
# Native Methods

# ---------------------------------------------------------------------- usage()
def usage():
   """usage() - Prints the usage message on stdout. """
   print "\n\n%s, Version %s, Library for using a Telnet Session   "  %(ME,VERSION)
   print "                             Gateway to support automated testing.  "
   print "\nUSAGE: %s [OPTIONS]                                    " %ME
   print "                                                         "
   print "OPTIONS:                                                 "
   print "   -h --help    Display this message.                 "
   print "   -v --verbose Runs the program in verbose mode, default: %s.   " %VERBOSE
   print "   -d --debug   Runs the program in debug mode (implies verbose) "
   print "                                                         "
   print "EXIT CODES:                                              "
   print "    0        -   All Unit Tests passed                   "
   print "    Non-Zero - One or more Unit Tests failed             "
   print "                                                         " 
   print "EXAMPLES:                                                " 
   print "    TODO - I'll make some examples up later.             "
   print "                                                         "

# ----------------------------------------------------------------------- main()   
def main():
   
   # --- Unit tests 
  
   testCounter  = 0
   testsPassed  = 0 
   testsFailed  = 0
   testsSkipped = 0
   OK_TO_TEST   = True
   
   # ---------------------------------------------------------------
   # Test 1: Default connection
   testCounter += 1 
   if OK_TO_TEST:
      print "---------------------------------"
      print "Test %d: Default connection" %testCounter
      print "connecting to default Telnet Server ..."
      try:
         tns        =  TelnetSession()
         tns.DEBUG  = True
         tns.connect()
         if not tns.connected: 
            raise ValueError, "Not connected to Telnet Server"
         else:
            print "Test %d: PASSED" %testCounter
            testsPassed += 1
      except Exception as e:
         print "Test %d: FAILED" %testCounter
         testsFailed += 1
         OK_TO_TEST = False            
   else:
      print "Test %d: Skipped" %testCounter
      testsSkipped += 1
      
   # ---------------------------------------------------------------
   # Test 2: Connection Parameters
   testCounter += 1 
   if OK_TO_TEST:
      print "---------------------------------"
      print "Test %d: Connection Parameters" %testCounter
      try:
         passed = tns.showParams()
         if not passed: 
            raise ValueError, "Problem with Telnet Server parameters"
         else:
            print "Test %d: PASSED" %testCounter
            testsPassed += 1
      except Exception as e:
         print "Test %d: FAILED" %testCounter
         testsFailed += 1
         OK_TO_TEST = False            
   else:
      print "Test %d: Skipped" %testCounter
      testsSkipped += 1
      
   # ---------------------------------------------------------------
   # Test 3: Try a help command
   testCounter += 1 
   if OK_TO_TEST:
      print "---------------------------------"
      print "Test %d: Try a 'wl ver' command " %testCounter
      print "connecting to default Telnet Server ..."
      try:
         answer = ""
         answer = tns.send("wl ver")
         if len(answer) == 0: 
            raise ValueError, "The 'wl ver' command returned nothing ??? "
         else:
            print answer
            print "Test %d: PASSED" %testCounter
            testsPassed += 1
      except Exception as e:
         print "Test %d: FAILED" %testCounter
         testsFailed += 1    
   else:
      print "Test %s: Skipped" %testCounter
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
if __name__ == "__main__":




   # Parse the command Line 
   ssidSet = False # Flag to see if we need to calcualte the ssid or did the user provide one.
   try: 
      arguments = getopt(sys.argv[1:]        , 
                         'hvda:u:p:c:b:s:k'  ,
                         ['help'       ,
                          'verbose'    , 
                          'debug'      , 
                          'kill'       ]     )   
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
