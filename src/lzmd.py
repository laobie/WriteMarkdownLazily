# -*- coding: utf-8 -*-
import hashlib
from os import path
import re
import sqlite3
from sys import argv
import requests

import tinify
import leancloud
from leancloud import File

# TinyPng API key (link: https://tinypng.com/developers)
TINY_API_KEY = "tiny_api_key"

# LeanCloud API id & key (link: https://leancloud.cn/docs/python_guide.html)
LEAN_CLOUD_API_ID = "leancloud_api_id"
LEAN_CLOUD_API_KEY = "leancloud_api_key"

# Match image in Markdown pattern
INSERT_IMAGE_PATTERN = re.compile('(!\[.*?\]\((?!http)(.*?)\))', re.DOTALL)
INSERT_URL_PATTERN = re.compile(r'[^!]\[\]\((http.*?)\)')

URL_TITLE_PATTERN = re.compile(r'<title>(.*?)</title>')


# Init TinyPng and LeanCloud API
def init_api():
    tinify.key = TINY_API_KEY
    leancloud.init(LEAN_CLOUD_API_ID, LEAN_CLOUD_API_KEY)


def get_file_size(file_path):
    return float(path.getsize(file_path))


# Compress image by TinyPng (https://tinypng.com)
def compress(source, target):
    print "compressing image %s, save to %s" % (source, target)
    data = tinify.from_file(source)
    data.to_file(target)
    scale = get_file_size(target) / get_file_size(source)
    return (1 - scale) * 100


# Upload image to LeanCloud
def upload(file_path):
    print 'uploading file %s' % file_path
    img_name = path.split(file_path)[1]
    img_file = open(file_path)
    up_file = File(img_name, img_file)
    img_url = up_file.save().url
    return img_url


# Calculate image file hash value
def calc_hash(file_path):
    with open(file_path, 'rb') as f:
        sha1obj = hashlib.sha1()
        sha1obj.update(f.read())
        file_hash = sha1obj.hexdigest()
        return file_hash


def connect_db(path):
    print 'connect to database %s' % path
    conn = sqlite3.connect(path)
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


class Handler:
    def __init__(self):
        self.__content = ''

    def read_from(self, source):
        print 'reading %s ...' % source
        with open(source) as md:
            self.__content = md.read()
        return self

    def write_to(self, target):
        print 'writing into %s ...' % target
        with open(target, 'w') as md:
            md.write(self.__content)

    def replace_image(self):
        images = INSERT_IMAGE_PATTERN.findall(self.__content)
        if not images:
            print 'found no image reference in source file ~'
            return self

        images = map(lambda i: i[1], images)
        print 'found %d image reference in source file ~' % len(images)

        with connect_db("ImageInfo.db") as db:
            for image in images:
                if not path.exists(image):
                    print "can not find image %s :(" % image
                    continue

                img_hash = calc_hash(image)
                # find local first
                image_data = find_in_db(db, img_hash)
                if image_data:
                    image_url = image_data[1]
                    print '[%s] => %s found in database' % (image, image_url)
                else:
                    # compress & upload
                    img_sp = path.split(image)
                    compressed_img = path.join(img_sp[0], 'cp_' + img_sp[1])
                    size_percent = compress(image, compressed_img)
                    image_url = upload(compressed_img).encode('utf-8')
                    write_db(db, img_hash, image_url)
                    print '[%s] => %s , size ⬇ %.2f%%' % (image, image_url, size_percent)

                self.__content = self.__content.replace('(%s)' % image, '(%s)' % str(image_url))

        return self

    def replace_url(self):
        urls = INSERT_URL_PATTERN.findall(self.__content)
        if not urls:
            print 'found no url reference in source file ~'
            return self

        print 'found %d url reference in source file ~' % len(urls)
        for url in urls:
            try:
                # download html & extract title
                title = URL_TITLE_PATTERN.search(requests.get(url, timeout=5).text)
                title = title.group(1).encode('utf-8') if title else ''

                self.__content = self.__content.replace('[](%s)' % url, '[%s](%s)' % (title, url))
                print '[%s] => %s' % (url, title)
            except:
                print '[%s] replace failed :(' % url

        return self


def main(source, target):
    if not path.exists(source):
        print "source file doesn't exist :("
        return

    init_api()

    Handler() \
        .read_from(source) \
        .replace_image() \
        .replace_url() \
        .write_to(target)

    print 'all done ~'


if __name__ == '__main__':
    if len(argv) > 2:
        script, source_file, target_file = argv
        main(source_file, target_file)
    else:
        print 'please enter source file and target file'
