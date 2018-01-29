import urllib2
from bs4 import BeautifulSoup
from tqdm import tqdm
import csv

"""
Script to scrap list of Vancouver schools from the Fraser Institute page
"""

base_url = "http://britishcolumbia.compareschoolrankings.org"
url = "/elementary/SchoolsByRankLocationName.aspx"
page = urllib2.urlopen(base_url+url).read()
soup = BeautifulSoup(page, "lxml")
record_table = soup.find_all("table", {"class":"rating"})
schools_html = record_table[0].find_all("tr")[2:]

school_keys = ["rank", "rank_5y", "trend", "name", "city", "rating", "rating_5y"]
schools = []
l=0
with open ("schools.csv", "w") as f:
	for school_html in tqdm(schools_html):
		school_val = school_html.find_all("td", {"class":"tdcell"})
		school = {}
		for i in range(len(school_val)):
			school[school_keys[i]] = school_val[i].get_text()
		school["url"] = base_url+school_val[3].a["href"]
		page_supl = urllib2.urlopen(school["url"])
		soup_supl = BeautifulSoup(page_supl, "lxml")
		school_supl = soup_supl.find("span", {"id":"ctl00_ContentPlaceHolder1_SchoolInfoDisplay"})
		school_supl_val = [elem for elem in school_supl.childGenerator()]
		school["type"] = school_supl_val[2]
		school["address"] = school_supl_val[4]+" "+school_supl_val[6]
		school["phone"] = school_supl_val[8]
		school["district"] = school_supl_val[11]
		del school["trend"]
		schools.append(school)
		if l==0:
			w = csv.DictWriter(f, school.keys())
			w.writeheader()
		l += 1
		w.writerow(school)



