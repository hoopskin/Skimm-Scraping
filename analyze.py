import mailbox
from bs4 import BeautifulSoup
#import html.parser
import html
#h = html.parser.HTMLParser()

mbox = mailbox.mbox('Skimm Emails.mbox')
#print(mbox)
#print(mbox.iterkeys())
#print(mbox.itervalues())

for item in mbox.items():
	print("-------------")
	msg = item[1]
	#print(msg['Subject'])
	if msg['Subject'].startswith("Daily Skimm"):
		#TODO: Encoding... Not sure what's going on. Some end tags aren't properly there, so Soup is having an issue determining what's the text
		#E.g. h3 ended with "&gt;" so soup thought loads after it was the 'text' since it hadn't 'ended' yet
		#soup = BeautifulSoup(h.unescape(msg.as_string().replace("=2E","",10000).replace("\n","",10000).replace("&lt;","<",10000).replace("&lt;=","<",10000).replace("&gt;",">",10000)), 'html.parser')
		soup = BeautifulSoup(html.unescape(msg.as_string().replace("=2E","",10000).replace("=","",10000).replace("\n","",10000)))
		#print(msg.as_string())
		topHeaders = soup.find_all('h1')
		for header in topHeaders:
			#This could be better...
			text = header.get_text()
			print(text)	

		for messyHeader in soup.find_all('h3'):
			print(messyHeader.get_text())
	#break