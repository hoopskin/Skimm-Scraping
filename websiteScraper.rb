require 'nokogiri'
require 'net/http'
require 'csv'
require 'progressbar'

#Go to the archive, get all of the links

url = "theskimm.com/archive"

site = Net::HTTP.get(url[0..url.index("/")-1], url[url.index("/")..-1])

pageObj = Nokogiri::HTML(site)

links = pageObj.css("div.links").css("a")
i = 0

suffixes = []
while i < links.size
	link = links[i]
	i+=1

	suffixes.insert(suffixes.size, link.attribute('href').value)
end

puts suffixes

oFile = CSV.open("skimmrData.csv", "ab")

#CSV.open("channelDataDump.csv", "ab") do |channelCSV|
#	channelCSV << ["ID", "Title", "Description", "Subscriber_Count", "Published_Date"]
#	pbar = ProgressBar.new("Channel Data", channelList.count)
#	channelList.each do |curChannel|
#		pbar.inc
#		channel = getChannel(curChannel)
#		channelCSV << [channel.id, channel.title, channel.description, channel.subscriber_count, channel.published_at]
#	end
#	pbar.finish
#end

i = 0
#while i < suffixes.size
for suffix in suffixes
	#suffix = suffixes[i]
	i+=1
	puts suffix
	url = "http://theskimm.com"+suffix
	
	url = url[url.index("//")+2..-1]

	site = Net::HTTP.get(url[0..url.index("/")-1], url[url.index("/")..-1])

	pageObj = Nokogiri::HTML(site)

	begin
		bdays = pageObj.css("p.skimm-p")[-1].css("span").css("span")[0].children
	rescue NoMethodError
		bdays = pageObj.css("p.skimm-p")[-1].children
	end

	rawBirthdayText = ""

	for b in bdays
		rawBirthdayText = rawBirthdayText + b.text
	end

	for person in rawBirthdayText.split(";")
		person = person.gsub("\u{a0}", "").gsub("^ ", "").strip.dump[1..-2]
		isSkimmbassador = person[0] == '*'
		if isSkimmbassador
			person = person[1..-1]
		end

		#puts isSkimmbassador
		city = ""
		state = ""
		personName = person
		if !person.index("(").nil?
			#They have a location
			if !person.split("(")[-1].index(",").nil?
				#They have a properly formatted location of "city, state" (international is an exception)
				city = person.split("(")[-1].split(",")[0].strip
				state = person.split("(")[-1].split(",")[1][0..-2].strip
			end

			personName = person[0..person.index("(")-1].strip
		end

		#isSkimmbassador.to_s
		#city
		#state
		#personName
		firstName = personName
		lastName = ""
		if !personName.index(" ").nil?
			firstName = personName[0..personName.index(" ")-1]
			lastName = personName[personName.index(" ")+1..-1]
		end

		oFile << [isSkimmbassador.to_s, city, state, firstName, lastName, suffix]

	end

	puts rawBirthdayText.split(";").size.to_s+" birthdays for "+suffix
end
