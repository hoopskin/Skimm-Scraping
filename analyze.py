import mailbox, html, sys
from bs4 import BeautifulSoup

class Person(object):
	"""docstring for Person"""
	def __init__(self, name, location, isSkimmBassador):
		super(Person, self).__init__()
		#Use if debugging creation working
		#print("Name: %s\t\t Location: %s\t\t Skimm'Bassador: %r" % (name, location, isSkimmBassador))
		self.name = name
		self.location = location
		self.isSkimmBassador = isSkimmBassador

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

def processEmails():
	global emailCount
	mbox = mailbox.mbox('Skimm Emails.mbox')

	i = 1
	emailCount = len(mbox.items())
	for item in mbox.items():
		update_progress("Process Emails", i/emailCount)
		i+=1
		msg = item[1]
		#print(msg['Subject'])
		if msg['Subject'].startswith("Daily Skimm"):
			soup = BeautifulSoup(html.unescape(msg.as_string().replace("=2E","",10000).replace("=","",10000).replace("\n","",10000)), "html.parser")

			birthdays = soup.find_all('p')[-1].get_text()
			birthdaysList = birthdays.split(";")
			for person in birthdaysList:

				isSkimmBassador = (person.strip()[0]=="*")
				try:
					name = person[:person.index("(")].strip()
					location = person[person.index("(")+1:-1].strip()
				except(ValueError):
					name = person
					location = ""
				personList.append(Person(name, location, isSkimmBassador))

	#TODO: Standardize location to city, state.
	#NOTE: There are global individuals.
	for person in personList:
		if len(person.location) == 0:
			continue
		else:
			try:
				locationDict[person.location.split(",")[-1].strip()]+=1
			except(KeyError):
				locationDict[person.location.split(",")[-1].strip()] = 1

def printResults():
	print("Found %i individuals across %i emails (weekdays):" % (len(personList), emailCount))
	print(locationDict)


def main():
	processEmails()
	printResults()


locationDict = {}
personList = []
stateAbbreviations = {'AL': 'Alabama','AK': 'Alaska','AZ': 'Arizona','AR': 'Arkansas','CA': 'California','CO': 'Colorado','CT': 'Connecticut','DE': 'Delaware','FL': 'Florida','GA': 'Georgia','HI': 'Hawaii','ID': 'Idaho','IL': 'Illinois','IN': 'Indiana','IA': 'Iowa','KS': 'Kansas','KY': 'Kentucky','LA': 'Louisiana','ME': 'Maine','MD': 'Maryland','MA': 'Massachusetts','MI': 'Michigan','MN': 'Minnesota','MS': 'Mississippi','MO': 'Missouri','MT': 'Montana','NE': 'Nebraska','NV': 'Nevada','NH': 'New Hampshire','NJ': 'New Jersey','NM': 'New Mexico','NY': 'New York','NC': 'North Carolina','ND': 'North Dakota','OH': 'Ohio','OK': 'Oklahoma','OR': 'Oregon','PA': 'Pennsylvania','RI': 'Rhode Island','SC': 'South Carolina','SD': 'South Dakota','TN': 'Tennessee','TX': 'Texas','UT': 'Utah','VT': 'Vermont','VA': 'Virginia','WA': 'Washington','WV': 'West Virginia','WI': 'Wisconsin','WY': 'Wyoming'}
emailCount = 0

main()
