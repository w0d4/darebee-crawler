from bs4 import BeautifulSoup
import requests
import urllib.request
import time
import pickle
import json
import shutil

base_url = "https://darebee.com"
pagination_url = "https://darebee.com/workouts.html?start="
downloaded_images = []
user_agent = 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
headers = { 'User-Agent': user_agent }


def get_current_ip():
	r = requests.get("https://ipinfo.io")
	answer = json.loads(str(r.text))
	current_ip = answer["ip"]
	return current_ip


def get_overview_page(pagination_number):
	global headers
	site = requests.get(pagination_url+str(pagination_number), headers=headers)
	soup = BeautifulSoup(site.text, "lxml")
	images = soup.find_all('img', itemprop="thumbnailUrl")
	return images


def download_images(images):
	global downloaded_images
	global user_agent
	for image in images:
		img_url = base_url+image['src'].replace("-intro","")
		print(img_url)
		filename = img_url.split("/")[-1]
		if filename in downloaded_images:
			print(f"{filename} was already downloaded")
			continue
		#urllib.request.urlretrieve(img_url, "archive/"+filename, headers=headers)
		req = urllib.request.Request(img_url)
		req.add_header('Referer', 'https://darebee.com/workouts.html')
		req.add_header('User-Agent', user_agent)
		with urllib.request.urlopen(req) as response, open("archive/"+filename, 'wb') as out_file:
			shutil.copyfileobj(response, out_file)
		downloaded_images.append(filename)
		with open('archive.txt', 'wb') as file:
			pickle.dump(downloaded_images, file)


def main():
	global downloaded_images
	print(f"Currently working with IP {get_current_ip()}")
	try:
		with open('archive.txt', 'rb') as file:
			downloaded_images = pickle.load(file)
	except FileNotFoundError:
		print("Cannot find archive file. Will start archiving everything")
		pass
	pagination = 0
	while True:
		images = get_overview_page(pagination)
		if len(images) == 0:
			break
		download_images(images)
		pagination = pagination + 15
		time.sleep(10)


if __name__ == "__main__":
    main()
