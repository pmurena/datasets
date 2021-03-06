#!/usr/bin/env python

from nltk.corpus import wordnet as wn
from re import findall as fa
import os
import getopt
import sys
from threading import Thread
import requests

off_url_src = "imagenet.txt"
img_base_dir = os.getcwd()
nb_threads = 4
file_lines = []

try:
    opts, args = getopt.getopt(sys.argv[1:], "d:f:")
except getopt.GetoptError:
    print('bad argument error, usage:')
    print('\targs1.py -d <base_directory> -f <input_file_name>')
    print('\ndefault:\n\t-d <current working directory>\n\t-f <imagenet.txt>')
    sys.exit(2)


for opt, arg in opts:
    if opt == "-d":
        if not arg[-1:] == "/":
            arg = arg + "/"
        img_base_dir = arg
    elif opt == "-f":
        off_url_src = arg

print("reading data")
with open(off_url_src, "r", errors="ignore") as f:
    for data in f.readlines():
        file_lines.append(data.split())
f.close()
print("data loaded")

print("building wordnet dictionary")
syns = list(wn.all_synsets())
offsets_list = [(s.offset(), s) for s in syns]
offsets_dict = dict(offsets_list)
print("wordnet built")

print("create directories")
for d in offsets_dict:
    tmp_dir = img_base_dir + offsets_dict[d].lemma_names()[0]
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
print("directories created")


def download(th):
    print("thread ", th, " started")
    n = 0
    while file_lines:
        print("thread ", th, " working on image ", n)
        entry = file_lines.pop()
        cat = offsets_dict[int(fa("n(\d+)_*", entry[0])[0])].lemma_names()[0]
        directory = img_base_dir + cat
        img_name = cat + "_" + str(th) + "_" + str(n) + entry[1][-4:]
        print("thread ", th, "downloading: ", entry[1])
        try:
            img_data = requests.get(entry[1]).content
        except requests.exceptions.RequestException as e:
            print(e)
            continue
        img_path = os.path.join(directory, img_name)
        with open(img_path, 'wb') as handler:
            handler.write(img_data)
            handler.close()
        print("thread ", th, " image ", n, "done")
        n = n + 1
    print("thread ", th, "all done")


for n in range(1, nb_threads + 1):
    thread = Thread(target=download, args=(n,))
    thread.start()
