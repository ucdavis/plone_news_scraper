import urllib.request, urllib.error, urllib.parse
import requests
from bs4 import BeautifulSoup
import json
import sys
import os
from url_normalize import url_normalize
from collections import deque
import re
import plone_login
import http.cookiejar
import argparse

agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'

class URLFilter:
	def __init__(self, link, args):
		self.link = link
		self.subtree = args.subtree
		self.whitelistEnabled = args.whitelist is not None
		if self.whitelistEnabled:
			self.whitelist = re.compile(args.whitelist)
	def filter(self, link):
		if self.subtree and self.link not in link:
			return False
		if self.whitelistEnabled and self.whitelist.match(link) is None:
			return False
		return True

class Parser:
	def __init__(self, urlFilter):
		self.pathInfo = {}
		self.rootDir = os.path.abspath(os.path.curdir)
		self.map_link_to_resource = open("index.json", "w")
		self.errors = open("errors.txt", "w")
		self.pages_parsed = set()
		self.cookie = http.cookiejar.CookieJar()
		self.build_opener()
		self.links = deque()
		self.filter = urlFilter.filter

		try:
			os.makedirs(self.rootDir + "/articles")
		except Exception as e:
			pass

		try:
			os.makedirs(self.rootDir + "/files")
		except Exception as e:
			pass

		try:
			os.makedirs(self.rootDir + "/news")
		except Exception as e:
			pass

	def loop(self):
		while len(self.links) > 0:
			link = self.links.popleft()
			self.parse(*link)

	def build_opener(self):
		opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookie))
		opener.addheaders = [('User-agent', agent)]
		urllib.request.install_opener(opener)

	def manageFile(self, relative):
		def useLink(link):
			hostname = link.split('/')[2:3][0]
			if hostname not in relative['href']:
				download_file = url_normalize(link + "/" + relative['href'])
				name = relative['href'].replace("/","").replace("../", "")
			else:
				download_file = relative['href']
				name = relative['href'].split('/')[-1].replace("/","").replace("../", "")

			while os.path.isfile(name):
				(root, ext) = os.path.splitext(name)
				name = root + "(1)" + ext
			try:
				urllib.request.urlretrieve(download_file, filename=name)
			except urllib.error.HTTPError as e:
				print("file download not working: " + download_file)
				print(e)
				self.errors.write("file download not working: " + download_file+"\n")
		return useLink

	def manageLink(self, relative):
		def useLink(link):
			extension = link.split('/')[3:]
			hostname = link.split('/')[2:3][0]
			extension = "/" + ('/').join(extension)
			end = relative['href']
			if not hostname in end:
				if end[0] is not "/":
					transformed = extension + "/" + relative['href']
					goto = link + '/' + end
				else:
					transformed = end
					goto = "http://" + hostname + end
				relative['href'] = transformed
			else:
				goto = end
				relative['href'] = "/" + ('/').join(end.split('/')[3:])
			self.links.append((goto,))
		return useLink

	def doNothing(self, *args):
		if args is not None and args[0] is not None: 
			self.errors.write("doing nothing for" + str(args[0]) + "\n")
			print("doing nothing for" + str(args[0]) + "\n")
		return self.doNothing

	def chooseLinkOption(self, relative):
		if ".mp4" in relative['href']:
			return self.doNothing
		if "." in relative['href'].split('/')[-1] or "files" in relative['href']:
			return self.manageFile(relative)
		return self.manageLink(relative)
	def cdExecute(self, directory, func):
		result = None
		currentDirectory = os.path.abspath(os.path.curdir)
		try:
			os.makedirs(directory)
		except Exception as e:
			pass
		os.chdir(directory)
		try:
			result = func()
		except Exception as e:
			print(e)
		os.chdir(currentDirectory)
		return result

	def scrapeNewsArticle(self, article, curURL):
		data = {}
		tileHeadline = article.find("h2", {"class": "tileHeadline"})
		data["headline"] = tileHeadline.find("a").decode_contents()
		url = tileHeadline.find("a", {"class": "url"})["href"]
		try:
			author = article.find('span', {"class": "documentByLine"})
			data["author"] = author.find("span").find("a").decode_contents()
			data["author-link"] = author.find("span").find("a")["href"]
		except Exception as e:
			print(e)
		try:
			data["description"] = article.find('span', {"class": "description"}).decode_contents()
		except Exception as e:
			print(e)
		goto = urllib.parse.urljoin(curURL, url)
		directory = url.split('/')[-1]
		def parseArticle():
			newsInfo = open("news.json", "w")
			image_link = None
			try:
				image = article.find("img", {"class": "tileImage"})
				image_link = image.get('src')
				if not "https://" or not "http://" in image_link:
					image_link = urllib.parse.urljoin(curURL, image_link)
				path = urllib.request.urlopen(image_link)
				filename = path.url.split('/')[-1]
				if filename is 'thumb' or filename is 'preview' or filename is 'mini':
					print('url not getting translated: ' + path.url)
				image['alt'] = filename
				while os.path.isfile(filename):
					(root, ext) = os.path.splitext(filename)
					filename = root + "(1)" + ext
				urllib.request.urlretrieve(image_link, filename=filename)
			except Exception as e:
				print("image link not working: " + str(image_link))
				print(e)
				self.errors.write(str(image_link)+"\n")
			json.dump(data, newsInfo, sort_keys=True, indent=4, separators=(',', ': '))
			self.links.append((goto, False))
			pass
		self.cdExecute(directory, parseArticle)

	def login(self, link, *args):
		if not len(sys.argv) > 3:
			return None
		hostname = link.split('/')[2:3][0]
		auth_cookie = plone_login.get_session_cookie("http://" + hostname, sys.argv[2], sys.argv[3])
		for k, v in auth_cookie.items():
			new_cookie = requests.cookies.create_cookie(k, v)
			self.cookie.set_cookie(new_cookie)

		self.build_opener()
		return "login"

	def getPage(self, link):
		directory = link.split('/')[-1]
		hdr = {'User-Agent': 'Mozilla/5.0'}
		req = urllib.request.Request(link, headers=hdr)
		try:
			page = urllib.request.urlopen(req)
			if page.url is not link:
				print(page.url + " is not " + link)
				result = self.parse(page.url)
				if result is "login":
					page = urllib.request.urlopen(req)

		except Exception as e:
			if len(sys.argv) >= 4:
				try:
					self.login(link)
					page = urllib.request.urlopen(req)
				except Exception as e:
					hostname = link.split('/')[2:3][0]
					print("can't login to " + hostname)
					self.errors.write("cannot parse page " + link + "with error: " + str(e))
					print("cannot parse page " + link + " with error: " + str(e))
					return None
			else:
				self.errors.write("cannot parse page " + link + "with error: " + str(e))
				print("cannot parse page " + link + " with error: " + str(e))
				return None
		if 'text/html' not in page.headers['Content-Type']:
			try:
				urllib.request.urlretrieve(link, filename=(self.rootDir + "/files/" + directory + ".pdf"))
			except Exception as e:
				self.errors.write("cannot save file at regular url " + link + " error: " + str(e))
				print("cannot save file at regular url" + link + " error: " + str(e))
			return None
		return page

	def parse(self, link, *args):
		if not self.filter(link):
			return None
		if link in self.pages_parsed:
			return None
		self.pages_parsed.add(link)
		page = self.getPage(link)
		if page is None:
			return self.doNothing(link)
		soup = BeautifulSoup(page, 'html.parser')
		body = soup.find("body")
		if body.get("class") is None:
			return self.doNothing(link, *args)
		if "portaltype-collection" in body.get("class") or "":
			return self.cdExecute(self.rootDir + "/news", lambda: self.parse_news(link, *args))
		if "portaltype-folder" in body.get("class"):
			return self.cdExecute(self.rootDir + "/files", lambda: self.parse_files(link, *args))
		# TODO improve pattern matchin
		if "portaltype-document" in body.get("class"):
			return self.cdExecute(self.rootDir + "/articles", lambda: self.parse_page(link, *args))
		if "portaltype-news-item" in body.get("class"):
			return self.cdExecute(self.rootDir + "/news", lambda: self.parse_page(link, *args))
		if "template-login_form" in body.get("class"):
			return self.login(link, *args)
		if "portaltype-fsdperson" in body.get("class"):
			return self.cdExecute(self.rootDir + "/people", lambda: self.parse_person(link, *args))
		if "portaltype-fsdfacultystaffdirectory" in body.get("class"):
			return self.cdExecute(self.rootDir + "/people", lambda: self.parse_people(link, *args))

		return self.doNothing(link, *args)
		
	def parse_files(self, link, num=1, *args):	
		page = self.getPage(link)
		if page is None:
			return
		print(link)
		hostname = link.split('/')[2:3][0]
		soup = BeautifulSoup(page, 'html.parser')

		try:
			html = soup.find("div", {"id": re.compile("content-core*") })
		except Exception as e:
			print(e)
			return
		try:
			links = html.find_all('a', {"class":"contenttype-file"})
			links = html.find_all('a', {"class":"url"})
		except Exception as e:
			print("not a content page " + str(e))
			return

		for href in links:
			self.chooseLinkOption(href)(link)

		self.handle_listing(html, num)

	def handle_listing(self, htmlSoup, num):
		try:
			listing = htmlSoup.find('div', {"class":"listingBar"})
			pages = listing.find_all("a")
			index = num - 1
			if listing.find("span", {"class": "previous"}) is not None:
				index += 1
			if listing.find("span", {"class": "next"}) is not None:
				index += 1
			otherpage = pages[index]
			self.links.append((otherpage["href"], num + 1))
		except Exception as e:
			print("can't find any more files, quitting", str(e))

	def parse_news(self, link, num=1, *args):
		page = self.getPage(link)
		if page is None:
			return
		print(link)
		soup = BeautifulSoup(page, 'html.parser')
		#print soup
		try:
			html = soup.find("div", {"id": re.compile("content-core*") })
		except Exception as e:
			print(e)
			return
		try:
			items = html.find_all('div', {"class":"tileItem"})
		except Exception as e:
			print("not a content page " + str(e))
			return
		for article in items:
			self.scrapeNewsArticle(article, link)
		os.chdir(os.path.abspath("../"))
		
		self.handle_listing(html, num)

	def parse_people(self, link, *args):
		page = self.getPage(link)
		if page is None:
			return
		print(link)
		soup = BeautifulSoup(page, 'html.parser')
		#print soup
		try:
			html = soup.find("div", {"id": re.compile("totalcontent") })
		except Exception as e:
			print(e)
			return
		try:
			items = [element.find('a') for element in html.find_all('div', {"class":"moreInfo"})]
		except Exception as e:
			print("not a content page " + str(e))
			return
		for person in items:
			self.links.append((person['href'],))

	def parse_person(self, link, *args):
		page = self.getPage(link)
		if page is None:
			return
		print(link)
		soup = BeautifulSoup(page, 'html.parser')
		directory = link.split('/')[-1]

		try:
			os.makedirs(directory)

		except Exception as e:
			print(e)
			try:
				directory = link.split('/')[-2] + '-' + directory
				os.makedirs(directory)
			except Exception as e:
				print(e)
				return

		os.chdir(directory)
		#print soup
		try:
			info = {}

			html = soup.find("div", {"class": "biography" })
			given_name = soup.find("span", {"class": "given-name"}).get_text()
			middle_name = soup.find("span", {"class": "additional-name"}).get_text()
			family_name = soup.find("span", {"class": "family-name"}).get_text()
			honorary_suffix = soup.find("span", {"class": "honorific-suffix"}).get_text()

			info["name"] = (" ").join([string for string in [given_name, middle_name, family_name, honorary_suffix] if len(string) > 0])

			address = soup.find("span", {"class": "street-address"}).get_text()

			if address and len(address) > 0:
				info["address"] = address

			phone_div = soup.find("span", {"class": ["tel", "officePhone"]})

			if phone_div:
				phone_number = phone_div.find("span", {"class": "value"}).get_text()
				if phone_number and len(phone_number) > 0:
					info["phone"] = phone_number

			email_span = soup.find("span", {"class": "email"})

			if email_span:
				email = email_span.find("a").get_text()
				if email and len(email) > 0:
					info["email"] = email

			title = [t.get_text() for t in soup.find_all("p", {"class": "title"})]
			info["title"] = title
			
			if html:
				with open("index.html", "wb") as output:
					output.write(html.encode())

			with open("person.json", "w") as person_file:
				json.dump(info, person_file, sort_keys=True, indent=4, separators=(',', ': '))

			headshot = soup.find("div", {"class": "headshot"})
			
			if headshot:
				face = soup.find("img", {"class": "photo"})
				self.handle_image(face, link)

		except Exception as e:
			print(e)
			return
		
	def handle_image(self, image, pageLink):
		image_link = image.get('src')
		hostname = pageLink.split('/')[2:3][0]

		try:
			if not "https://" or not "http://" in image_link:
				image_link = url_normalize(pageLink + "/" + image_link)
				path = urllib.request.urlopen(image_link)
				if '@@images' in path.url:
					filename = path.url.split('/')[-4]
				else:
					filename = path.url.split('/')[-1]
				if filename is 'thumb' or filename is 'preview' or filename is 'mini':
					print('url not getting translated: ' + path.url)
				image['alt'] = filename
				while os.path.isfile(filename):
					(root, ext) = os.path.splitext(filename)
					filename = root + "(1)" + ext
				urllib.request.urlretrieve(image_link, filename=filename)

			elif hostname in image_link:
				path = urllib.request.urlopen(image_link)
				if '@@images' in path.url:
					filename = path.url.split('/')[-3]
				else:
					filename = path.url.split('/')[-1]
				if filename is 'thumb' or filename is 'preview' or filename is 'mini':
					print('url not getting translated: ' + path.url)
				image['alt'] = filename
				while os.path.isfile(filename):
					(root, ext) = os.path.splitext(filename)
					filename = root + "(1)" + ext
				urllib.request.urlretrieve(image_link, filename=filename)
				
		except Exception as e:
			print(e)
			print("image link not working: " + str(pageLink) + ": " + str(image_link))
			self.errors.write(str(pageLink) + ": " + str(image_link)+"\n")

	def parse_page(self, link, *args):
		page = self.getPage(link)
		if page is None:
			return
		print(link)
		hostname = link.split('/')[2:3][0]
		soup = BeautifulSoup(page, 'html.parser')
		directory = link.split('/')[-1]

		makedir = True
		if len(args) > 0:
			makedir = args[0]

		if makedir:
			try:
				os.makedirs(directory)
			
			except Exception as e:
				print(e)
				try:
					directory = link.split('/')[-2] + '-' + directory
					os.makedirs(directory)
				except Exception as e:
					print(e)

		os.chdir(directory)
		#print soup
		try:
			html = soup.find("div", {"id": re.compile("parent-fieldname-text*") })
		except Exception as e:
			print(e)
			return
		try:
			links = soup.find_all('a', {"class":"internal-link"})
			links += soup.find_all('a', {"class": "contenttype-link"})
			links += soup.find_all('a', {"class": "contenttype-document"})
			links += soup.find_all('a', {"class": "contenttype-folder"})
			links += soup.find('header').find('nav').find_all('a')
			links += [item for item in html.find_all('a', {"href": re.compile(hostname)}) if not ("class" in item.attrs and "internal-link" in item.attrs['class'])]
			images = html.find_all('img')
		except Exception as e:
			print("not a content page " + str(e))
			return
		for image in images:
			self.handle_image(image, link)

		for href in links:
			if href['href'].split('/')[-1] is "":
				href['href'] = href['href'][:-1]
			self.chooseLinkOption(href)(link)

		output = open("index.html", "wb")
		meta = {}
		meta["link"] = link
		dirObject = {}
		dirObject["path"] = directory
		try:
			titleName = soup.find(attrs={"id": re.compile("parent-fieldname-title*") })
			meta["title"] = titleName.string.strip('\n ')
			dirObject["title"] = titleName.string.strip('\n ')
		except Exception as e:
			print(e)

		try:
			description = soup.find(attrs={"id": re.compile("parent-fieldname-description") })
			meta["description"] = description.string.strip('\n ')
		except Exception as e:
			pass

		self.pathInfo[directory] = dirObject
		output.write(html.encode())
		output.close()
		with open("meta.json", "w") as outputMetaFile:
			json.dump(meta, outputMetaFile, sort_keys=True, indent=4, separators=(',', ': '))


argparser = argparse.ArgumentParser(description='Download a plone website')
argparser.add_argument('url', type=str)
argparser.add_argument('-u', type=str, dest='username', 
					help='username')
argparser.add_argument('-p', dest='password', type=str,
                    help='password')
argparser.add_argument('--whitelist', dest='whitelist', type=str)
argparser.add_argument('--subtree', dest="subtree", action="store_true")

if __name__ == '__main__':
	if len(sys.argv) < 1:
		raise AttributeError("please call with a url") 
	args = argparser.parse_args()
	urlFilter = URLFilter(sys.argv[1], args)
	parser = Parser(urlFilter)
	parser.links.append((sys.argv[1],))
	parser.loop()
	json.dump(parser.pathInfo, parser.map_link_to_resource, sort_keys=True, indent=4, separators=(',', ': '))
	parser.map_link_to_resource.close()