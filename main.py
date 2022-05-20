# Class: CST 205 - Multimedia Design & Programming
# Title: main.py
# Abstract: The purpose of this web based app is to
add filter effects on images.
# Authors: Yash Patel
# Date Created: 05/19/2022


import ast as at
import os
from flask import Flask, render_template, request, json, redirect, url_for, abort
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from flickrapi import FlickrAPI
from requests import get as requests_get
from wtforms import SelectField, StringField
from wtforms.validators import DataRequired
from preprocess import *


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Y-A-S-H-P-A-T-E-L'
bootstrap = Bootstrap(app)

"""
Created by: Yash Patel
The purpose of this web based app is to
add filter effects on images.
I am using the these effects listed below
"""
effects = ['None', 'Grayscale', 'Negative', 'Sepia', 'Thumbnail']


def image_details():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    info = os.path.join(dir_path, "info.json")
    with open(info) as f:
        return json.loads(f.read())


def save_image_details(info_dict):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    info = os.path.join(dir_path, "info.json")
    with open(info, 'w') as info_file:
        info_file.write(json.dumps(info_dict))


def filename_id(filename):
    return os.path.basename(filename).rsplit('.')[0]


def get_image_details(image):
    image_info = {}
    local_detail = image_details()

    if image in local_detail:
        image_info = local_detail[image]
        image_info['url'] = f'/static/images/{image}.jpg'
    else:
        raw_response = flickr.photos.getInfo(photo_id=image)
        flickr_info = json.loads(raw_response.decode('utf-8'))
        if flickr_info['stat'] == 'ok':
            photo = flickr_info['photo']
            # Get url of original photo
            photo_sizes = json.loads(flickr.photos.getSizes(photo_id=image).decode('utf-8'))
            original_url = photo_sizes['sizes']['size'][-1]['source']
            image_info = {
                'title': photo['title']['_content'],
                'tags': [tag['_content'] for tag in photo['tags']['tag']],
                'flickr_page_url': photo['urls']['url'][0]['_content'],
                'url': original_url
            }
    return image_info


class Search(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])


class ImageEffect(FlaskForm):
    effect = SelectField('Effect', choices=effects)


class ImageUpload(FlaskForm):
    image_file = FileField('Image', validators=[FileRequired()])
    image_title = StringField('Title', validators=[DataRequired()])
    image_tags = StringField('Tags')
    image_effect = SelectField('Effect', choices=effects)


flickr_filename = os.path.join(app.static_folder, 'data', 'flickr.json')
with open(flickr_filename) as flickr_file:
    flickr_keys = json.load(flickr_file)
    flickr = FlickrAPI(flickr_keys['public_key'], flickr_keys['secret_key'], format='json')


def search(query):
    keywords = query.lower().split()
    results = []
    image_info_file = image_details()
    for image_id in image_info_file:
        image_info = image_info_file[image_id]
        hits = 0
        for keyword in keywords:
            if keyword in image_info['title'].lower().split() or keyword in [tag.lower() for tag in image_info['tags']]:
                hits += 1
        if hits != 0:
            image_info['id'] = image_id
            image_info['hits'] = hits
            results.append(image_info)
    results.sort(key=lambda img: img['hits'], reverse=True)
    return results


def flickr_search(query):
    extras = 'url_sq,url_t,url_s,url_q,url_m,url_n,url_z,url_c,url_l,url_o'
    decode = (flickr.photos.search(text=query, per_page=5, safe_search=1, extras=extras)).decode('utf-8')
    photos = at.literal_eval(decode)
    return photos['photos']['photo']


def apply_image_effect(image_path, effect, output_path=None):

    if output_path is None:
        output_path = image_path
    if effect == 'Grayscale':
        grayscale(image_path, output_path)
    elif effect == 'Negative':
        negative(image_path, output_path)
    elif effect == 'Sepia':
        sepia(image_path, output_path)
    elif effect == 'Thumbnail':
        thumbnail(image_path, output_path)


def download_flickr_img(flickr_url, file_path):
    r = requests_get(flickr_url, stream=True)
    with open(file_path, 'wb') as f:
        for chunk in r:
            f.write(chunk)


@app.route('/')
def index():

    search_form = Search()
    local_results = []
    flickr_results = []
    query = request.args.get('query')

    if query is not None:
        local_results = search(query)
        flickr_results = flickr_search(query)

    return render_template(
        'index.html',
        form=search_form,
        search_query=query,
        local_results=local_results,
        flickr_results=flickr_results
    )


@app.route('/image/<image_id>', methods=('GET', 'POST'))
def image(image_id):

    form = ImageEffect()
    image_info = get_image_details(image_id)
    effect = form.effect.data

    if 'url' not in image_info:
        abort(404)

    if form.validate_on_submit() and effect != 'None':
        modified_file_name = os.path.join('static', 'images')
        modified_file_path = modified_file_name + '/' + f'{image_id}_{effect}.jpg'
        if not os.path.exists(modified_file_path):
            if 'flickr_page_url' in image_info:
                download_flickr_img(image_info['url'], modified_file_path)
                apply_image_effect(modified_file_path, effect)
            else:
                image_file_path = os.path.join('static', 'images')
                path = image_file_path + '/' + f'{image_id}.jpg'
                apply_image_effect(path, effect, modified_file_path)
        image_info['url'] = f'/static/images/effect_cache/{modified_file_name}'

    return render_template('image.html', form=form, image_info=image_info)


@app.route('/upload', methods=('GET', 'POST'))
def upload():

    upload_form = ImageUpload()

    if upload_form.validate_on_submit():
        image_file = upload_form.image_file.data
        image_file_path = os.path.join('static', 'images')
        path = image_file_path + '/' + image_file.filename
        print(path)
        image_file.save(path)
        apply_image_effect(path, path)
        image_id = filename_id(image_file.filename)
        image_info = image_details()
        image_info[image_id] = {
            'title': upload_form.image_title.data,
            'tags': upload_form.image_tags.data.split(',')
        }
        save_image_details(image_info)
        return redirect(url_for('image', image_id=image_id))

    return render_template('upload.html', form=upload_form)