# Class: CST 205 - Multimedia Design & Programming
# Title: preprocess.py
# Abstract: Code contains functions for image manipulations.
# Authors: Yash Patel
# Date Created: 05/19/2022


import numpy as np
from PIL import Image


def shrink_image(your_image):
    source3 = Image.open(your_image)
    w, h = source3.width, source3.height

    w_image = input("Enter a value to reduce your image's width (Between 0 - 5): ")
    h_image = input("Enter a new height (Between 0 - 5): ")

    target_x = 0
    for source_x in range(0, source3.width, w_image):
        target_y = 0
        for source_y in range(0, source3.height, h_image):
            pixel = source3.getpixel((source_x, source_y))
            canvas = Image.new('RGB', (round(w / w_image), round(h / h_image)))
            canvas.putpixel((target_x, target_y), pixel)
            target_y += 1
        target_x += 1
    canvas.show()


def resize_up_down(your_image):
    image = Image.open(your_image)
    w = input("Enter a new width for the image: ")
    h = input("Enter a new height: ")
    resized_image = image.resize(w, h)
    resized_image.show()


def scaling_up(your_image):
    source = Image.open(your_image)
    mf = input("Enter a value to enlarge your image (Between 2 - 4): ")
    w, h = source.width * mf, source.height * mf
    target = Image.new('RGB', (w, h))

    target_x = 0
    for source_x in np.repeat(range(source.width), mf):
        target_y = 0
        for source_y in np.repeat(range(source.height), mf):
            pixel = source.getpixel((int(source_x), int(source_y)))
            target.putpixel((target_x, target_y), pixel)
            target_y += 1
        target_x += 1
    target.show()


def grayscale(your_image, output_path):
    im2 = Image.open(your_image)
    new_list = [((a[0] * 299 + a[1] * 587 + a[2] * 114) // 1000,) * 3 for a in im2.getdata()]
    im2.putdata(new_list)

    im2.save(output_path)


def negative(your_image, output_path):
    img = Image.open(your_image)
    image_a = np.array(img)
    max_value = 255
    image_a = max_value - image_a
    inverted_image = Image.fromarray(image_a)
    inverted_image.save(output_path)


def sepia(your_image, output_path):
    im2 = Image.open(your_image)
    width, height = im2.size
    sepiaImg = im2.copy()

    for x in range(width):
        for y in range(height):
            red, green, blue = im2.getpixel((x, y))
            new_val = (0.3 * red + 0.59 * green + 0.11 * blue)

            new_red = int(new_val * 2)
            if new_red > 255:
                new_red = 255
            new_green = int(new_val * 1.5)
            if new_green > 255:
                new_green = 255
            new_blue = int(new_val)
            if new_blue > 255:
                new_blue = 255

            sepiaImg.putpixel((x, y), (new_red, new_green, new_blue))

    sepiaImg.save(output_path)


def thumbnail(your_image, output_path):
    im2 = Image.open(your_image)
    w, h = im2.width // 2, im2.height // 2
    target = Image.new('RGB', (w, h), 'aliceblue')

    target_x = 0
    for source_x in range(0, im2.width, 2):
        target_y = 0
        for source_y in range(0, im2.height, 2):
            if source_x >= im2.width or source_y >= im2.height or target_x >= w or target_y >= h:
                continue
            pixel = im2.getpixel((source_x, source_y))
            target.putpixel((target_x, target_y), pixel)
            target_y += 1
        target_x += 1

    target.save(output_path)
