# Stdlib
import json
import os
import glob
from collections import defaultdict
from urllib.request import urlretrieve

# Installed
from flask import Flask, request, render_template, redirect, make_response

################################################################################
# Functions to load the data.

def load_system_output(filename):
    "Load system output as a dictionary: imgid: description."
    with open(filename) as f:
        system = json.load(f)
    return {imgid: system['imgToEval'][imgid]['caption'][0]['caption']
            for imgid in system['imgToEval']}


def get_scores_subdict(d):
    "Extract only the metric scores from a dict."
    metrics = ['CIDEr', 'Bleu_4', 'Bleu_3', 'Bleu_2', 'Bleu_1', 'ROUGE_L', 'METEOR']
    return dict((k,d[k]) for k in metrics)


def load_system_scores(filename):
    "Create an index of the form {imgid: {cider:score, meteor:score, ...}, ...}"
    with open(filename) as f:
        system = json.load(f)
    return {imgid: get_scores_subdict(system['imgToEval'][imgid]) for imgid in system['imgToEval']}


def load_all_system_scores(system_files):
    score_data = {system: load_system_scores(filename)
                  for system, filename in system_files.items()}
    system_scores_by_images = defaultdict(list)
    for system, index in score_data.items():
        for image_id, results in index.items():
            system_scores_by_images[image_id].append((system, results))
    return system_scores_by_images
    

def load_human_data(filename):
    "Load the human descriptions."
    with open(filename) as f:
        data = json.load(f)
    description_index = defaultdict(list)
    for image in data['annotations']:
        key = str(image['image_id'])
        caption = image['caption']
        description_index[key].append(caption)
    return description_index


def url_generator(filename):
    "Function to generate URLs for different filenames."
    if 'train2014' in filename:
        return 'http://images.cocodataset.org/train2014/' + filename
    elif 'val2014' in filename:
        return 'http://images.cocodataset.org/val2014/' + filename
    else:
        return None


def load_image_data(filename):
    "Load the image URLs and filenames."
    with open(filename) as f:
        data = json.load(f)
    return {str(image['id']): {'url': url_generator(image['file_name']),
                               'filename': image['file_name']}
            for image in data['images']}


def load_all_systems(system_files):
    "Load system data by images: {imgid: {system: caption, ...}, ...}"
    system_data = {system: load_system_output(filename)
                    for system,filename in system_files.items()}
    system_data_by_images = defaultdict(dict)
    for system, index in system_data.items():
        for image_id, caption in index.items():
            system_data_by_images[image_id][system] = caption
    return system_data_by_images


def download_url(url, folder='./static/COCO-images/'):
    "Download a file to a particular folder."
    filename = url.split('/')[-1]
    local_filename, headers = urlretrieve(url, folder + filename)
    print('Downloaded:', local_filename)
    print('Headers:', headers)

################################################################################
# Loading the data.

system_files = {filename.split('_')[-1][:-4]: filename
                for filename in glob.glob('./Data/Systems/*.txt')}

human_data = load_human_data('./Data/COCO/merged_captions_coco-cn_test.json')
image_data = load_image_data('./Data/COCO/merged_captions_coco-cn_test.json')
system_data = load_all_systems(system_files)
system_scores = load_all_system_scores(system_files)

imgids = list(image_data)
first_id = imgids[0]
max_index = len(imgids) - 1

################################################################################
# Global variables to make search possible.
search        = False
query         = ''
result_ids    = []
before_search = first_id

################################################################################
# Set up app:
app = Flask(__name__)

################################################################################
# Main browsing functionality.

@app.route('/')
def main():
    "Main page redirects to the first item to be annotated."
    page = '/item/' + first_id
    return redirect(page)


@app.route('/item/<imgid>')
def item_page(imgid):
    """
    Serve the item page.
    """
    # Assess whether there is an image before or after the current page.
    current_index = imgids.index(imgid)
    if current_index > 0:
        previous = '/item/' + imgids[current_index -1]
    else:
        previous = None
    if current_index < max_index:
        next = '/item/' + imgids[current_index + 1]
    else:
        next = None
    
    # Get data to display
    human_captions = human_data[imgid]
    system_captions = system_data[imgid]
    scores = system_scores[imgid]
    image = image_data[imgid]['filename']
    
    print(scores)
    
    # Check if the image exists. If not, download it.
    if not os.path.isfile('./static/COCO-images/' + image):
        print("We need to download the image!")
        url = image_data[imgid]['url']
        download_url(url)
    return render_template('index.html',
                            imgid=imgid,
                            humans=human_captions,
                            systems=system_captions,
                            image='/static/COCO-images/' + image,
                            next_page=next,
                            previous_page=previous,
                            system_scores=scores
                            )

################################################################################
# Running the website

if __name__ == '__main__':
    app.debug = True
app.run(threaded=True)
