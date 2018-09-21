import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import json
import sys
import os
from url_normalize import url_normalize
import re

agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'

class Parser:
	def __init__(self):
		self.pathInfo = {}
		self.rootDir = os.path.abspath(os.path.curdir)
		self.map_link_to_resource = open("index.json", "w")
		self.errors = open("errors.txt", "w")
		self.pages_parsed = set()
		opener = urllib.request.build_opener()
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
			self.cdExecute(self.rootDir, lambda: self.parse_page(goto))
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
		currentDirectory = os.path.abspath(os.path.curdir)
		try:
			os.makedirs(directory)
		except Exception as e:
			pass
		os.chdir(directory)
		try:
			func()
		except Exception as e:
			print(e)
		os.chdir(currentDirectory)

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
			self.parse_page(goto)
			pass
		self.cdExecute(directory, parseArticle)

	def getPage(self, link):
		directory = link.split('/')[-1]
		hdr = {'User-Agent': 'Mozilla/5.0'}
		req = urllib.request.Request(link,headers=hdr)
		try:
			page = urllib.request.urlopen(req)
		except Exception as e:
			self.errors.write("cannot parse page " + link + "with error: " + str(e))
			print("cannot parse page " + link + " with error: " + str(e))
			return None
		if 'text/html' not in page.headers['Content-Type']:
			try:
				urllib.request.urlretrieve(link, filename=directory)
			except Exception as e:
				self.errors.write("cannot save file at regular url" + link + " error: " + str(e))
				print("cannot save file at regular url" + link + " error: " + str(e))
			return None
		return page

	def parse(self, link):
		page = self.getPage(link)
		if page is None:
			return self.doNothing(link)
		if link in self.pages_parsed:
			return None
		self.pages_parsed.add(link)
		soup = BeautifulSoup(page, 'html.parser')
		body = soup.find("body")
		if body.get("class") is None:
			return self.doNothing(link)
		if "portaltype-collection" in body.get("class"):
			return self.parse_news(link)
		# TODO improve pattern matchin
		if "portaltype-document" in body.get("class") or "portaltype-news-item" in body.get("class"):
			return self.parse_page(link)
		return self.doNothing(link)
		

	def parse_news(self, link, num=1):
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
		try:
			os.makedirs(os.path.abspath("./news"))
		except Exception as e:
			pass
		os.chdir(os.path.abspath("./news"))
		for article in items:
			self.scrapeNewsArticle(article, link)
		os.chdir(os.path.abspath("../"))
		try:
			listing = html.find('div', {"class":"listingBar"})
			pages = listing.find_all("a")
			index = num - 1
			if listing.find("span", {"class": "previous"}) is not None:
				index += 1
			if listing.find("span", {"class": "next"}) is not None:
				index += 1
			otherpage = pages[index]
			self.parse_news(otherpage["href"], num + 1)
		except Exception as e:
			print("can't find any more news, quitting", str(e))

	def parse_page(self, link):
		page = self.getPage(link)
		if page is None:
			return
		print(link)
		hostname = link.split('/')[2:3][0]
		soup = BeautifulSoup(page, 'html.parser')
		#print soup
		try:
			html = soup.find("div", {"id": re.compile("parent-fieldname-text*") })
		except Exception as e:
			print(e)
			return
		try:
			links = html.find_all('a', {"class":"internal-link"})
			links += [item for item in html.find_all('a', {"href": re.compile(hostname)}) if not ("class" in item.attrs and "internal-link" in item.attrs['class'])]
			images = html.find_all('img')
		except Exception as e:
			print("not a content page " + str(e))
			return
		for image in images:
			
			image_link = image.get('src')
			try:
				if not "https://" or not "http://" in image_link:
					image_link = url_normalize(link + "/" + image_link)
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
			except:
				print("image link not working: " + str(link) + ": " + str(image_link))
				self.errors.write(str(link) + ": " + str(image_link)+"\n")
		for href in links:
			self.chooseLinkOption(href)(link)

		output = open("index.html", "wb")
		dirObject = {}
		dirObject["path"] = link
		try:
			titleName = soup.find(attrs={"id": re.compile("parent-fieldname-title*") })
			dirObject["title"] = titleName.string.strip('\n')
		except Exception as e:
			print(e)
		directory = link.split('/')[-1]
		self.pathInfo[directory] = dirObject
		output.write(html.encode())
		output.close()

if __name__ == '__main__':
	if len(sys.argv) < 1:
		raise AttributeError("please call with a url") 
	parser = Parser()
	parser.parse(sys.argv[1])
	json.dump(parser.pathInfo, parser.map_link_to_resource, sort_keys=True, indent=4, separators=(',', ': '))
	parser.map_link_to_resource.close()