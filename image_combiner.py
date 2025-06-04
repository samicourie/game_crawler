import os
import random
import numpy as np
from PIL import Image, ImageEnhance, ImageOps

image_list = os.listdir('static/Background')
poster_size = 256
random.shuffle(image_list)
# random.shuffle(image_list)
image_list = image_list[:240]
poster_count = 1
for offset in range(0, len(image_list), poster_size):
    images_objs = [Image.open('static/Background/' + img).convert('RGB') for img in image_list[offset: offset+poster_size]]
    converters = [ImageEnhance.Color(v) for v in images_objs]
    image_obj = [v.enhance(1.5) for v in converters]
    # images_objs = [ImageOps.expand(img.resize((864, 1269)), border=10, fill='yellow') for img in images_objs]
    images_objs = [ImageOps.expand(img.resize((450, 600)), border=10, fill='yellow') for img in images_objs]
    horizontal_count = 24
    image_hor_list = []
    for offset in range(0, len(images_objs), horizontal_count):
        image_hor_list.append(np.hstack([img for img in images_objs[offset: offset+horizontal_count]]))

    poster = np.vstack([img for img in image_hor_list])
    poster = Image.fromarray(poster)
    poster.save('Posters/poster_' + str(poster_count) + '.jpg')
    poster_count += 1
