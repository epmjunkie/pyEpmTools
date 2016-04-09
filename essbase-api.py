"""
Auth: Justin Waldrip
Date: 04/08/2016
Purp: Custom library for interacting with the Essbase Java API
Note: Created out of a need for the ability to execute dynamic calculation scripts
"""

from com.essbase.api.session import IEssbase
from com.essbase.api.domain import IEssDomain
from com.essbase.api.datasource import IEssOlapServer

class Essbase(object):
	def __init__(self, username=None, password=None, providerServer=None, essbaseServer=None):
		self.olap = None
		self.cube = None
		self.username = username
		self.password = password
		self.providerUrl = 'http://%(server)s/aps/JAPI' % { 'server': providerServer }
		self.essbaseServer = essbaseServer
		#Create JAPI instance
		self.essbase = IEssbase.Home.create(IEssbase.JAPI_VERSION)
		#Sign on to provider services
		self.domain = self.essbase.signOn(username, password, False, None, self.providerUrl)

	def connect(self, app=None, db=None):
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
			self.essbase.signOff()
		return "Disconnected"
		
	def start(self):
		self.cube.start()
		
	def stop(self):
		self.cube.stop()
		
	def calculate(self, script=None, syntaxCheckOnly=False):
		if script == None:
			return False
		#Less than 30 characters lets assume its a physical script
		elif len(script) < 30:
			self.cube.calculate(syntaxCheckOnly, script)
			return True
		#Everything else is a dynamic script so run it
		else:
			self.cube.calculate(script, syntaxCheckOnly)
			return True