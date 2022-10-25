# XingDumper
Python 3 script to dump company employees from XING API.

The results contain firstname, lastname, position, gender, location and a user's profile link. Only 2 API calls are required to retrieve all employees. 

With the `--full` CLI flag an additional API request will be made for each employee to retrieve contact details such as email, fax, mobile and phone number. However, this data is most often unset by XING users.

## How-To
1. Sign into www.xing.com and retrieve your ``login`` cookie value e.g. via developer tools
2. Specify your cookie value in the python script's variable ``LOGIN_COOKIE`` or via the CLI flag ``--cookie``
3. Browse your company on XING and note the url. Must be something like https://www.xing.com/pages/appleretaildeutschlandgmbh
4. Install requirements via ``pip install -r requirements.txt``
5. Run the Python script and enjoy results

## Usage
````
usage: xingdumper.py [-h] --url <xing-url> [--count <number>] [--cookie <cookie>] [--full] [--quiet]

optional arguments:
  -h, --help         show this help message and exit
  --url <xing-url>   A XING company url - https://xing.com/pages/<company>
  --count <number>   Amount of employees to extract - max. 2999
  --cookie <cookie>  XING 'login' cookie for authentication
  --full             Dump additional contact details (slow) - email, phone, fax, mobile
  --quiet            Show employee results only
````

## Docker Run Examples
````
docker run --rm l4rm4nd/xingdumper:latest --url <xing-url> --cookie <cookie>
````

## Examples

Dumping all Audi employees from XING API (max. 3000) into outfile using `--quiet` mode:
````
python3 xingdumper.py --url https://www.xing.com/pages/audiag --quiet > audi_employees.out
````
Dumping 10 Apple employees from XING API with additional contact details as terminal output:
````
python3 xingdumper.py --url https://www.xing.com/pages/appleretaildeutschlandgmbh --count 10 --full
````
**Note**: Contact details are most often empty. We Germans take privacy seriously! Further, the details may only be accessible if you already belong to the contact list of the crawled employee. Kinda unlikely, however the default privacy settings of XING would allow a retrival, if the data is configured and the privacy settings not changed by the user.

## Results

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

Firstname;Lastname;Position;Gender;Location;E-Mail;Fax;Mobile;Phone;Profile
Mina;Abdallah;RFIC Design Engineer;MALE;Unterhaching,Deutschland;None;None;None;None;https://www.xing.com/profile/Mina_Abdallah
Isma;Abdan;Gabelstaplerfahrer;MALE;Huelva,Spanien;None;None;None;None;https://www.xing.com/profile/Isma_Abdan

[i] Successfully crawled 2 Apple employees. Hurray ^_-
````
