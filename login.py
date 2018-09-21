import requests
import sys
from bs4 import BeautifulSoup

agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'


def get_session_cookie(url, username, password):
    admin = requests.get(url + "/caslogin")
    soup = BeautifulSoup(admin.text, 'html.parser')
    execute = soup.find(name="input", attrs={'name': "execution"})
    login = requests.post(admin.url, cookies=admin.cookies, data={'execution': execute["value"], 'username': username, 'password': password, 'submit': "LOGIN", "_eventId": "submit"}, allow_redirects=False)
    if login.status_code == 302:
        step2 = login.headers["Location"]
        final = requests.get(step2, cookies=login.cookies, allow_redirects=False)
        if final.status_code == 302:
            return final.cookies
    raise ValueError("Wrong password or username")
    

if __name__ == "__main__":
    url = "http://ffhi.ucdsitefarm.acsitefactory.com"
    cookie = get_session_cookie(url, sys.argv[1], sys.argv[2])
    admin = requests.get(url + "/admin/content", cookies=cookie)
    print(admin.status_code)
    if admin.status_code is 200:
        print("Login OK!")