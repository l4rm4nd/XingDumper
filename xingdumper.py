import requests
import json
import argparse
from argparse import RawTextHelpFormatter
from datetime import datetime

# you may store your session cookie here persistently
LOGIN_COOKIE = "<INSERT-YOUR-XING-LOGIN-COOKIE-VALUE>"

# converting german umlauts
special_char_map = {ord('ä'):'ae', ord('ü'):'ue', ord('ö'):'oe', ord('ß'):'ss'}

format_examples = '''
--email-format '{0}.{1}@example.com' --> john.doe@example.com
--email-format '{0[0]}.{1}@example.com' --> j.doe@example.com
--email-format '{1}@example.com' --> doe@example.com
--email-format '{0}@example.com' --> john@example.com
--email-format '{0[0]}{1[0]}@example.com' --> jd@example.com
'''

parser = argparse.ArgumentParser("xingdumper.py", formatter_class=RawTextHelpFormatter)
parser.add_argument("--url", metavar='<xing-url>', help="A XING company url - https://xing.com/pages/<company>", type=str, required=True)
parser.add_argument("--count", metavar='<number>', help="Amount of employees to extract - max. 2999", type=int, required=False)
parser.add_argument("--cookie", metavar='<cookie>', help="XING 'login' cookie for authentication", type=str, required=False,)
parser.add_argument("--full", help="Dump additional contact details (slow) - email, phone, fax, mobile", required=False, action='store_true')
parser.add_argument("--quiet", help="Show employee results only", required=False, action='store_true')
parser.add_argument("--email-format", help="Python string format for emails; for example:"+format_examples, required=False, type=str)

args = parser.parse_args()
url = args.url

if (args.cookie):
	LOGIN_COOKIE = args.cookie

if (args.email_format):
	mailformat = args.email_format
else:
	mailformat = False

if (args.count and args.count < 3000):
	count = args.count
else:
	# according to XING, the result window must be less than 3000
	count = 2999

api = "https://www.xing.com/xing-one/api"
headers = {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)', 'Content-type': 'application/json'}
cookies_dict = {"login": LOGIN_COOKIE}

if (url.startswith('https://www.xing.com/pages/')):
	try:
		before_keyword, keyword, after_keyword = url.partition('pages/')
		company = after_keyword

		# retrieve company id from the api
		postdata1 = {"operationName":"EntitySubpage","variables":{"id":company,"moduleType":"employees"},"query":"query EntitySubpage($id: SlugOrID!, ) {\n entityPageEX(id: $id) {\n ... on EntityPage {\n slug\n  title\n context {\n  companyId\n }\n  }\n }\n}\n"}
		r = requests.post(api, data=json.dumps(postdata1), headers=headers, cookies=cookies_dict)
		response1 = r.json()

		companyID = response1["data"]["entityPageEX"]["context"]["companyId"]
		
		# retrieve employee information from the api based on previously obtained company id
		postdata2 = {"operationName":"Employees","variables":{"consumer":"","id":companyID,"first":count,"query":{"consumer":"web.entity_pages.employees_subpage","sort":"CONNECTION_DEGREE"}},"query":"query Employees($id: SlugOrID!, $first: Int, $after: String, $query: CompanyEmployeesQueryInput!, $consumer: String! = \"\", $includeTotalQuery: Boolean = false) {\n  company(id: $id) {\n id\n totalEmployees: employees(first: 0, query: {consumer: $consumer}) @include(if: $includeTotalQuery) {\n total\n }\n employees(first: $first, after: $after, query: $query) {\n total\n edges {\n node {\n profileDetails {\n id\n firstName\n lastName\n displayName\n gender\n pageName\n location {\n displayLocation\n  }\n occupations {\n subline\n }\n }\n }\n }\n }\n }\n}\n"}
		r2 = requests.post(api, data=json.dumps(postdata2), headers=headers, cookies=cookies_dict)
		response2 = r2.json()

		if not args.quiet:

			print("""\

▒██   ██▒ ██▓ ███▄    █   ▄████ ▓█████▄  █    ██  ███▄ ▄███▓ ██▓███  ▓█████  ██▀███  
▒▒ █ █ ▒░▓██▒ ██ ▀█   █  ██▒ ▀█▒▒██▀ ██▌ ██  ▓██▒▓██▒▀█▀ ██▒▓██░  ██▒▓█   ▀ ▓██ ▒ ██▒
░░  █   ░▒██▒▓██  ▀█ ██▒▒██░▄▄▄░░██   █▌▓██  ▒██░▓██    ▓██░▓██░ ██▓▒▒███   ▓██ ░▄█ ▒
 ░ █ █ ▒ ░██░▓██▒  ▐▌██▒░▓█  ██▓░▓█▄   ▌▓▓█  ░██░▒██    ▒██ ▒██▄█▓▒ ▒▒▓█  ▄ ▒██▀▀█▄  
▒██▒ ▒██▒░██░▒██░   ▓██░░▒▓███▀▒░▒████▓ ▒▒█████▓ ▒██▒   ░██▒▒██▒ ░  ░░▒████▒░██▓ ▒██▒
▒▒ ░ ░▓ ░░▓  ░ ▒░   ▒ ▒  ░▒   ▒  ▒▒▓  ▒ ░▒▓▒ ▒ ▒ ░ ▒░   ░  ░▒▓▒░ ░  ░░░ ▒░ ░░ ▒▓ ░▒▓░
░░   ░▒ ░ ▒ ░░ ░░   ░ ▒░  ░   ░  ░ ▒  ▒ ░░▒░ ░ ░ ░  ░      ░░▒ ░      ░ ░  ░  ░▒ ░ ▒░
 ░    ░   ▒ ░   ░   ░ ░ ░ ░   ░  ░ ░  ░  ░░░ ░ ░ ░      ░   ░░          ░     ░░   ░ 
 ░    ░   ░           ░       ░    ░       ░            ░               ░  ░  by LRVT
			""")

			print("[i] Company Name: " + response1["data"]["entityPageEX"]["title"])
			print("[i] Company X-ID: " + companyID)
			print("[i] Company Slug: " + company)
			print("[i] Dumping Date: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
			if mailformat:
				print("[i] Email Format: " + mailformat)
			print()

		if not mailformat:
			if args.full:
				legende = "Firstname;Lastname;Position;Gender;Location;E-Mail;Fax;Mobile;Phone;Profile"
			else:
				legende = "Firstname;Lastname;Position;Gender;Location;Profile"
		else:
			if args.full:
				legende = "Firstname;Lastname;Email;Position;Gender;Location;E-Mail;Fax;Mobile;Phone;Profile"
			else:
				legende = "Firstname;Lastname;Email;Position;Gender;Location;Profile"
		
		print(legende)

		dump_count = 0

		# loop over employees
		for employee in response2['data']['company']['employees']['edges']:
			dump_count += 1
			firstname = employee['node']['profileDetails']['firstName']
			lastname = employee['node']['profileDetails']['lastName']
			try:
				position = employee['node']['profileDetails']['occupations'][0]['subline']
			except:
				position = "None"
			gender = employee['node']['profileDetails']['gender']
			location = employee['node']['profileDetails']['location']['displayLocation'].replace('**','').replace(', ',',')
			pagename = employee['node']['profileDetails']['pageName']

			if args.full:
				# dump additional contact details for each employee. Most often is "None", so no default api queries for this data
				postdata3 = {"operationName":"getXingId","variables":{"profileId":pagename},"query":"query getXingId($profileId: SlugOrID!, $actionsFilter: [AvailableAction!]) {\n  profileModules(id: $profileId) {\n    __typename\n    xingIdModule(actionsFilter: $actionsFilter) {\n      xingId {\n        status {\n          localizationValue\n          __typename\n        }\n        __typename\n      }\n      __typename\n      ...xingIdContactDetails\n       }\n  }\n}\n\nfragment xingIdContactDetails on XingIdModule {\n  contactDetails {\n    business {\n          email\n      fax {\n        phoneNumber\n   }\n      mobile {\n        phoneNumber\n  }\n      phone {\n        phoneNumber\n   }\n   }\n        __typename\n  }\n  __typename\n}\n"}
				r3 = requests.post(api, data=json.dumps(postdata3), headers=headers, cookies=cookies_dict)
				response3 = r3.json()
				try:
					# try to extract contact details
					email = response3['data']['profileModules']['xingIdModule']['contactDetails']['business']['email']
					fax = response3['data']['profileModules']['xingIdModule']['contactDetails']['business']['fax']['phoneNumber']
					mobile = response3['data']['profileModules']['xingIdModule']['contactDetails']['business']['mobile']['phoneNumber']
					phone = response3['data']['profileModules']['xingIdModule']['contactDetails']['business']['phone']['phoneNumber']
				except:
					# if contact details are missing in the API response, set to 'None'
					email = "None"
					fax = "None"
					mobile = "None"
					phone = "None"
				
				if not mailformat:
					# print employee information as Comma Separated Values (CSV)
					print(firstname + ";" + lastname + ";" + position + ";" + gender + ";" + location + ";" + str(email) + ";" + str(fax) + ";" + str(mobile) + ";" + str(phone) + ";" + "https://www.xing.com/profile/" + pagename)
				else:
					print(firstname + ";" + lastname + ";" + mailformat.format(firstname.lower().replace(".","").translate(special_char_map),lastname.lower().replace(".","").translate(special_char_map)) + ";" + position + ";" + gender + ";" + location + ";" + str(email) + ";" + str(fax) + ";" + str(mobile) + ";" + str(phone) + ";" + "https://www.xing.com/profile/" + pagename)
			else:
				if not mailformat:
					print(firstname + ";" + lastname + ";" + position + ";" + gender + ";" + location + ";" + "https://www.xing.com/profile/" + pagename)
				else:
					print(firstname + ";" + lastname + ";" + mailformat.format(firstname.lower().replace(".","").translate(special_char_map),lastname.lower().replace(".","").translate(special_char_map)) + ";" + position + ";" + gender + ";" + location + ";" + "https://www.xing.com/profile/" + pagename)
		
		if not args.quiet:
			print()
			print("[i] Successfully crawled " + str(dump_count) + " " + response1["data"]["entityPageEX"]["title"] + " employees. Hurray ^_-")
	
	except Exception as e:
		print()
		print("[!] Exception. Either API has changed and this script is broken or authentication failed.")
		print("    > Set 'LOGIN_COOKIE' variable permanently in script or use the '--cookie' CLI flag!")
		print("[debug] " + str(e))
else:
	print()
	print("[!] Invalid URL provided.")
	print("[i] Example URL: 'https://www.xing.com/pages/appleretaildeutschlandgmbh'")
