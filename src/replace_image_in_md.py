# -*- coding: utf-8 -*-
import hashlib
import os
import re
import sqlite3
from sys import argv

import tinify
import leancloud
from leancloud import File

# TinyPng API key (link: https://tinypng.com/developers)
TINY_API_KEY = "your_tiny_png_api_key"

# LeanCloud API id & key (link: https://leancloud.cn/docs/python_guide.html)
LEAN_CLOUD_API_ID = "your_lean_cloud_app_id"
LEAN_CLOUD_API_KEY = "your_lean_cloud_api_key"

# Match image in Markdown pattern
INSERT_IMAGE_PATTERN = re.compile('(!\[.*?\]\((?!http)(.*?)\))', re.DOTALL)


# Init TinyPng and LeanCloud API
def init_api():
    tinify.key = TINY_API_KEY
    leancloud.init(LEAN_CLOUD_API_ID, LEAN_CLOUD_API_KEY)


def get_file_size(file_path):
    return float(os.path.getsize(file_path))


# Find image list in Markdown file
def get_image_list_from_md(md_path):
    md_file = open(md_path)
    content = md_file.read()
    image_list = re.findall(INSERT_IMAGE_PATTERN, content)
    return image_list


# Compress image by TinyPng (https://tinypng.com)
def compress(source, target):
    print("[%s]" % os.path.split(source)[1]),
    data = tinify.from_file(source)
    data.to_file(target)
    scale = get_file_size(target) / get_file_size(source)
    print ('⬇ %.2f%%' % ((1 - scale) * 100)),


# Upload image to LeanCloud
def upload(file_path):
    if os.path.exists(file_path):
        img_name = os.path.split(file_path)[1]
        img_file = open(file_path)
        up_file = File(img_name, img_file)
        img_url = up_file.save().url
        print(" url: %s" % img_url)
        return img_url


# Calculate image file hash value
def calc_hash(file_path):
    with open(file_path, 'rb') as f:
        sha1obj = hashlib.sha1()
        sha1obj.update(f.read())
        file_hash = sha1obj.hexdigest()
        return file_hash


def connect_db(path):
    conn = sqlite3.connect(os.path.join(path, "ImageInfo.db"))
    conn.execute('''
       CREATE TABLE IF NOT EXISTS ImageInfo(
       hash    TEXT    NOT NULL PRIMARY KEY,
       url     TEXT    NOT NULL
       );
    ''')
    return conn


def write_db(conn, img_hash, img_url):
    conn.execute("INSERT INTO ImageInfo (hash, url) VALUES ('%s','%s')" % (img_hash, img_url))
    conn.commit()


def find_in_db(conn, img_hash):
    cursor = conn.execute('SELECT * FROM ImageInfo WHERE hash=?', (img_hash,))
    return cursor.fetchone()


def replace_img(source_md, target_md, conn):
    image_list = get_image_list_from_md(source_md)
    md_content = open(source_md).read()
    fb = open(target_md, 'w')

    print 'start >>>>>\n'

    for image in image_list:
        source_img = os.path.join(os.path.split(source_md)[0], image[1])
        db_data = find_in_db(conn, calc_hash(source_img))
        if db_data:
            print("[%s] >>> url: %s" % (os.path.split(source_img)[1], db_data[1]))
            url = db_data[1]
            md_content = md_content.replace(image[0], image[0].replace(image[1], str(url)))

        elif os.path.exists(source_img) and os.path.isfile(source_img):
            compressed_img = os.path.join(os.path.split(source_img)[0], 'cp_' + os.path.split(source_img)[1])
            compress(source_img, compressed_img)
            url = upload(compressed_img)
            md_content = md_content.replace(image[0], image[0].replace(image[1], str(url)))
            write_db(conn, calc_hash(source_img), url)

        else:
            print source_img + "is not exit or not a file"

    print '\n<<<<< end'

    fb.write(md_content)
    fb.close()


def main(script_file, source, target):
    if os.path.exists(source):
        init_api()
        db_connect = connect_db(os.path.split(script_file)[0])
        replace_img(source, target, db_connect)
        db_connect.close()
    else:
        print 'source file not exist'


if __name__ == '__main__':
    if len(argv) > 2:
        script, source_file, target_file = argv
        main(script, source_file, target_file)
    else:
        print 'please enter source file and target file'
