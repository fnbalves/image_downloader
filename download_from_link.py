import argparse, sys
import urllib.request
import ssl
import re
import os
from requests import Request, Session
from bs4 import BeautifulSoup as Soup
from os.path import exists

def get_next_possible_path(initial_path):
    if not exists(initial_path):
        return initial_path
    index = 1
    base_name = '.'.join(initial_path.split('.')[:-1])
    extension = initial_path.split('.')[-1]
    next_name = base_name + '(%d)' % index + '.' + extension
    while exists(next_name):
        index += 1
        next_name = base_name + '(%d)' % index + '.' + extension
    return next_name

def get_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def get_headers(extra_headers):
    headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36' }
    
    if extra_headers is not None:
        for header in extra_headers:
            headers[header] = extra_headers[header]
    return headers

def load_site(url, extra_headers = None):
    headers = get_headers(extra_headers)
    ctx = get_ssl_context()

    req = urllib.request.Request(url, None, headers)

    url_opener = urllib.request.urlopen(req, context=ctx)
    
    raw_response = url_opener.read()
    
    return raw_response

def save_image(url, dest_filename, extra_headers = None):
    headers = get_headers(extra_headers)
    ctx = get_ssl_context()

    file_extension = url.split('.')[-1]
    req = urllib.request.Request(url, headers=headers)
    raw_path_to_save = dest_filename + '.' + file_extension
    path_to_save = get_next_possible_path(raw_path_to_save)
    with open(path_to_save, "wb") as f:
        with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
            f.write(r.read())

def create_folder(folder):
    if not os.path.isdir(folder):
        os.makedirs(folder, exist_ok=True)

def download_images_from_page(args):
    folder = args.dest_folder
    url = args.url
    headers = None
    
    src_tag = 'src'
    if args.src_tag is not None:
        src_tag = args.src_tag

    if args.referer is not None:
        headers = {}
        headers['Referer'] = args.referer
    
    create_folder(folder)
    info = load_site(url, headers)
    soup = Soup(info, 'html.parser')
    imgs = soup.findAll(args.image_tag)
    target_imgs = [i for i in imgs if i.has_attr(args.required_attr)]

    if args.attr_regex is not None:
        target_imgs[:] = [t for t in target_imgs if re.match(args.attr_regex, t[args.required_attr])]
    
    num_images = len(target_imgs)
    print('Found %d images' % num_images)
    for index, i in enumerate(target_imgs[3:]):
        try:
            image_raw_name = i[src_tag].split('?')[0]
            if '://' not in image_raw_name:
                url_base = args.url.split('://')[0] + '://' + args.url.replace('http://', '').replace('https://', '').split('/')[0]
                image_raw_name = url_base + image_raw_name
            image_name = image_raw_name.split('/')[-1].split('.')[0]
            path = os.path.join(folder, image_name)
            save_image(image_raw_name, path, headers)
            print('Saved %d of %d' % (index + 1, num_images))
        except:
            pass

def check_required_args(args):
    any_is_missing = False
    if args.url is None:
        print('--url is required')
        any_is_missing = True
    if args.image_tag is None:
        print('--image_tag is required')
        any_is_missing = True
    if args.required_attr is None:
        print('--required_attr is required')
        any_is_missing = True
    if args.dest_folder is None:
        print('--dest_folder is required')
        any_is_missing = True
    
    if any_is_missing:
        exit(-1)

parser=argparse.ArgumentParser()

parser.add_argument('--url', help='Source url')
parser.add_argument('--image_tag', help='Image tag to search')
parser.add_argument('--src_tag', help='The tag that contains the image address. Defaults to src')
parser.add_argument('--required_attr', help='Required attribute for the image tags')
parser.add_argument('--attr_regex', help='Optional regex to max for the attribute defined in --required-attr')
parser.add_argument('--referer', help='Referer for the request')
parser.add_argument('--dest_folder', help='Destination folder')

args = parser.parse_args()

check_required_args(args)
download_images_from_page(args)