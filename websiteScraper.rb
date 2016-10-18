require 'nokogiri'
require 'net/http'

url = "http://theskimm.com/2016/09/05/skimm-for-september-6th-3"

url = url[url.index("//")+2..-1]

site = Net::HTTP.get(url[0..url.index("/")-1], url[url.index("/")..-1])

pageObj = Nokogiri::HTML(site)

bdays = pageObj.css("p.skimm-p")[-1].css("span").css("span")[0].children

rawBirthdayText = ""

for b in bdays
	rawBirthdayText = rawBirthdayText + b.text
end

for person in rawBirthdayText.split(";")
	person = person.gsub("\u{a0}", "").gsub("^ ", "").strip.dump
	puts person[1..-2]
end

puts rawBirthdayText.split(";").size.to_s+" birthdays"