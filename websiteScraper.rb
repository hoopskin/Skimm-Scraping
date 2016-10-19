require 'nokogiri'
require 'net/http'

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
		person = person.gsub("\u{a0}", "").gsub("^ ", "").strip.dump
		puts person[1..-2]
	end

	puts rawBirthdayText.split(";").size.to_s+" birthdays for "+suffix
end

url = "http://theskimm.com/2016/09/05/skimm-for-september-6th-3"
