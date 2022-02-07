try:
    import sys
    import os
    import time
    import requests
    import re
    import math
    import concurrent.futures
    from colored import *
except ImportError:
    print("Trying to install the required modules! THIS MAY DISPLAY LARGE ERRORS!\nPlease try to run this script again once all of the modules have been successfully installed.\n\n")
    input("press enter to start installing... ")
    os.system("py -m pip install -r requirements.txt")
    os.system("python -m pip install -r requirements.txt")
    os.system("python3 -m pip install -r requirements.txt")
    input("\n\ndone installing modules! please restart the script now. Press enter to continue... ")
    sys.exit()

# Colors 
redBg = bg('red') 
greenBg = bg('green') 
red = fg('red') 
green = fg('green')
black = fg('black')

reset = attr('reset')

def check_username(username):
    retry = True
    while retry:
        retry = False
        result = bool(regex.search(username))
        if not (result or (len(username) < 3) or (len(username) > 16)):
            res = client.get('https://api.mojang.com/users/profiles/minecraft/' + username)
            if res.status_code == 200:
                print( red + f'{username} was taken.' + reset )
            elif res.status_code == 204:
                print( green + f'{username} is available or never used.' + reset )
                # from stackoverflow:
                # concurrent.futures.ThreadPoolExecutor allow only one thread to access the common data structure or location in memory at a time; the threading.Lock() primitive is used to manage this, so race conditions don't occur!
                available_names.append(username)
            elif res.status_code == 429:
                end_time = time.time()
                global start_time
                time_to_wait = math.ceil(200 - (end_time - start_time))
                global rate_limited
                if not rate_limited:
                    rate_limited = True
                    print( redBg + black + f'Request is being refused due to IP being rate limited. Waiting {time_to_wait} seconds before reattempting...' + reset )
                retry = True
                time.sleep(time_to_wait)
                rate_limited = False
                start_time = time.time()
            else:
                res.raise_for_status()
                print( redBg + black + f'Unhandled HTTP status code: {res.status_code}. Exiting...' + reset )
                sys.exit()
        else:
            print( red + f'{username} is an invalid username.' + reset )
            invalid_names.append(username)

filepath = sys.argv[1]
if not os.path.isfile(filepath):
    print( redBg + black + f'File path {filepath} does not exist. Exiting...' + reset )
    sys.exit()
available_names = []
invalid_names = []
with open(filepath) as name_list:
    username_list = [line.strip() for line in name_list]
    if not username_list:
        print( redBg + black + f'{filepath} is empty. Exiting...' + reset )
        sys.exit()
regex = re.compile(r'[^a-zA-Z0-9_.]')
client = requests.Session()
rate_limited = False
start_time = time.time()
with concurrent.futures.ThreadPoolExecutor() as executor:
    try:
        executor.map(check_username, username_list)
    except Exception as exc:
        print( redBg + black + f'There is a problem: {exc}. Exiting...' + reset )
        sys.exit()
print()
print( greenBg + black + f'Available username(s): {available_names}' + reset )
if invalid_names:
    print( redBg + black + f'Invalid username(s): {invalid_names}' + reset )
