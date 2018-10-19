import requests
import sys
from bs4 import BeautifulSoup

agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'


def get_session_cookie(url, username, password):
    login = requests.post(url + "/login_form", data={'__ac_name': username, 
                                                    '__ac_password': password,
                                                    'ajax_include_head': "",
                                                    'ajax_load':"",
                                                    'came_from':"",
                                                    'cookies_enabled':"",
                                                    'form.submitted':1,
                                                    'join_url':"",
                                                    'js_enabled':0,
                                                    'login_name':"",
                                                    'mail_password_url':"",
                                                    'next':"",
                                                    'pwd_empty':0,
                                                    'submit':"Log+in",
                                                    'target':""})
    if login.status_code == 200:
        return login.cookies
    raise ValueError("Wrong password or username")
    

if __name__ == "__main__":
    url = "http://asi.ucdavis.edu"
    cookie = get_session_cookie(url, sys.argv[1], sys.argv[2])
    print(cookie)