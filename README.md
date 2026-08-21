<div align="center" width="100%">
    <h1>XingDumper</h1>
    <p>Python 3 script to dump company employees from XING API</p><p>
    <a target="_blank" href="https://github.com/l4rm4nd"><img src="https://img.shields.io/badge/maintainer-LRVT-orange" /></a>
    <a target="_blank" href="https://GitHub.com/l4rm4nd/XingDumper/graphs/contributors/"><img src="https://img.shields.io/github/contributors/l4rm4nd/XingDumper.svg" /></a><br>
    <a target="_blank" href="https://GitHub.com/l4rm4nd/XingDumper/commits/"><img src="https://img.shields.io/github/last-commit/l4rm4nd/XingDumper.svg" /></a>
    <a target="_blank" href="https://GitHub.com/l4rm4nd/XingDumper/issues/"><img src="https://img.shields.io/github/issues/l4rm4nd/XingDumper.svg" /></a>
    <a target="_blank" href="https://github.com/l4rm4nd/XingDumper/issues?q=is%3Aissue+is%3Aclosed"><img src="https://img.shields.io/github/issues-closed/l4rm4nd/XingDumper.svg" /></a><br>
        <a target="_blank" href="https://github.com/l4rm4nd/XingDumper/stargazers"><img src="https://img.shields.io/github/stars/l4rm4nd/XingDumper.svg?style=social&label=Star" /></a>
    <a target="_blank" href="https://github.com/l4rm4nd/XingDumper/network/members"><img src="https://img.shields.io/github/forks/l4rm4nd/XingDumper.svg?style=social&label=Fork" /></a>
    <a target="_blank" href="https://github.com/l4rm4nd/XingDumper/watchers"><img src="https://img.shields.io/github/watchers/l4rm4nd/XingDumper.svg?style=social&label=Watch" /></a><br>
    <a target="_blank" href="https://hub.docker.com/r/l4rm4nd/xingdumper"><img src="https://badgen.net/badge/icon/l4rm4nd%2Fxingdumper:latest?icon=docker&label" /></a><br><p>
    <a href="https://www.buymeacoffee.com/LRVT" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>
</div>

## 💬 Description

XingDumper is a Python 3 script that dumps employee data from the XING social networking platform.

The results contain firstname, lastname, position, gender, location and a user's profile link. Only 2 API calls are required to retrieve all employees. With the `--email-format` CLI flag one can define a Python string format to auto generate email addresses based on the retrieved first and last name.

## ✨ Requirements

XingDumper talks with the unofficial XING API, which requires authentication. Therefore, you must have a valid XING user account. To keep it simple, XingDumper just expects a cookie value provided by you. Doing it this way, even 2FA protected accounts are supported. Furthermore, you are tasked to provide a XING company URL to dump employees from.

#### Retrieving XING Cookie

1. Sign into www.xing.com and retrieve your ``login`` cookie value e.g. via developer tools
2. Specify your cookie value either in the python script's variable ``LOGIN_COOKIE`` or temporarily during runtime via the CLI flag ``--cookie``

#### Retrieving XING Company URL

1. Search your target company on Google Search or directly on XING
2. The Xing company URL should look something like this: https://www.xing.com/pages/appleretaildeutschlandgmbh

## 🎓 Usage

````
usage: xingdumper.py [-h] --url <xing-url> [--count <number>] [--cookie <cookie>] [--full] [--quiet] [--email-format <mail-format>] [--output-json <json-file>] [--output-csv <csv-file>]

options:
  -h, --help            show this help message and exit
  --url <xing-url>      A XING company url - https://xing.com/pages/<company>
  --count <number>      Amount of employees to extract - max. 2999
  --cookie <cookie>     XING 'login' cookie for authentication
  --full                Dump additional contact details (slow) - email, phone, fax, mobile
  --email-format <mail-format>       Python string format for emails; for example:
                        --email-format '{0}.{1}@example.com' --> john.doe@example.com
                        --email-format '{0[0]}.{1}@example.com' --> j.doe@example.com
                        --email-format '{1}@example.com' --> doe@example.com
                        --email-format '{0}@example.com' --> john@example.com
                        --email-format '{0[0]}{1[0]}@example.com' --> jd@example.com
  --output-json <json-file>
                        Store results in json output file
  --output-csv <csv-file>
                        Store results in csv output file                        
````

### 🐳 Example 1 - Docker Run

````
docker run --rm l4rm4nd/xingdumper:latest --url https://www.xing.com/pages/audiag --cookie '<cookie>' --email-format '{0}.{1}@apple.de'
````

### 🐍 Example 2 - Native Python

````
# install dependencies
pip install -r requirements.txt

python3 xingdumper.py --url https://www.xing.com/pages/audiag --cookie '<cookie>' --email-format '{0}.{1}@apple.de'
````

### 🌍 Example 3 - Browser Dev Console

1. Open Xing and log in
2. Open the Xing company site with `/pages/xxyy`
3. Open developer console (CTRL+SHIFT+i), paste the content of `console.js` and press enter
4. Define email format and provide email domain in JS popups
5. Confirm to start

Results printed in dev console and downloaded as CSV.

## 💎 Outputs

The script will return employee data as semi-colon separated values (like CSV):

````

▒██   ██▒ ██▓ ███▄    █   ▄████ ▓█████▄  █    ██  ███▄ ▄███▓ ██▓███  ▓█████  ██▀███  
▒▒ █ █ ▒░▓██▒ ██ ▀█   █  ██▒ ▀█▒▒██▀ ██▌ ██  ▓██▒▓██▒▀█▀ ██▒▓██░  ██▒▓█   ▀ ▓██ ▒ ██▒
░░  █   ░▒██▒▓██  ▀█ ██▒▒██░▄▄▄░░██   █▌▓██  ▒██░▓██    ▓██░▓██░ ██▓▒▒███   ▓██ ░▄█ ▒
 ░ █ █ ▒ ░██░▓██▒  ▐▌██▒░▓█  ██▓░▓█▄   ▌▓▓█  ░██░▒██    ▒██ ▒██▄█▓▒ ▒▒▓█  ▄ ▒██▀▀█▄  
▒██▒ ▒██▒░██░▒██░   ▓██░░▒▓███▀▒░▒████▓ ▒▒█████▓ ▒██▒   ░██▒▒██▒ ░  ░░▒████▒░██▓ ▒██▒
▒▒ ░ ░▓ ░░▓  ░ ▒░   ▒ ▒  ░▒   ▒  ▒▒▓  ▒ ░▒▓▒ ▒ ▒ ░ ▒░   ░  ░▒▓▒░ ░  ░░░ ▒░ ░░ ▒▓ ░▒▓░
░░   ░▒ ░ ▒ ░░ ░░   ░ ▒░  ░   ░  ░ ▒  ▒ ░░▒░ ░ ░ ░  ░      ░░▒ ░      ░ ░  ░  ░▒ ░ ▒░
 ░    ░   ▒ ░   ░   ░ ░ ░ ░   ░  ░ ░  ░  ░░░ ░ ░ ░      ░   ░░          ░     ░░   ░ 
 ░    ░   ░           ░       ░    ░       ░            ░               ░  ░  by LRVT                                                   

[i] Company Name: Apple
[i] Company X-ID: 271572.8873b4
[i] Company Slug: appleretaildeutschlandgmbh
[i] Dumping Date: 24/12/2021 13:37:00
[i] Email Format: {0}.{1}@apple.de

Firstname;Lastname;Email;Position;Gender;Location;E-Mail;Fax;Mobile;Phone;Profile
Mina;Abdallah;mina.abdallah@apple.de;RFIC Design Engineer;MALE;Unterhaching,Deutschland;None;None;None;None;https://www.xing.com/profile/Mina_Abdallah
Isma;Abdan;isma.abdan@apple.de;Gabelstaplerfahrer;MALE;Huelva,Spanien;None;None;None;None;https://www.xing.com/profile/Isma_Abdan

[i] Successfully crawled 2 Apple employees. Hurray ^_-
````

Optionally, you can use the CLI parameters `--output-json` and `--output-csv` to store the results as JSON or CSV.

## 💥 Limitations

Dumped contact details via `--full` are most often empty. Germans seem to take privacy very seriously.

Furthermore, the details may only be accessible if you already belong to the contact list of the crawled employee. Kinda unlikely, however, the default privacy settings of XING would allow a retrival, if the data is configured and the privacy settings not changed by the crawled employee.

## 🤖 Repo Statistics

![Alt](https://repobeats.axiom.co/api/embed/cb3bbff6ff44db8f1aa645d442c4889c9c697073.svg "Repobeats analytics image")
