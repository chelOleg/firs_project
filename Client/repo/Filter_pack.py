from PIL import Image, ImageDraw
from PIL.ImageQt import ImageQt
import os
def sepia(image):
    draw = ImageDraw.Draw(image)
    width = image.size[0]
    height = image.size[1]
    pix = image.load()

    for i in range(width):
        for j in range(height):
            a = pix[i, j][0]
            b = pix[i, j][1]
            c = pix[i, j][2]
            S = (a + b + c)
            c = c
            b = c * 2
            a = c * 3
            if (a > 255):
                a = 255
            if (b > 255):
                b = 255
            if (c > 255):
                c = 255
            draw.point((i, j), (a, b, c))

    return image

def negative(image):
    draw = ImageDraw.Draw(image)
    width = image.size[0]
    height = image.size[1]
    pix = image.load()

    for i in range(width):
        for j in range(height):
            a = pix[i, j][0]
            b = pix[i, j][1]
            c = pix[i, j][2]
            draw.point((i, j), (255 - a, 255 - b, 255 - c))

    return image

def gray(image):
    draw = ImageDraw.Draw(image)
    width = image.size[0]
    height = image.size[1]
    pix = image.load()
    for i in range(width):
        for j in range(height):
            a = pix[i, j][0]
            b = pix[i, j][1]
            c = pix[i, j][2]
            # Среднее значение
            S = (a + b + c) // 3
            draw.point((i, j), (S, S, S))
    return image

def get_bits(image):
    try:
        img = open(image, "rb")
        b_image = img.read()
        img.close()
    except:
        b_image = None
    return b_image

def set_bits(data,name):
    file = open(name,'wb')
    file.write(data)
    file.close()

def mini_picture(name,save_as,h = 250,w = 250):
    image = Image.open(name)
    image = image.resize((h, w), Image.ANTIALIAS)
    image.save(save_as)
