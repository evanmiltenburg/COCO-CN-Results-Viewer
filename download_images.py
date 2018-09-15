import json
from time import sleep
from urllib.request import urlretrieve


def get_url_list(filename):
    "Function to get the URL"
    with open(filename) as f:
        data = json.load(f)
    return [url_generator(image['file_name']) for image in data['images']]


def download_url(url, folder='static/COCO-images/'):
    "Download a file to a particular folder."
    filename = url.split('_')[-1]
    urlretrieve(url, folder + filename)


def download_images():
    "Function to download all images, but this takes ages.."
    url_list = get_url_list('./Data/COCO/merged_captions_coco-cn_test.json')
    for i, url in enumerate(url_list):
        print('Downloading file', i, "out of", len(url_list))
        download_url(url)
        print("Downloaded.")
        sleep(2)

if __name__ == "__main__":
    download_images()
