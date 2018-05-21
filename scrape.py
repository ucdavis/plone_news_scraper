import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import json
import sys
import os
from url_normalize import url_normalize
import re

pathInfo = {}
rootDir = os.path.abspath(os.path.curdir)
map_link_to_resource = open("index.json", "w")
newsArticles = open("news.json", "w")
errors = open("errors.txt", "w")
pages_parsed = set()
agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'
opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', agent)]
urllib.request.install_opener(opener)

def scrapeNewsArticle(article):
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
	link = article.find("a")
	extension = url.split('/')[3:]
	hostname = url.split('/')[2:3][0]
	extension = "/" + ('/').join(extension)
	end = link['href']
	if not hostname in end:
		if end[0] is not "/":
			transformed = extension + "/" + link['href']
			goto = url + '/' + end
		else:
			transformed = end
			goto = "http://" + hostname + end
		link['href'] = transformed
	else:
		goto = end
		link['href'] = "/" + ('/').join(end.split('/')[3:])
	currentDirectory = os.path.abspath(os.path.curdir)
	os.chdir(rootDir)
	directory = url.split('/')[-1]
	try:
		os.makedirs(directory)
	except Exception as e:
		print(e)
	os.chdir(directory)
	newsInfo = open("news.json", "w")
	json.dump(data, newsInfo, sort_keys=True, indent=4, separators=(',', ': '))
	parse_page(goto)
	os.chdir(currentDirectory)

def parse_news(link):
	print(link)
	if link in pages_parsed:
		return
	pages_parsed.add(link)
	site = link
	directory = link.split('/')[-1]
	hdr = {'User-Agent': 'Mozilla/5.0'}
	req = urllib.request.Request(site,headers=hdr)
	try:
		page = urllib.request.urlopen(req)
	except Exception as e:
		errors.write("cannot parse page " + link + "with error: " + str(e))
		print("cannot parse page " + link + " with error: " + str(e))
		return
	if 'text/html' not in page.headers['Content-Type']:
		os.chdir(os.path.abspath('../'))
		try:
			urllib.request.urlretrieve(link, filename=directory)
		except Exception as e:
			errors.write("cannot save file at regular url" + link + " error: " + str(e))
			print("cannot save file at regular url" + link + " error: " + str(e))
		return
	hostname = link.split('/')[2:3][0]
	soup = BeautifulSoup(page, 'html.parser')
	#print soup
	try:
		html = soup.find("div", {"id": re.compile("content-core*") })
	except Exception as e:
		print(e)
		return
	try:
		os.makedirs(directory)
	except Exception as e:
		print(e)
	os.chdir(directory)
	try:
		items = html.find_all('div', {"class":"tileItem"})
	except Exception as e:
		print("not a content page " + str(e))
		return
	for article in items:
		scrapeNewsArticle(article)
	dirObject = {}
	dirObject["path"] = link
	try:
		titleName = soup.find(attrs={"id": re.compile("parent-fieldname-title*") })
		dirObject["title"] = titleName.string.strip('\n')
	except Exception as e:
		print(e)
	pathInfo[directory] = dirObject

def parse_page(link):
	print(link)
	if link in pages_parsed:
		return
	pages_parsed.add(link)
	site = link
	hdr = {'User-Agent': 'Mozilla/5.0'}
	directory = link.split('/')[-1]
	req = urllib.request.Request(site,headers=hdr)
	try:
		page = urllib.request.urlopen(req)
	except Exception as e:
		errors.write("cannot parse page " + link + "with error: " + str(e))
		print("cannot parse page " + link + " with error: " + str(e))
		return
	if 'text/html' not in page.headers['Content-Type']:
		os.chdir(os.path.abspath('../'))
		try:
			urllib.request.urlretrieve(link, filename=directory)
		except Exception as e:
			errors.write("cannot save file at regular url" + link + " error: " + str(e))
			print("cannot save file at regular url" + link + " error: " + str(e))
		return
	hostname = link.split('/')[2:3][0]
	soup = BeautifulSoup(page, 'html.parser')
	#print soup
	try:
		html = soup.find("div", {"id": re.compile("parent-fieldname-text*") })
	except Exception as e:
		print(e)
		return
	try:
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
			errors.write(str(link) + ": " + str(image_link)+"\n")
	
	output = open("index.html", "wb")
	dirObject = {}
	dirObject["path"] = link
	try:
		titleName = soup.find(attrs={"id": re.compile("parent-fieldname-title*") })
		dirObject["title"] = titleName.string.strip('\n')
	except Exception as e:
		print(e)
	pathInfo[directory] = dirObject
	output.write(html.encode())
	output.close()

if __name__ == '__main__':
	if len(sys.argv) < 1:
		raise AttributeError("please call with a url") 
	parse_news(sys.argv[1])
	json.dump(pathInfo, map_link_to_resource, sort_keys=True, indent=4, separators=(',', ': '))
	map_link_to_resource.close()
	newsArticles.close()