require 'nokogiri'
require 'net/http'
require 'csv'
require 'progressbar'

#Go to the archive, get all of the links

url = "theskimm.com/archive"

#NOTE: Look into what's easier for testing / publishing data. If it's a CSV, or part of a JS file?
dataFileName = "skimmrData.csv"
oFile = CSV.open(dataFileName, "ab")

site = Net::HTTP.get(url[0..url.index("/")-1], url[url.index("/")..-1])

pageObj = Nokogiri::HTML(site)

links = pageObj.css("div.links").css("a")
i = 0

#TODO: Eventually this should ignore ones we've already captured
suffixesWeAlreadyHave = []

CSV.foreach(dataFileName) do |row|
	if suffixesWeAlreadyHave.index(row[-1]).nil?
		suffixesWeAlreadyHave.insert(suffixesWeAlreadyHave.size, row[-1])
	end
end

suffixes = []
while i < links.size
	link = links[i]
	i+=1

	suffixes.insert(suffixes.size, link.attribute('href').value)
end

suffixes = suffixes - suffixesWeAlreadyHave

puts suffixes



genderHash = Hash.new
CSV.foreach("nameGender.csv") do |row|
	if genderHash[row[0]].nil?
		genderHash[row[0]] = row[1]
	else
		genderHash[row[1]] = "Both"
	end
end

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

		gender = "Unknown"
		if !genderHash[firstName].nil?
			gender = genderHash[firstName]
		end

		oFile << [isSkimmbassador.to_s, city, state, firstName, lastName, gender, suffix]

	end

	puts rawBirthdayText.split(";").size.to_s+" birthdays for "+suffix
end
