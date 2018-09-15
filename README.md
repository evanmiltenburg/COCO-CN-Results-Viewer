# COCO-CN output inspector
This is a lightweight tool to inspect the results of different image description
systems on the COCO-CN test set. It automatically downloads the images as you
browse through the results. This saves you from having to download *all* the
images in the dataset. I've also provided a script to download the images, if you
need to work offline.

## Requirements

* Python 3.6
* Flask 0.12

Other versions may work, but remain untested. I recommend [downloading Anaconda](https://www.anaconda.com/download/).

## How to run this tool

To run the tool, just use `python resultsviewer.py` on the command line.
If you want to download the images first, run `python download_images.py` and wait for the script to complete. This may take a long time.

## Contact
* Tool: Emiel van Miltenburg, Tilburg University
* Data: Xirong Li, Renmin University of China
