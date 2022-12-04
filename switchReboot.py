import requests
import hashlib
import random
from bs4 import BeautifulSoup


## Set Url, Set Password. Should be kept in a seperate file.

loginUrl = 'http://yourIPhere/login.cgi'
rebootHTML = 'http://yourIPhere/device_reboot.htm'
rebootCGI = 'http://1yourIPhere/device_reboot.cgi'
switchpassword = ''

###############################################################################################

## Function for combining strings, creates a merge (abc, 123 -> a1b2c3)

def merge(str1, str2):
    arr1 = list(str1)
    arr2 = list(str2)
    result = ""
    index1 = 0
    index2 = 0
    while ((index1 < len(arr1)) or (index2 < len(arr2))):
        if(index1 < len(arr1)):
            result += arr1[index1]
            #print("part1")
            index1 = index1+1
        if(index2 < len(arr2)):
            result += arr2[index2]
            index2 = index2+1
    #print(result)
    return result

###############################################################################################

def main():
    ## Session GET request for gathering div information.

    with requests.session() as session:
        response = session.get(loginUrl)


    ## Specifify sorting gathered html with 'lxml', search for the 'rand' property. This is generated on a given 
    ## interval, or after a reboot. Interval not known.


    soup = BeautifulSoup(response.text, features='lxml')
    rand = (soup.find("input", type="hidden", attrs={"name": "rand"})["value"])


    ## Use merge function to replicate merge function on web page. Print for debug.

    resultStr = merge(switchpassword, rand)
    #print(resultStr)


    ## Page uses basic md5 hash of mixed string. Print for debug.

    md5 = hashlib.md5(resultStr.encode())

    password = md5.hexdigest()
    
    #print(password)


    ## Session POST request to send to .cgi page. .cgi pages are always input, this requires redirect rule
    ## and specification of data content type. Print for debug.


    p = requests.post(
            loginUrl, 
            data=(f'password={password}'), 
            allow_redirects=True,
            headers={'X-Requested-With': 'Python requests', 'Content-type': 'text/xml'}
        )
    #print(p.text)
    #print(p.cookies)


    ## Save html of redirected (or not) web page to html, rather than looking through terminal.

    with open('index.html', 'w') as f:
        f.write(p.text)
    
        

    ## Looks through response from POST request to confirm password worked successfully.

    text = 'The password is invalid.'
    if text in p.text:
        print('Wrong Password!')
        exit()

    text2 = "Your account is temporarily locked."
    if text2 in p.text:
        print('Wait for timeout.')
    
    cookie = p.cookies

    return cookie

###############################################################################################

    ## Assigns cookie from POST of last session.
def reboot():

        cooky = main()
        #print(cooky)

        ## Gathers html of device_reboot.htm

        with requests.session() as session:
            r = session.get(rebootHTML, cookies=cooky)
            
        #print(r.text)


        ## Gathers hash of reboot.htm checkbox.

        soup = BeautifulSoup(r.text, features='lxml')
        checkHash = (soup.find("input", type="hidden", attrs={"name": "hash"})["value"])
        #print(checkHash)

        ## POST request with url, binary data (checkbox on + hash), redirects, and cookies.

        re = requests.post(
                rebootCGI, 
                data=(f'CBOX=on&hash={checkHash}'), 
                allow_redirects=True,
                headers={'X-Requested-With': 'Python requests', 'Content-type': 'text/xml'},
                cookies=cooky
            )
        
        if 'The device is restarting.' in re.text:
            print('Rebooting.')

if __name__ == '__main__':
    reboot()
