import urllib2
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import csv

"""
Script to scrap list of Vancouver schools from the Fraser Institute page
"""

base_url = "http://britishcolumbia.compareschoolrankings.org"
url = "/elementary/SchoolsByRankLocationName.aspx"

def get_basic_data(base_url, school_url):
	page = urllib2.urlopen(base_url + school_url).read()
	soup = BeautifulSoup(page, "html.parser")
	rating_table = soup.find_all("table", {"class":"rating"})
	schools_html = rating_table[0].find_all("tr")[2:]

	schools = []
	school_keys = ["rank", "rank_5y", "trend", "name", "city", "rating", "rating_5y"]

	for school_html in tqdm(schools_html):
		school_val = school_html.find_all("td", {"class":"tdcell"})
		school = {}
		for i in range(len(school_val)):
			school[school_keys[i]] = school_val[i].get_text()
		school["url"] = base_url + school_val[3].a["href"]
		del school["trend"]
		schools.append(school)
		
	return schools

def district_clean(text):
	return text.replace("School District: ","")

def phone_clean(text):
	return text.replace("Phone Number: ", "")

def get_additional_data(school_dic):
	try: 
		page_supl = urllib2.urlopen(school_dic["url"])
		soup_supl = BeautifulSoup(page_supl, "html.parser")
		school_supl = soup_supl.find("span", {"id":"ctl00_ContentPlaceHolder1_SchoolInfoDisplay"})
		school_supl_val = [elem for elem in school_supl.childGenerator()]
		school = {}
		school_dic["type"] = school_supl_val[2]
		school_dic["address"] = school_supl_val[4]+school_supl_val[6]
		school_dic["phone"] = phone_clean(school_supl_val[8])
		school_dic["district"] = district_clean(school_supl_val[11])
		return school_dic
	except Exception as e:
		print (e)
		
from multiprocessing import Pool

def main():
	base_url = "http://britishcolumbia.compareschoolrankings.org"
	url = "/elementary/SchoolsByRankLocationName.aspx"
	schools_list = get_basic_data(base_url, url)
	
	try:
		p = Pool(10)
		schools = []
		with tqdm(total = len(schools_list)) as pbar:
			for i, res in tqdm(enumerate(p.imap_unordered(get_additional_data, schools_list))):
				pbar.update()
				schools.append(res)
		pbar.close()
		p.close()
		p.join()

	except Exception as e:
		print (e)
	
	table_header =  ["address"
					, "name"
					, "type"
					, "rating"
					, "rating_5y"
					, "rank"
					, "rank_5y"
					, "city"
					, "phone"
					, "district"
					, "url"
					]

	with open ("data.csv","w") as f:
		w = csv.DictWriter(f, table_header)
		w.writeheader()
		for school in schools:
			try:
				w.writerow(school)

			except Exception as e:
				print (e)

if __name__ == '__main__':
	main()
# with open ("schools.csv", "w") as f:
# 	for school_html in tqdm(schools_html):
# 		school_val = school_html.find_all("td", {"class":"tdcell"})
# 		school = {}
# 		for i in range(len(school_val)):
# 			school[school_keys[i]] = school_val[i].get_text()
# 		school["url"] = base_url+school_val[3].a["href"]
# 		# try: 
# 		# 	page_supl = urllib2.urlopen(school["url"])
# 		# 	soup_supl = BeautifulSoup(page_supl, "lxml")
# 		# 	school_supl = soup_supl.find("span", {"id":"ctl00_ContentPlaceHolder1_SchoolInfoDisplay"})
# 		# 	school_supl_val = [elem for elem in school_supl.childGenerator()]
# 		# 	school["type"] = school_supl_val[2]
# 		# 	school["address"] = school_supl_val[4]+" "+school_supl_val[6]
# 		# 	school["phone"] = school_supl_val[8]
# 		# 	school["district"] = school_supl_val[11]
# 		# except:
# 		# 	errors.append(school["name"])
		
# 		del school["trend"]
# 		schools.append(school)
# 		if l==0:
# 			w = csv.DictWriter(f, school.keys())
# 			w.writeheader()
# 		l += 1
# 		try:
# 			w.writerow(school)
# 		except:
# 			errors.append(school)
# for e in errors:
# 	print (e)



