"""
Auth: Justin Waldrip
Date: 04/08/2016
Purp: Jython library for interacting with the Essbase Java API
Note: Created for the ability to execute dynamic calculation scripts from FDMEE event scripts
"""

from com.essbase.api.session import IEssbase
from com.essbase.api.domain import IEssDomain
from com.essbase.api.datasource import IEssOlapServer

#Const
ESSBASE_SVR = "localhost:1424"
PROVIDER_SVR = "localhost:19000"
USERNAME = "admin"
PASSWORD = ""

class Essbase(object):
	def __init__(self, username=None, password=None, providerServer=None, essbaseServer=None):
		self.olap = None
		self.cube = None
		self.username = USERNAME if username is None else username
		self.password = PASSWORD if password is None else password
		self.providerUrl = 'http://%(server)s/aps/JAPI' % { 'server': PROVIDER_SVR if providerServer is None else providerServer }
		self.essbaseServer = ESSBASE_SVR if essbaseServer is None else essbaseServer
		#Create JAPI instance
		self.essbase = IEssbase.Home.create(IEssbase.JAPI_VERSION)
		#Sign on to provider services
		self.domain = self.essbase.signOn(self.username, self.password, False, None, self.providerUrl)

	def connect(self, app=None, db=None):
		if app is None or db is None:
			return "Application or database not specified."
		#Open connection to olap server and get cube
		olap = self.domain.getOlapServer(self.essbaseServer)
		olap.connect()
		self.cube = olap.getApplication(app).getCube(db)
		self.olap = olap
		return olap
	
	def disconnect(self):
		if self.essbase == None:
			return "Nothing to disconnect"
		if self.essbase.isSignedOn() == True:
			self.olap.disconnect()
			self.essbase.signOff()
		return "Disconnected"
		
	def start(self):
		self.cube.start()
		
	def stop(self):
		self.cube.stop()
		
	def calculate(self, script=None, dynamic=False, syntaxCheckOnly=False):
		if script == None:
			return False
		
		if dynamic:
			self.cube.calculate(script, syntaxCheckOnly)
			return True
		else:
			self.cube.calculate(syntaxCheckOnly, script)
			return True
