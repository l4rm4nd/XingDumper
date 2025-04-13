import requests
import json
import argparse
import csv
from argparse import RawTextHelpFormatter
from datetime import datetime

LOGIN_COOKIE = "<INSERT-YOUR-XING-LOGIN-COOKIE-VALUE>"

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
parser.add_argument("--cookie", metavar='<cookie>', help="XING 'login' cookie for authentication", type=str, required=False)
parser.add_argument("--full", help="Dump additional contact details (slow) - email, phone, fax, mobile", action='store_true')
parser.add_argument("--email-format", help="Python string format for emails; for example:" + format_examples, metavar='<mail-format>', type=str)
parser.add_argument("--output-json", help="Store results in json output file", metavar="<json-file>", type=str, required=False)
parser.add_argument("--output-csv", help="Store results in csv output file", metavar="<csv-file>", type=str, required=False)

args = parser.parse_args()
url = args.url

if args.cookie:
    LOGIN_COOKIE = args.cookie

mailformat = args.email_format if args.email_format else False
count = args.count if args.count and args.count < 3000 else 2999

api = "https://www.xing.com/xing-one/api"
headers = {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)', 'Content-type': 'application/json'}
cookies_dict = {"login": LOGIN_COOKIE}

if url.startswith('https://www.xing.com/pages/'):
    try:
        _, _, company = url.partition('pages/')

        postdata1 = {"operationName":"EntitySubpage","variables":{"id":company,"moduleType":"employees"},"query":"query EntitySubpage($id: SlugOrID!, ) { entityPageEX(id: $id) { ... on EntityPage { slug title context { companyId } } } }"}
        r = requests.post(api, data=json.dumps(postdata1), headers=headers, cookies=cookies_dict, timeout=200)
        response1 = r.json()
        companyID = response1["data"]["entityPageEX"]["context"]["companyId"]
        companyTitle = response1["data"]["entityPageEX"]["title"]

        postdata2 = {"operationName":"Employees","variables":{"consumer":"","id":companyID,"first":count,"query":{"consumer":"web.entity_pages.employees_subpage","sort":"CONNECTION_DEGREE"}},"query":"query Employees($id: SlugOrID!, $first: Int, $after: String, $query: CompanyEmployeesQueryInput!, $consumer: String! = \"\", $includeTotalQuery: Boolean = false) { company(id: $id) { id totalEmployees: employees(first: 0, query: {consumer: $consumer}) @include(if: $includeTotalQuery) { total } employees(first: $first, after: $after, query: $query) { total edges { node { profileDetails { id firstName lastName displayName gender pageName location { displayLocation } occupations { subline } } } } } } }"}
        r2 = requests.post(api, data=json.dumps(postdata2), headers=headers, cookies=cookies_dict, timeout=200)
        response2 = r2.json()

        employees = []

        if not args.output_json and not args.output_csv:
            print()
            print("[i] Company Name: " + companyTitle)
            print("[i] Company X-ID: " + companyID)
            print("[i] Company Slug: " + company)
            print("[i] Dumping Date: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            if mailformat:
                print("[i] Email Format: " + mailformat)
            print()
        else:
        	print()

        for emp in response2['data']['company']['employees']['edges']:
            pd = emp['node']['profileDetails']
            firstname = pd['firstName']
            lastname = pd['lastName']
            gender = pd.get('gender', 'N/A')
            location = pd.get('location', {}).get('displayLocation', '').replace('**','').replace(', ',',')
            pagename = pd.get('pageName', '')
            profile_url = f"https://www.xing.com/profile/{pagename}"
            try:
                position = pd['occupations'][0]['subline']
            except:
                position = "None"

            employee_entry = {
                "firstname": firstname,
                "lastname": lastname,
                "position": position,
                "gender": gender,
                "location": location,
                "profile": profile_url
            }

            if mailformat:
                firstname_clean = firstname.lower().replace(".", "").translate(special_char_map)
                lastname_clean = lastname.lower().replace(".", "").translate(special_char_map)
                employee_entry['email'] = mailformat.format(firstname_clean, lastname_clean)

            if args.full:
                postdata3 = {"operationName":"getXingId","variables":{"profileId":pagename},"query":"query getXingId($profileId: SlugOrID!, $actionsFilter: [AvailableAction!]) { profileModules(id: $profileId) { __typename xingIdModule(actionsFilter: $actionsFilter) { xingId { status { localizationValue __typename } __typename } __typename ...xingIdContactDetails } } } fragment xingIdContactDetails on XingIdModule { contactDetails { business { email fax { phoneNumber } mobile { phoneNumber } phone { phoneNumber } } __typename } __typename }"}
                r3 = requests.post(api, data=json.dumps(postdata3), headers=headers, cookies=cookies_dict, timeout=200)
                r3data = r3.json()
                try:
                    contact = r3data['data']['profileModules']['xingIdModule']['contactDetails']['business']
                    employee_entry['business_email'] = contact.get('email', 'None')
                    employee_entry['fax'] = contact.get('fax', {}).get('phoneNumber', 'None')
                    employee_entry['mobile'] = contact.get('mobile', {}).get('phoneNumber', 'None')
                    employee_entry['phone'] = contact.get('phone', {}).get('phoneNumber', 'None')
                except:
                    employee_entry['business_email'] = employee_entry['fax'] = employee_entry['mobile'] = employee_entry['phone'] = 'None'

            employees.append(employee_entry)

        if not args.output_json and not args.output_csv:
            print("Firstname;Lastname;" + ("Email;" if mailformat else "") + "Position;Gender;Location;" + ("E-Mail;Fax;Mobile;Phone;" if args.full else "") + "Profile")
            for emp in employees:
                values = [emp['firstname'], emp['lastname']]
                if mailformat:
                    values.append(emp['email'])
                values += [emp['position'], emp['gender'], emp['location']]
                if args.full:
                    values += [emp['business_email'], emp['fax'], emp['mobile'], emp['phone']]
                values.append(emp['profile'])
                print(";".join(values))
            print()

        if args.output_json:
            try:
                output = {
                    "company_id": companyID,
                    "company_url": url,
                    "company_slug": company,
                    "timestamp": datetime.now().isoformat(),
                    "employees": employees
                }
                with open(args.output_json, 'w', encoding='utf-8') as f:
                    json.dump(output, f, ensure_ascii=False, indent=4)
                print(f"[i] Results written to JSON: {args.output_json}")
            except Exception as e:
                print(f"[!] Error writing JSON: {e}")

        if args.output_csv:
            try:
                with open(args.output_csv, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f, delimiter=';')
                    headers = ["Firstname", "Lastname"]
                    if mailformat:
                        headers.append("Email")
                    headers += ["Position", "Gender", "Location"]
                    if args.full:
                        headers += ["E-Mail", "Fax", "Mobile", "Phone"]
                    headers.append("Profile")
                    writer.writerow(headers)
                    for emp in employees:
                        row = [emp['firstname'], emp['lastname']]
                        if mailformat:
                            row.append(emp['email'])
                        row += [emp['position'], emp['gender'], emp['location']]
                        if args.full:
                            row += [emp['business_email'], emp['fax'], emp['mobile'], emp['phone']]
                        row.append(emp['profile'])
                        writer.writerow(row)
                print(f"[i] Results written to CSV: {args.output_csv}")
            except Exception as e:
                print(f"[!] Error writing CSV: {e}")

        print(f"[i] Successfully crawled {len(employees)} {companyTitle} employees. Hurray ^_-")

    except Exception as e:
        print("\n[!] Exception. Either API has changed and this script is broken or authentication failed.")
        print("    > Set 'LOGIN_COOKIE' variable permanently in script or use the '--cookie' CLI flag!")
        print(f"[debug] {e}")
else:
    print("\n[!] Invalid URL provided.")
    print("[i] Example URL: 'https://www.xing.com/pages/appleretaildeutschlandgmbh'")
