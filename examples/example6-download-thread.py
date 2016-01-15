# example6-download-thread.py - download json and all full-size images from a thread
from __future__ import print_function
import py8chan
import sys
import os
import requests
import json

def mkdirs(path):
    """Make directory, if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)

def download_file(local_filename, url, clobber=False):
    """Download the given file. Clobber overwrites file if exists."""
    dir_name = os.path.dirname(local_filename)
    mkdirs(dir_name)

    if clobber or not os.path.exists(local_filename):
        i = requests.get(url)

        # if not exists
        if i.status_code == 404:
            print('Failed to download file:', local_filename, url)
            return False

        # write out in 1MB chunks
        chunk_size_in_bytes = 1024*1024  # 1MB
        with open(local_filename, 'wb') as local_file:
            for chunk in i.iter_content(chunk_size=chunk_size_in_bytes):
                local_file.write(chunk)

    return True

def download_json(local_filename, url, clobber=False):
    """Download the given JSON file, and pretty-print before we output it."""
    
    # write reformatted json
    with open(local_filename, 'w') as json_file:
        json_data = download_file(local_filename, url, clobber)
        json_file.write(json.dumps(json_data, sort_keys=True, indent=2, separators=(',', ': ')))

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Quick and dirty 8chan Archiver")
        print("%s - Save the JSON and all images for an 8chan post." % (sys.argv[0]))
        print("\tUsage: %s <board> <thread_id>" % (sys.argv[0]))
        sys.exit(1)
    
    board_name = sys.argv[1]
    thread_id = sys.argv[2]
    
    # grab the first thread on the board by checking first page
    board = py8chan.Board(board_name)
    thread = board.get_thread(thread_id)
    
    # create folders according to chan.arc standard
    path = os.path.join(os.getcwd(), "8chan", board_name, thread_id)
    images_path = os.path.join(path, "images")
    mkdirs(images_path)

    # archive the thread JSON
    json_url = py8chan.Url.thread_api_url(board_name, thread_id)
    download_json(os.path.join(path, "%s.json" % thread_id), json_url)

    # record the url of every file on the first thread, even extra files in posts
    for img in thread.file_objects():
        print("Downloading %s..." % img.file_url)
        download_file(os.path.join(images_path, "%s" % img.filename), img.file_url)

if __name__ == '__main__':
    main()
