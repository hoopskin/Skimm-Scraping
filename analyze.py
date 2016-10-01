import mailbox, html, sys, csv, datetime
from bs4 import BeautifulSoup

class Person(object):
	"""docstring for Person"""
	def __init__(self, name, location, isSkimmBassador, birthday):
		super(Person, self).__init__()
		#Use if debugging creation working
		#print("Name: %s\t\t Location: %s\t\t Skimm'Bassador: %r" % (name, location, isSkimmBassador))
		self.name = name.replace(",","",100).strip()
		self.location = location
		self.isSkimmBassador = isSkimmBassador
		self.birthday = birthday

		self.city = ""
		self.state = ""
		self.foreignAddr = None
		self.detCityState()
		self.gender = self.detGender()

	def detGender(self):
		try:
			return nameGenderDict[self.name.split()[0]]
		except(KeyError):
			return "Unknown"

	def detCityState(self):
		splitLoc = self.location.split(",")
		if len(splitLoc) == 1:
			if self.location[-2:] in abbrevToState.keys():
				self.state = self.location[-2:]
				self.city = self.location[:-2].strip()
			else:
				self.state = splitLoc[0].strip()
		else:
			self.city = splitLoc[0].strip()
			self.state = splitLoc[1].strip()
			if self.state in stateToAbbrev.keys():
				self.state = stateToAbbrev[self.state]

		if self.state in abbrevToState.keys():
			self.foreignAddr = False
		else:
			self.foreignAddr = True

def update_progress(task, progress):
	"""Creates / Updates a progress bar."""
	barLength = 10 # Modify this to change the length of the progress bar
	status = ""
	if isinstance(progress, int):
		progress = float(progress)
	if not isinstance(progress, float):
		progress = 0
		status = "error: progress var must be float\r\n"
	if progress < 0:
		progress = 0
		status = "Halt...\r\n"
	if progress >= 1:
		progress = 1
		status = "Done...\r\n"
	block = int(round(barLength*progress))
	text = "\r"+task+": [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), int(progress*100), status)
	sys.stdout.write(text)
	sys.stdout.flush()

def processGenderFile():
	global nameGenderDict
	print("Processing Gender File...")
	reader = csv.reader(open("nameGender.csv", "rt"))
	header = next(reader)
	for row in reader:
		if row[0] in nameGenderDict.keys():
			nameGenderDict[row[0]] = "Both"
		else:
			nameGenderDict[row[0]] = row[1]
	print("Complete!\n")

def processEmails():
	global emailCount, genderDict
	mbox = mailbox.mbox('Skimm Emails.mbox')

	i = 1
	emailCount = len(mbox.items())
	for item in mbox.items():
		update_progress("Process Emails", i/emailCount)
		i+=1
		msg = item[1]
		bday = msg['Received'].split("  ")[-1]
		bday = bday.split(" ")[1:4]
		bday = "%s %s %s"%(bday[0], bday[1], bday[2])
		bday = datetime.datetime.strptime(bday, "%d %b %Y")
		#print(msg['Subject'])
		if msg['Subject'].startswith("Daily Skimm"):
			soup = BeautifulSoup(html.unescape(msg.as_string().replace("=2E","",10000).replace("=","",10000).replace("\n","",10000)).replace("\xa0",", ", 10000), "html.parser")

			birthdays = soup.find_all('p')[-1].get_text()
			birthdaysList = birthdays.split(";")
			for person in birthdaysList:
				person = person.replace("\xa0"," ", 10000).strip()

				#TODO: This is messy, is there a better way?
				if len(person) == 0:
					continue

				if person[0] == ",":
					person = person[1:].strip()
				
				if person.startswith("theSkimm"):
					person = person[11:]
				elif person.startswith("Dr "):
					person = person[3:]
				elif person.startswith("Skimm Mom "):
					person = person[10:]

				#isSkimmBassador = (person.strip()[0]=="*")
				isSkimmBassador = False
				try:
					name = person[:person.index("(")].strip()
					isSkimmBassador = name[0] == "*"
					if isSkimmBassador:
						name = name[1:]
					location = person[person.index("(")+1:-1].strip()
				except(ValueError):
					name = person
					location = ""

				personList.append(Person(name, location, isSkimmBassador, bday))

def preProcess():
	global locationDict, genderDict, globalSkimmbassadorCount, locationSkimmDict, birthdayDict

	for person in personList:
		#Gender
		try:
			genderDict[person.gender]+=1
		except(KeyError):
			genderDict[person.gender] = 1

		#Global SkimmBassador Rate
		if person.isSkimmBassador:
			globalSkimmbassadorCount+=1

		#Location SkimmBassador
		if person.foreignAddr:
			locationSkimmDict["Foreign"][1]+=1
			if person.isSkimmBassador:
				locationSkimmDict["Foreign"][0]+=1
		else:
			try:
				locationSkimmDict[person.state][1]+=1
			except(KeyError):
				locationSkimmDict[person.state] = [0,1]

			#Don't need to do try-catch since previous captures all
			if person.isSkimmBassador:
				locationSkimmDict[person.state][0]+=1

		#Birthday
		try:
			birthdayDict[person.birthday]+=1
		except(KeyError):
			birthdayDict[person.birthday] = 1
	
def printGenderSplit():
	print("------Gender-----")

	keys = list(genderDict.keys())
	keys.sort()

	for k in keys:
		print("%s\t%i" % (k, genderDict[k]))
	
	print("--End of Gender--")

def printSkimmbassadorRate():
	print("-----Skimmbassador Rate-----")
	print("%i/%i = %.2f%%" % (globalSkimmbassadorCount, len(personList), globalSkimmbassadorCount/len(personList)*100))
	print("--End of Simmbassador Rate--")

def printBirthdayRate():
	print("------Birthdays-----")
	keys = list(birthdayDict.keys())
	keys.sort()

	for k in keys:
		print("%s\t%i" % (datetime.datetime.strftime(k, "%m/%d/%Y"), birthdayDict[k]))

	print("--End of Birthdays--")

def printLocSkimmbassadorRates():
	print("------Skimmbassadors by State-----")

	locKeys = list(locationSkimmDict.keys())
	locKeys.sort()

	for k in locKeys:
		if locationSkimmDict[k][1]>0:
			numerator = locationSkimmDict[k][0]
			denominator = locationSkimmDict[k][1]
			print("%s\t%i/%i = %.2f%%\t%i/%i = %.2f%%" % (k, numerator, denominator, numerator/denominator*100, numerator, globalSkimmbassadorCount, numerator/globalSkimmbassadorCount*100))
	print("--End of Skimmbassadors by State--")

def printResults():
	print("Found %i individuals across %i emails (weekdays):" % (len(personList), emailCount))
	preProcess()
	printSkimmbassadorRate()
	printLocSkimmbassadorRates()
	printBirthdayRate()
	printGenderSplit()

def main():
	processEmails()
	printResults()


nameGenderDict = {}
genderDict = {}
locationSkimmDict = {"Foreign":[0,0]}
birthdayDict = {}
abbrevToState = {'AL': 'Alabama','AK': 'Alaska','AZ': 'Arizona','AR': 'Arkansas','CA': 'California','CO': 'Colorado','CT': 'Connecticut','DE': 'Delaware','FL': 'Florida','GA': 'Georgia','HI': 'Hawaii','ID': 'Idaho','IL': 'Illinois','IN': 'Indiana','IA': 'Iowa','KS': 'Kansas','KY': 'Kentucky','LA': 'Louisiana','ME': 'Maine','MD': 'Maryland','MA': 'Massachusetts','MI': 'Michigan','MN': 'Minnesota','MS': 'Mississippi','MO': 'Missouri','MT': 'Montana','NE': 'Nebraska','NV': 'Nevada','NH': 'New Hampshire','NJ': 'New Jersey','NM': 'New Mexico','NY': 'New York','NC': 'North Carolina','ND': 'North Dakota','OH': 'Ohio','OK': 'Oklahoma','OR': 'Oregon','PA': 'Pennsylvania','RI': 'Rhode Island','SC': 'South Carolina','SD': 'South Dakota','TN': 'Tennessee','TX': 'Texas','UT': 'Utah','VT': 'Vermont','VA': 'Virginia','WA': 'Washington','WV': 'West Virginia','WI': 'Wisconsin','WY': 'Wyoming'}
stateToAbbrev = {'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA','Colorado':'CO','Connecticut':'CT','Delaware':'DE','Florida':'FL','Georgia':'GA','Hawaii':'HI','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA','Kansas':'KS','Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD','Massachusetts':'MA','Michigan':'MI','Minnesota':'MN','Mississippi':'MS','Missouri':'MO','Montana':'MT','Nebraska':'NE','Nevada':'NV','New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM','New York':'NY','North Carolina':'NC','North Dakota':'ND','Ohio':'OH','Oklahoma':'OK','Oregon':'OR','Pennsylvania':'PA','Rhode Island':'RI','South Carolina':'SC','South Dakota':'SD','Tennessee':'TN','Texas':'TX','Utah':'UT','Vermont':'VT','Virginia':'VA','Washington':'WA','West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY'}

personList = []

emailCount = 0
globalSkimmbassadorCount = 0

print("\n"*80)
processGenderFile()
main()
