import mailbox
from bs4 import BeautifulSoup
#import html.parser
import html
#h = html.parser.HTMLParser()
class Person(object):
	"""docstring for Person"""
	def __init__(self, name, location, isSkimmBassador):
		super(Person, self).__init__()
		#Use if debugging creation working
		#print("Name: %s\t\t Location: %s\t\t Skimm'Bassador: %r" % (name, location, isSkimmBassador))
		self.name = name
		self.location = location
		self.isSkimmBassador = isSkimmBassador

personList = []
locationDict = {}

mbox = mailbox.mbox('Skimm Emails.mbox')

#TODO: Add progress bar, especially as this gets bigger and processing time would increase.
for item in mbox.items():
	print("-------------")
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


print("Found %i individuals across %i emails (weekdays):" % (len(personList), len(mbox.items())))
print(locationDict)