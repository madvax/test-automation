#!/usr/bin/env python

# ==============================================================================
# This script executes test cases listed in a test suite file and tracks the 
# test case execution results. Made for Seyem Arslan on the occasion of her 
# appointment as "Survey in the Cloud" Test Automation Engineer.  
#
# Harold Wilson, April 2016 

# STANDARD LIBRARY IMPORTS =====================================================
import sys
import os
import time 
from thread import start_new_thread # Used for treaded testcase execution
from subprocess import Popen        # Used for Help functions, see showHelp()

# SITE PACKAGE IMPORTS =========================================================
try: 
   from PyQt4.QtCore import pyqtSignal, SIGNAL, QRect, QSize
   from PyQt4.QtGui  import QApplication, QMainWindow, qApp 
   from PyQt4.QtGui  import QAction, QMenu, QIcon, QTextCursor 
   from PyQt4.QtGui  import QMessageBox, QFileDialog, QFont
   from PyQt4.QtGui  import QGridLayout, QWidget, QTextEdit, QStatusBar
   from PyQt4.QtGui  import QTabWidget, QColor, QPalette, QPixmap
   from PyQt4.QtGui  import QSplashScreen
   from PyQt4.Qt     import *
except:
   sys.stderr.write("\nERROR -- Unable to import PyQt4 from the site library")
   sys.stderr.write("\n         You can download the PyQt4 library from:")
   sys.stderr.write("\n         http://qt.nokia.com/downloads")
   sys.stderr.flush()
   sys.exit(1)

# SCRIPT GLOBALS ===============================================================   
VERSION        = "1.0.0"                                     # Version for this library
DEBUG          = False                                       # Flag for debug operation
VERBOSE        = True                                        # Flag for verbose operation
LOGGING        = True                                        # Flag for logging
FIRST          = 0                                           # First list index
LAST           = -1                                          # Last list index
ME             = os.path.split(sys.argv[FIRST])[LAST]        # Name of this file
MY_PATH        = os.path.dirname(os.path.realpath(__file__)) # Path for this file
LIBRARY_PATH   = os.path.join(MY_PATH, "lib")                # relative Library path 
RESOURCE_PATH  = os.path.join(MY_PATH, "res")                # relative Resource path 
CONFIG_FILE    = os.path.join(MY_PATH, "testmaster.conf")    # Config file from testmaster
PYTHON_INTERPRETER = sys.executable

# CUSTOM LIBRARY IMPORTS =======================================================
sys.path.append(LIBRARY_PATH) # Add custom library path to the Python Path
try:
   import  am_Command
   # print "%s Successfully loaded the am_Command library, version %s" %(ME, am_Command.VERSION)
except Exception as e: 
   print "%s ERROR -- Unable to import the am_Command library" %ME
   print e
   sys.exit(2)
   
# ==============================================================================   
# ============================================================================== MainWindow
# ==============================================================================
class MainWindow(QMainWindow):
   """ MainWindow(QMainWindow) This is the class/object for the main window 
       of the GUI application. This main window and GUI applicaiton are a Single
       Document Interface (SDI) Application. """

   # ---------------------------------------------------------------------------
   def __init__(self, parent = None):  
      """ MainWindow constructor  """         
   
      # Text messages for the class are set here 
      self.genericMsg = "WARNING -- Your changes have NOT been saved.\nAre you sure you want to %s\nand lose all of your changes?"
      self.quit_msg   = self.genericMsg %"exit the program"   
      self.new_msg    = self.genericMsg %"start a new file"   
      self.open_msg   = self.genericMsg %"open a new file"   
      self.close_msg  = self.genericMsg %"close this file"
      
      self.testcases       = [] # \
      self.testsuitefolder = "" #  \__ Start with a clean slate.
      
      # Read the confuration file data into the local class namespace as the
      # class will need this information.  
      try:
         self.configs = {}
         self.configs = configFile2dictionary(CONFIG_FILE)
         # print self.configs 
         if len(self.configs) == 0:
            raise Exception ("Failed to read configurations from \"%s\"" %CONFIG_FILE)
         self.configs['testcasefolder'] = os.path.join(MY_PATH, self.configs['testcasefolder'])
         self.configs['resultshome']  = os.path.join(MY_PATH, self.configs['resultshome'])
      except Exception as e:
         # TODO: SHow this as a message box as well
         print e
         print "Using default configurations"
         self.configs['testcasefolder'] = "/tmp/testcases"
         self.configs['resultshome']  = "/var/www/html/results"
        
      # Call to the Super Class for QT MainWindow
      super(MainWindow, self).__init__() # Don't ask, just do it.

      # Set up a way to write to the Console Area in from a separate thread. This 
      # allows for real-time output to the consoleArea.   
      self.consoleMessage   = pyqtSignal(str)
      self.connect(self, SIGNAL("self.consoleMessage"), self.updateConsole)
      
      # Set up a way to write to the Debug Area from a separate thread. This 
      # allows for real-time output to the consoleArea.   
      self.debugMessage   = pyqtSignal(str)
      self.connect(self, SIGNAL("self.debugMessage"), self.updateDebug)
            
      # Set up a way to write to the Results Area from a separate thread. This 
      # allows for real-time output to the resultsArea.   
      self.resultsMessage   = pyqtSignal(str)
      self.connect(self, SIGNAL("self.resultsMessage"), self.updateResults)      

      # The Steps for creating the main windows
      self.create_menubarActions()
      self.create_menubar()
      self.create_toolbarActions()
      self.create_toolbar()
      self.createWidgets()
      self.paint_mainWindow()
      self.setState(0) # This needs fixed, see setState()
     
   # ---------------------------------------------------------------------------   
   def create_menubarActions(self):
      # 
      # Create the menubar actions that will server as the link between 
      # menubar items and function calls. NOTE: Every 'triggered' argument 
      # must point to a valid function.  
      
      # File Menu Actions  - - - - - - - - - - - - - - - - - - - - - - - - - - - 
      self.mbExit   = QAction( "E&xit",    self, shortcut="Alt+E", statusTip="Exit the application",  triggered=self.cleanExit)       
      self.mbNew    = QAction( "N&ew",     self, shortcut="Alt+N", statusTip="Create a new file",     triggered=self.newFile)      
      self.mbOpen   = QAction( "O&pen",    self, shortcut="Alt+O", statusTip="Open an existing file", triggered=self.openFile)
      self.mbClose  = QAction( "C&lose",   self, shortcut="Alt+C", statusTip="Close a file",          triggered=self.closeFile)
      self.mbSave   = QAction( "S&ave",    self, shortcut="Alt+S", statusTip="Save the  file",        triggered=self.saveFile)
      self.mbSaveAs = QAction( "Save A&s", self, shortcut="Alt+A", statusTip="Save a file as",        triggered=self.saveAsFile)
      
      # Script Menu Actions  - - - - - - - - - - - - - - - - - - - - - - - - - - 
      self.mbRun   = QAction( "R&un",  self, shortcut="Alt+R", statusTip="Run the loaded file",       triggered=self.runScript)
      self.mbStop  = QAction( "S&top", self, shortcut="Alt+S", statusTip="Stop script execution ",    triggered=self.stopScript) 
      self.mbDebug = QAction( "D&ebug",self, shortcut="Alt+D", statusTip="Debug the loaded file",     triggered=self.debugScript)
      
      # Help Menu Actions   -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
      self.mbHelp  = QAction( "H&elp",  self, shortcut="Alt+H", statusTip="Display help",             triggered=self.showHelp) 
      self.mbAbout = QAction( "A&bout", self, shortcut="Alt+A", statusTip="About This program",       triggered=self.showAbout)    
   
   
   # ---------------------------------------------------------------------------
   def create_toolbarActions(self):
      # Create the actions for the toolbar. Status tips and shortcut keys for 
      # the toolbar components are defined here. NOTE: Every 'triggered' 
      # connection must point to a valid function.   
      self.tbExit = QAction(QIcon(os.path.join(RESOURCE_PATH, 'Exit.png')), 'Exit', self)
      self.tbExit.setShortcut('Ctrl+Q')
      self.tbExit.setStatusTip('Exit application')
      self.tbExit.triggered.connect(self.cleanExit)
      
      self.tbNew = QAction(QIcon(os.path.join(RESOURCE_PATH, 'New.png')), 'New', self)
      self.tbNew.setShortcut('Ctrl+N')
      self.tbNew.setStatusTip('Start a new file')
      self.tbNew.triggered.connect(self.newFile)

      self.tbOpen = QAction(QIcon(os.path.join(RESOURCE_PATH, 'Open.png')), 'Open', self)
      self.tbOpen.setShortcut('Ctrl+O')
      self.tbOpen.setStatusTip('Open an existing file')
      self.tbOpen.triggered.connect(self.openFile)

      self.tbSave = QAction(QIcon(os.path.join(RESOURCE_PATH, 'Save.png')), 'Save', self)
      self.tbSave.setShortcut('Ctrl+S')
      self.tbSave.setStatusTip('Save to a file ')
      self.tbSave.triggered.connect(self.saveFile)

      self.tbRun = QAction(QIcon(os.path.join(RESOURCE_PATH, 'Run.png')), 'Run', self)
      self.tbRun.setShortcut('Ctrl+R')
      self.tbRun.setStatusTip('Run the loaded script')
      self.tbRun.triggered.connect(self.runScript)

      self.tbStop = QAction(QIcon(os.path.join(RESOURCE_PATH, 'Stop.png')), 'Stop', self)
      self.tbStop.setShortcut('Ctrl+S')
      self.tbStop.setStatusTip('Stop script execution')
      self.tbStop.triggered.connect(self.stopScript)
      
      self.tbDebug = QAction(QIcon(os.path.join(RESOURCE_PATH, 'Debug.png')), 'Debug', self)
      self.tbDebug.setShortcut('Ctrl+D')
      self.tbDebug.setStatusTip('Debug script')
      self.tbDebug.triggered.connect(self.debugScript)

      self.tbInfo = QAction(QIcon(os.path.join(RESOURCE_PATH, 'Info.png')), 'Info', self)
      self.tbInfo.setShortcut('Ctrl+O')
      self.tbInfo.setStatusTip('Info About this program')
      self.tbInfo.triggered.connect(self.showAbout)

      self.tbHelp = QAction(QIcon(os.path.join(RESOURCE_PATH, 'Help.png')), 'Help', self)
      self.tbHelp.setShortcut('Ctrl+H')
      self.tbHelp.setStatusTip('Help using this program')
      self.tbHelp.triggered.connect(self.showHelp)
   
   # ---------------------------------------------------------------------------
   def create_toolbar(self):   
      self.toolbar = self.addToolBar('Main')
      self.toolbar.addAction(self.tbOpen)
      self.toolbar.addAction(self.tbNew)      
      self.toolbar.addAction(self.tbSave)
      self.toolbar.addAction(self.tbExit)
      self.toolbar.addSeparator()  # -------------
      self.toolbar.addAction(self.tbRun)
      self.toolbar.addAction(self.tbStop)
      self.toolbar.addAction(self.tbDebug)
      self.toolbar.addSeparator() # --------------       
      self.toolbar.addAction(self.tbHelp)
      self.toolbar.setIconSize(QSize(50,50))

   # ---------------------------------------------------------------------------
   def create_menubar(self): 
      # Create File Menu
      self.fileMenu = QMenu("&File")
      self.fileMenu.addAction(self.mbNew)      
      self.fileMenu.addAction(self.mbOpen)
      self.fileMenu.addSeparator()
      self.fileMenu.addAction(self.mbSave)  
      self.fileMenu.addAction(self.mbSaveAs)  
      self.fileMenu.addSeparator()
      self.fileMenu.addAction(self.mbClose) 
      self.fileMenu.addAction(self.mbExit)
      # Create Script Menu 
      self.scriptMenu = QMenu("&Script")
      self.scriptMenu.addAction(self.mbRun)
      self.scriptMenu.addAction(self.mbStop)
      self.scriptMenu.addAction(self.mbDebug)
      # Create Help Menu
      self.helpMenu = QMenu("&Help")
      self.helpMenu.addAction(self.mbHelp)
      self.helpMenu.addAction(self.mbAbout)
      # Add menus to menubar
      menubar = self.menuBar()
      menubar.addMenu(self.fileMenu)
      menubar.addMenu(self.scriptMenu)
      menubar.addMenu(self.helpMenu)

   # ---------------------------------------------------------------------------   
   def createWidgets(self):
      # Create the widgets used in the main window and other parts of the script.
      
      # --- Text Area ----
      self.textArea = QTextEdit()                     # Text editor
      self.textArea.setFont(QFont("Courier", 14))     # Keepin' it simple

      # -- Console Area ---
      self.consoleArea = QTextEdit()                  # Console Area 
      consolePalette = QPalette()                     # A bit more complex
      bgColor = QColor(0, 0, 0)                       #   Green Text with  
      txColor = QColor(0, 255, 0)                     #   Black background 
      consolePalette.setColor(QPalette.Base, bgColor) # 
      consolePalette.setColor(QPalette.Text, txColor) # 
      self.consoleArea.setPalette(consolePalette)     # 
      self.consoleArea.setFont(QFont("Courier", 14))  # Font name and size
      self.consoleArea.setReadOnly(True)              # Read only  

      # --- Debug Area ---
      self.debugArea = QTextEdit()                    # Debug Area
      debugPalette = QPalette()                       # Palette for area
      bgColor = QColor(0, 0, 0)                       # Black Background 
      debugPalette.setColor(QPalette.Base, bgColor)   #
      txColor = QColor(255, 0, 0)                     # Red Text
      debugPalette.setColor(QPalette.Text, txColor)   #
      self.debugArea.setPalette(debugPalette)         #
      self.debugArea.setFont(QFont("Courier", 14))    # Font name and size
      self.debugArea.setReadOnly(True)                # Read only
   
      # --- Results Area ---
      self.resultsArea = QTextEdit()                  # Results Area
      consolePalette = QPalette()                     # A bit more complex
      bgColor = QColor(0, 0, 0)                       #   White Text with  
      txColor = QColor(255, 255, 255)                 #   Black background 
      consolePalette.setColor(QPalette.Base, bgColor) # 
      consolePalette.setColor(QPalette.Text, txColor) # 
      self.resultsArea.setPalette(consolePalette)     # 
      self.resultsArea.setFont(QFont("Courier", 10))  # Font name and size
      self.resultsArea.setReadOnly(True)              # Read only  
      
      # --- Tab Area ---  
      self.tabs = QTabWidget()                       # Tabs
      self.tabs.addTab(self.consoleArea, 'Console')  # Add Console Area tab 
      self.tabs.addTab(self.debugArea,   'Debug'  )  # Add Debug Area tab
      self.tabs.addTab(self.resultsArea, 'Results')  # Add Results Area tab
      # TODO: Change the tab indexes to meaningful words not just 0,1,2
      self.tabs.setTabIcon(0, QIcon(os.path.join(RESOURCE_PATH, "Run.png"     ))) # Add Icon to tab  
      self.tabs.setTabIcon(1, QIcon(os.path.join(RESOURCE_PATH, "Debug.png"   ))) # Add Icon to tab
      self.tabs.setTabIcon(2, QIcon(os.path.join(RESOURCE_PATH, "results.png" ))) # Add Icon to tab
      self.tabs.setIconSize(QSize(30,30))
      self.tabs.setTabShape(QTabWidget.Triangular)   # Set tab shape
   
   # ---------------------------------------------------------------------------
   def paint_mainWindow(self):
         
      # Define and use a "Grid Layout" for the main window.
      grid = QGridLayout()
      grid.addWidget(self.textArea, 1, 1)
      grid.addWidget(self.tabs,     2, 1)
      
      # Create central widget, add layout, and set
      central_widget = QWidget()
      central_widget.setLayout(grid)
      self.setCentralWidget(central_widget)      
      
      # Fun feature for users. If you are going to have a toolbar then you 
      # really need this status bar to show what the icons do.        
      self.statusbar = QStatusBar(self) 
      self.statusbar.setObjectName( "statusbar") 
      MainWindow.setStatusBar(self, self.statusbar) 
      self.statusbar.show()
      
      # Initial settings for the main window 
      #
      #    Set the Main Window Geometry
      top    =  100 # Main Window initial 'top' position (as pixels from top of screen)
      left   =  100 # Main Window initial 'left' position (as pixels from left side of screen)
      width  = 1000 # Main Window initial 'width' (as pixels)
      height =  700 # Main Window initial 'height' (as pixels)
      self.setGeometry(QRect(top, left, width, height))  
 
      # Create connection(s)
      #    If the contents of the text area are changed then call a function 
      #    to set the appropriate file menu state. This file menu state can 
      #    also be used to ensure clean exits. In english, keep track 
      #    of changes to the text editor. It affects the "state" of the
      #    application. See setState()
      self.connect(self.textArea, SIGNAL("textChanged()"), self.textChanged)

  # ---------------------------------------------------------------------------      
   def cleanExit(self): 
      # Provides an "ARE YOU SURE" method for clean exits.
      if self.state == 2: # See setState()
         reply = QMessageBox.question(self, 'Message', self.quit_msg, QMessageBox.Yes, QMessageBox.No)
         if reply == QMessageBox.Yes:
            qApp.quit()
         else:
            pass
      else:   
         qApp.quit()
         
   # ---------------------------------------------------------------------------      
   def newFile(self): 
      # Start a new file. However, if a file is already open AND has not been 
      # saved, then we prompt the user before starting a new file. 
      # Remember, we are implementing SDI behavior, google it.   
      if self.state == 2:
         reply = QMessageBox.question(self, 'Message', self.new_msg, QMessageBox.Yes, QMessageBox.No)
         if reply == QMessageBox.Yes:
            self.textArea.clear()
            self.consoleArea.clear()
            self.debugArea.clear()
            self.resultsArea.clear()
            self.inputFile = ''
            self.setState(1)
            self.updateDebug("New File Started")
         else:
            self.updateDebug("New File Aborted")
      else:   
         self.textArea.clear()
         self.consoleArea.clear()
         self.debugArea.clear()
         self.resultsArea.clear()
         self.inputFile = '' 
         self.setState(1)
         self.updateDebug("New File Started")

   #----------------------------------------------------------------------------
   def openFile(self): 
      # Open a new file. However, if a file is already open AND has not been 
      # saved, then we prompt the user before opening a new file. 
      # Remember, we are implementing SDI behavior, google it.   
      if self.state == 2:
         reply = QMessageBox.question(self, 'Message', self.open_msg, QMessageBox.Yes, QMessageBox.No)
         if reply == QMessageBox.Yes:
            self.textArea.clear()
            self.consoleArea.clear()
            self.debugArea.clear()
            self.resultsArea.clear()
            self.inputFile = ''
            self.setState(1)
            # Let's go ahead and load the file.
            self.loadScript() 
         else:
            self.updateDebug("Open File aborted")
      else:   
         self.inputFile = QFileDialog.getOpenFileName(self, 'Open File', '.')
         fname = open(self.inputFile)
         data = fname.read()
         self.textArea.clear()
         self.consoleArea.clear()
         self.debugArea.clear()
         self.resultsArea.clear()
         self.textArea.setText(data)
         fname.close() 
         self.setState(1)
         # Let's go ahead and load the file.
         self.loadScript()       
      
   # ---------------------------------------------------------------------------      
   def closeFile(self): 
      # Close the open file and return to the initial/unopened state.
      # A clean exit has been implemented 
      if self.state == 2:
         reply = QMessageBox.question(self, 'Message', self.close_msg, QMessageBox.Yes, QMessageBox.No)
         if reply == QMessageBox.Yes:
            self.textArea.clear()
            self.consoleArea.clear()
            self.debugArea.clear()
            self.resultsArea.clear()
            self.inputFile = ""
            self.setState(0)
         else:
            self.updateDebug("Close File aborted")
      else:   
         self.textArea.clear()
         self.consoleArea.clear()
         self.debugArea.clear()
         self.resultsArea.clear()
         self.inputFile = ""
         self.setState(0)

   # ---------------------------------------------------------------------------               
   def saveFile(self): 
      # save the contents of text editor to a file
      if self.inputFile == "":
         self.saveAsFile()   
      else:
         if len(self.inputFile) > 0:
            filePointer = open(self.inputFile, 'w')
            filePointer.write(self.textArea.toPlainText())
            filePointer.close()
            self.setState(1) # Set initial menu state
            self.loadScript()
         else:
            # TODO: Add message box warning here
            pass         
   
   # ---------------------------------------------------------------------------      
   def saveAsFile(self): 
      # save the contents of text editor to a file
      filename = ""      
      filename = QFileDialog.getSaveFileName(self, 
                                             'Save File', 
                                             self.inputFile)
      if len(filename) > 0:
         filePointer = open(filename, 'w')
         filePointer.write(self.textArea.toPlainText())
         filePointer.close()
         self.inputFile = filename # Set to the new file name
         self.setState(1) # Set initial menu state
         self.loadScript()          
      else:
         # TODO: Add message box warning here
         pass      


   # ---------------------------------------------------------------------------
   def checkScript(self):
      """ Checks to see if the loaded script "test suite" is valid. Returns the 
          number of errors found in the script "test suite".  
          A valid script "test suite" has noting but:
            - Comment lines, starting with '#' 
            - Blank lines, contain nothing but white space
            - Filename lines, lines with the name of testcase filenames
      
         Anything else is considered an error. We also take the liberty of 
         verfying that all files (testcases) listed actually exist. Non-existant
         testcases are also errors. The details of this check are listed in the 
         debug tab of the main window.
      """
      errorCount     = 0 
      self.testcases = []
      self.updateDebug("Checking... ") 
      lines = self.textArea.toPlainText().split('\n')
      lineNumber = 0
      for line in lines:
         lineNumber += 1
         line = str(line)
         line = line.strip()
         if len(line) > 0:
            if line[FIRST] != '#':
               if os.path.exists(line): 
                  self.updateDebug("Console line %d: OK." %lineNumber)
                  self.testcases.append(line)
               else:
                  self.updateDebug("Console line %d: Unable to find test case \"%s\"." %(lineNumber, line))
                  errorCount += 1
            else:
               self.updateDebug("Console line %d: Skipped as comment." %lineNumber)            
         else:
            self.updateDebug("Console line %d: Skipped as whitespace." %lineNumber)
         lineNumber = lineNumber +1         
      self.updateDebug("Checked, found %d Error(s)" %errorCount )
      return errorCount
      
   # ---------------------------------------------------------------------------
   def loadScript(self):
      self.updateDebug("Loading \"%s\"" %self.inputFile)
      errors = self.checkScript()
      if errors == 0:
         self.consoleArea.clear() 
         self.debugArea.clear() 
         self.resultsArea.clear() 
         self.setState(4) 
         self.updateDebug("Loaded \"%s\""   %self.inputFile)
         self.updateConsole("Loaded \"%s\"" %self.inputFile)         
      else: 
         msg = "This script has errors and cannot be executed.\n"
         msg +=  "\nSee the Debug Tab for details."
         QMessageBox.critical(self, "Script Error", msg, QMessageBox.Ok) 
         self.setState(3) 
         self.updateConsole("Failed to load \"%s\"\nSee Debug tab for details." %self.inputFile)

   # ---------------------------------------------------------------------------      
   def threadedExecution(self, threadBuffer):
      """ This is the threaded execution of the test cases. While in this 
          thread/function please only use "self.emit(SIGNAL, message)" for  
          outputs to the tabs (console, debug, and results). Any other attempt 
          to update the tabs will raise an unhandled tread exception. 
      """
      try:
         self.setState(5) # Runing test
         
         # Entered Threaded Execution
         message = "Executing %d testcases" %len(self.testcases)
         self.emit(SIGNAL("self.consoleMessage"),  message)
         self.emit(SIGNAL("self.debugMessage"  ),  message)
         
         # For Results Report
         reportTime = time.strftime("%A, %B %d, %Y (%H:%M:%S)", time.localtime())
         message = """
Test Report for test suite: %s %s 

Test Cases in Suite:\n""" %(self.inputFile ,reportTime)
         counter = 0                                        # 
         for t in self.testcases:                           # Add a neatly 
            counter = counter + 1                           # printed list 
            message = message + "  %2d %s\n" %(counter, t)  # of test cases        

         message = message + """

Results Detailed in: %s
         
Results Summary: """ %self.testsuitefolder 

         self.emit(SIGNAL("self.resultsMessage"),  message)
         
         
         # Loop through each of the test cases and create subfolders for each 
         # testcase as we go                  
         testcaseCounter    = 0
         numberOfTestcases  = len(self.testcases)
         for testcase in self.testcases:
            
            # Loop/testcase Counter 
            testcaseCounter += 1
            
            # Initial Testcase Message 
            message = "Starting testcase %d of %d %s" %(testcaseCounter, numberOfTestcases, testcase)
            self.emit(SIGNAL("self.consoleMessage"),  message)
            self.emit(SIGNAL("self.debugMessage"  ),  message)
             
            # Create the folder for the testcase 
            testcasename = os.path.split(testcase)[LAST].split('.')[FIRST]
            testcasefolder = os.path.join(self.testsuitefolder, testcasename)
            message = "Creating testcase folder: %s" % testcasefolder
            self.emit(SIGNAL("self.debugMessage"  ),  message)            
            # TODO: Put this make folder in a try/except block
            os.mkdir(testcasefolder)
            message = "Created testcase folder: %s" % testcasefolder
            self.emit(SIGNAL("self.debugMessage"  ),  message)            

            # Execute the test case.
            message = "Executing: %s" % testcase
            self.emit(SIGNAL("self.consoleMessage"),  message)
            self.emit(SIGNAL("self.debugMessage"  ),  message)

            # *** ******************* ***
            # *** TEST CASE EXECUTION ***
            # *** ******************* ***
            c = am_Command.Command("%s %s " %(testcase, testcasefolder))
            c.run()



            testcaseResults = c.returnResults()
            message = "   Command:\n%s\n   Output:\n%s\n   Errors: \n%s\n   Return: %s\n" %(testcaseResults["command"]   ,
                                                                                            testcaseResults["output"]    ,
                                                                                            testcaseResults["error"]     ,
                                                                                            testcaseResults["returnCode"])           
            self.emit(SIGNAL("self.debugMessage"  ),  message)
               
            if testcaseResults['returnCode'] == 0: 
               message = "Testcase %s PASSED" %testcasename
            else:
               message = "Testcase %s FAILED" %testcasename
            self.emit(SIGNAL("self.consoleMessage"),  message)
            self.emit(SIGNAL("self.debugMessage"  ),  message)
            self.emit(SIGNAL("self.resultsMessage"),  message)      

            # Write the output and error files to the testcase folder
            # TODO: Put these file writes in try/except blocks            
            if len(testcaseResults['output']) > 0:
               message = "Writing output file to testcase folder %s" %testcasefolder
               self.emit(SIGNAL("self.debugMessage"  ),  message)               
               f = open(os.path.join(testcasefolder,"output.txt"), 'w')
               f.write(testcaseResults['output'])
               f.close()
            if len(testcaseResults['error']) > 0:
               message = "Writing error file to testcase folder %s" %testcasefolder
               self.emit(SIGNAL("self.debugMessage"  ),  message)
               f = open(os.path.join(testcasefolder, "errors.txt"), 'w')
               f.write(testcaseResults['error'])
               f.close()                  
            
            # Final Message for this testcase      
            message = "Completed  testcase %d of %d" %(testcaseCounter, numberOfTestcases)
            self.emit(SIGNAL("self.consoleMessage"),  message)
            self.emit(SIGNAL("self.debugMessage"  ),  message)


         # We are now out of the loop and done with all testcase executions.   
         message = "Testcase execution complete, see Results tab for details." 
         self.emit(SIGNAL("self.consoleMessage"),  message)
         self.emit(SIGNAL("self.debugMessage"  ),  message)
         
         # Report Footer
         message = "--- END OF REPORT ---"
         self.emit(SIGNAL("self.resultsMessage"),  message)            
         
         # Show the Results tab when the test suite is fnished.
         time.sleep(3)                 # Wait for the buffer. It may take a few 
         self.tabs.setCurrentIndex(2)  # secons to write the last message to the 
         #                             # tab's text area. 
         
         # Write the report to the "report.txt" file in the test suite results 
         # folder 
         # TODO: Put this file write in a try/except block.
         summaryReportFilename = os.path.join(self.testsuitefolder, "SummaryRepot.txt")
         f = open(summaryReportFilename, 'w')
         f.write(self.resultsArea.toPlainText())
         f.close()
         
         self.setState(7) # Finished test case executions 
      
      except Exception as e:
         print e
      
   # ---------------------------------------------------------------------------
   def runScript(self):
      """ Wrapper for the threaded execution. """
      
      # Make sure we have a results home foldder
      message = "Checking results home folder"
      self.updateDebug(message)
      if not os.path.exists(self.configs['resultshome']):
         message = "Creating Results home: %s" %self.configs['resultshome'] 
         self.updateDebug(message)
         try:
            os.mkdir(resultsHome)
            message = "Created Results home: %s" %self.configs['resultshome'] 
            self.updateDebug(message)
         except:
            message = "Unable to create the Results Home folder.\n%s" % self.configs['resultshome'] 
            self.updateDebug(message)
            QMessageBox.critical(self, "Script Error", message, QMessageBox.Ok) 
            self.setState(3)
            return 
      else:
         message = "Results home using: %s" %self.configs['resultshome'] 
         self.updateDebug(message)
      
      # Create the test suite folder using a timestamp.
      timestamp = time.strftime("%Y%m%d-%H%M%S", time.localtime())
      if os.path.exists(self.configs['resultshome']):
         try: 
            self.testsuitefolder = os.path.join( self.configs['resultshome'], timestamp)
            message = "Creating Test Suite Folder: %s" %self.testsuitefolder             
            self.updateDebug(message)
            os.mkdir(self.testsuitefolder)
            message = "Created Test Suite Folder: %s" %self.testsuitefolder             
            self.updateDebug(message)
         except:
            message = "Unable to create the Test Suite folder.\n%s" % self.testsuitefolder 
            self.updateDebug(message)
            QMessageBox.critical(self, "Script Error", message, QMessageBox.Ok) 
            self.setState(3)
            return 
            
      # Spawn the execution thread. Execution is threaded so that the console 
      # and debug tabs can be updated in real time.  
      start_new_thread(self.threadedExecution, (self,))   
      
   # --------------------------------------------------------------------------
   def stopScript(): 
      pass # TODO: Write this function
   # --------------------------------------------------------------------------
   def debugScript():
      pass # TODO: Write this function
   # --------------------------------------------------------------------------
   def showHelp(self): 
      Popen(["/usr/bin/gedit", "readme.txt"], shell=True)

   # --------------------------------------------------------------------------
   def textChanged(self): 
      # Set the file menu state to indicate unsaved changes to text.
      self.setState(2)      
   
   # ---------------------------------------------------------------------------
   def updateConsole(self, message):
      # Updates the console area
      consoleText = self.consoleArea.toPlainText()
      # consoleText += "\n"
      consoleText += "%s\n" %str(message)
      self.consoleArea.setText(consoleText)
      self.consoleArea.moveCursor(QTextCursor.End)

   # ---------------------------------------------------------------------------
   def updateDebug(self, message):
      # Updates the debug area 
      debugText = self.debugArea.toPlainText()
      # consoleText += "\n"
      debugText += "%s\n" %str(message)
      self.debugArea.setText(debugText)
      self.debugArea.moveCursor(QTextCursor.End)

   # ---------------------------------------------------------------------------
   def updateResults(self, message):
      # Updates the results area
      consoleText = self.resultsArea.toPlainText()
      # consoleText += "\n"
      consoleText += "%s\n" %str(message)
      self.resultsArea.setText(consoleText)
      self.resultsArea.moveCursor(QTextCursor.End)
     
   # ---------------------------------------------------------------------------               
   def showAbout(self): 
      # Shows the about box
      aboutTitle = "About %s" %ME
      aboutText  = "Test Case Runner\n%s, Version %s\nNETSCOUT, April 2016\n\nFor support contact:\nharold.wlison@netscout.com"%(ME, VERSION)
      QMessageBox.about(self, aboutTitle, aboutText)
      
   # --------------------------------------------------------------------------   
   def textChanged(self): 
      # Set the file menu state to indicate unsaved changes to text.
      self.setState(2)         
      
   # ---------------------------------------------------------------------------
   def setState(self, state):
      # ------------------------------------------------------------------------
      # ************************* STATE MACHINE MANAGEMENT *********************   
      # ------------------------------------------------------------------------
      # The state of the program determines what menubar items or toolbar 
      # buttons are active or even visible. Additionally, some method behavior 
      # may also vary depending on the state of the program. The states are 
      # listed below:
      # 
      #    State 0 : The program is started but no file or editor session is 
      #               opened.
      #    State 1 : A file or text editor session is opened but the text is 
      #              unchanged since last save.
      #    State 2 : A file or text editor session is opened and the text has 
      #              changed since the last save.
      #    State 3 : The text in the editor has errors and cannot be executed.
      #    State 4 : The text in the editor has no errors.
      #    State 5 : The text in the editor is being executed. 
      #    State 6 : The text in the editor has been stopped before execution has 
      #              completed.
      #    State 7 : The text in the editor has successfully completed.
      #    State 8 : The text in the editor has terminated with errors.
      self.state = state  
      if self.state == 0:
         self.mbExit.setEnabled(True)      
         self.mbNew.setEnabled(True) 
         self.mbOpen.setEnabled(True)
         self.mbClose.setEnabled(False)
         self.mbSave.setEnabled(False)
         self.mbSaveAs.setEnabled(False)
         self.mbRun.setEnabled(False)
         self.mbStop.setEnabled(False)   
         self.mbDebug.setEnabled(False)
         self.tbOpen.setEnabled(True)
         self.tbNew.setEnabled(True) 
         self.tbSave.setEnabled(False)
         self.tbExit.setEnabled(True)
         self.tbRun.setEnabled(False)
         self.tbStop.setEnabled(False)
         self.tbDebug.setEnabled(False) 
         self.textArea.setVisible(False)
         self.tabs.setVisible(False)
      elif self.state == 1:
         self.mbExit.setEnabled(True)      
         self.mbNew.setEnabled(True) 
         self.mbOpen.setEnabled(True)
         self.mbClose.setEnabled(True)
         self.mbSave.setEnabled(False)
         self.mbSaveAs.setEnabled(False)
         self.mbRun.setEnabled(True)
         self.mbStop.setEnabled(False)   
         self.mbDebug.setEnabled(True)
         self.tbOpen.setEnabled(True)
         self.tbNew.setEnabled(True) 
         self.tbSave.setEnabled(False)
         self.tbExit.setEnabled(True)
         self.tbRun.setEnabled(True)
         self.tbStop.setEnabled(False)
         self.tbDebug.setEnabled(True) 
         self.textArea.setVisible(True)
         self.tabs.setVisible(True)
         # self.consoleArea.setVisible(True)
         # self.debugArea.setVisible(True)
      elif self.state == 2:
         self.mbExit.setEnabled(True)      
         self.mbNew.setEnabled(True) 
         self.mbOpen.setEnabled(True)
         self.mbClose.setEnabled(True)
         self.mbSave.setEnabled(True)
         self.mbSaveAs.setEnabled(True)
         self.mbRun.setEnabled(True)
         self.mbStop.setEnabled(False)   
         self.mbDebug.setEnabled(True)
         self.tbOpen.setEnabled(True)
         self.tbNew.setEnabled(True) 
         self.tbSave.setEnabled(True)
         self.tbExit.setEnabled(True)
         self.tbRun.setEnabled(True)
         self.tbStop.setEnabled(False)
         self.tbDebug.setEnabled(True) 
         self.textArea.setVisible(True)
         self.tabs.setVisible(True)
      elif self.state == 3:
         self.mbRun.setEnabled(False)
         self.mbStop.setEnabled(False)   
         self.mbDebug.setEnabled(True)
         self.tbRun.setEnabled(False)
         self.tbStop.setEnabled(False)
         self.tbDebug.setEnabled(True) 
      elif self.state == 4:
         pass
      elif self.state == 5:
         self.mbRun.setEnabled(False)
         self.mbStop.setEnabled(True)   
         self.mbDebug.setEnabled(False)
         self.tbRun.setEnabled(False)
         self.tbStop.setEnabled(True)
         self.tbDebug.setEnabled(False) 
      elif self.state == 6:
         self.mbRun.setEnabled(True)
         self.mbStop.setEnabled(False)   
         self.mbDebug.setEnabled(True)
         self.tbRun.setEnabled(True)
         self.tbStop.setEnabled(False)
         self.tbDebug.setEnabled(True)
      elif self.state == 7:
         self.mbRun.setEnabled(True)
         self.mbStop.setEnabled(False)   
         self.mbDebug.setEnabled(True)
         self.tbRun.setEnabled(True)
         self.tbStop.setEnabled(False)
         self.tbDebug.setEnabled(True)
      elif self.state == 8:
         self.mbRun.setEnabled(True)
         self.mbStop.setEnabled(False)   
         self.mbDebug.setEnabled(True)
         self.tbRun.setEnabled(True)
         self.tbStop.setEnabled(False)
         self.tbDebug.setEnabled(True)
      else:
         pass
      return  
 
# ------------------------------------------------------------------------------ configFile2dictionary()
def configFile2dictionary(configFile, delimeter=' '):
   """ configFile2dictionary(configFile) --> {configurations...}
       Given a configuration file, this function returns a dictionary of
       key-value pairs from that file. """
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
   
# ==============================================================================
def main():
   """ Starts the Main Window Interface  """
   app = QApplication(sys.argv)
   app.setWindowIcon(QIcon(os.path.join(RESOURCE_PATH, "manager.ico"))) 

   start       = time.time()                               # Start timer for splash screen                                   
   splashImage = os.path.join(RESOURCE_PATH, "splash.jpg") # Define splash image 
   pixmap      = QPixmap(splashImage)                      # Create a pixmap object
   splash      = QSplashScreen(pixmap)                     # Create a splash screen object
   # This "splash.setMask()" is usefull if the splashscreen is not a regular 
   # ractangle. This is also the reason we created a separate object of type 
   # pixmap.
   # splash.setMask(pixmap.mask())                         # Accomodate odd shapes  
   splash.show()                                           # Show splash screen
   splash.showMessage((u'%s, Version %s Starting...' %(ME, VERSION)), Qt.AlignLeft | Qt.AlignBottom, Qt.black)
   # make sure Qt really display the splash screen 
   while time.time() - start < 3: # \
      time.sleep(0.001)           #  > Timer for splash screen.
      app.processEvents()         # /
   mainWin = MainWindow()         # Create object of type "MainWindow"
   splash.finish(mainWin)         # kill the splashscreen   

   mainWin.setGeometry(100, 100, 1000, 700) # Initial window position and size
   mainWin.setWindowTitle(ME)               # Initial Window title
   mainWin.show()                           # Abracadabra "POOF!"
   sys.exit(app.exec_())                    # Handles all clean exits 

# ==============================================================================
if __name__ == "__main__":
   main()

