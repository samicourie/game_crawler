import pymongo

import os
import random
import requests
from io import BytesIO

import cv2
import numpy as np
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity

import torch
import torch.nn as nn
from torchvision import models, transforms


class ImageUtility:
    def __init__(self):
        self.embeddings = []  # list of numpy arrays
        self.filenames = []   # corresponding filenames
        self.similarity_matrix = None  # 2D numpy array
        # 1. Load pretrained ResNet model (remove final classification layer)
        self.resnet = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
        self.model = nn.Sequential(*list(self.resnet.children())[:-1])  # drop final FC layer
        self.model.eval()

        # 2. Transform pipeline for images
        self. transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406], 
                std=[0.229, 0.224, 0.225]
            )
        ])

    def reset(self):
        self.embeddings = []
        self.filenames = []
        self.similarity_matrix = None

    # 3. Function to extract embeddings
    def get_embedding(self, img):
        tensor = self.transform(img).unsqueeze(0)  # add batch dimension
        with torch.no_grad():
            features = self.model(tensor)
        return features.flatten().numpy()

    def convert_url_img_to_pil(self, response):
        img = Image.open(BytesIO(response.content)).convert('RGB')
        return img
    
    def read_img_from_path(self, path):
        img = Image.open(path).convert('RGB')
        return img

    def add_or_not(self, embedding, name, threshold=0.87):
        
        if len(self.embeddings) == 0:
            # first image
            self.embeddings.append(embedding)
            self.filenames.append(name)
            self.similarity_matrix = np.array([[1.0]])
            return True
        
        # convert list -> array
        existing = np.array(self.embeddings)
        
        # compute similarity with all previous embeddings
        sim_scores = cosine_similarity([embedding], existing)[0]
        
        # check if similar to anything
        for fname, score in zip(self.filenames, sim_scores):
            if score > threshold:
                return False  # too similar, do not add
        
        # update storage
        self.embeddings.append(embedding)
        self.filenames.append(name)
        
        # update similarity matrix
        new_row = sim_scores.tolist() + [1.0]
        if self.similarity_matrix is not None:
            self.similarity_matrix = np.vstack([
                np.hstack([self.similarity_matrix, np.array(sim_scores).reshape(-1,1)]),
                new_row
            ])
        else:
            self.similarity_matrix = np.array([[1.0]])

        return True

    def clean_images_path(self, path):
        game_path = ''
        for img_file in os.listdir(path):
            if img_file.split(' ')[0] != game_path:
                game_path = img_file.split(' ')[0]
                self.reset()
            try:
                img = self.read_img_from_path(path + img_file)
                embedding = self.get_embedding(img)
                if not self.add_or_not(embedding, path):
                    print('Removing:', img_file)
                    os.remove(path + img_file)
            except Exception as e:
                print(e)

    def download_images(self, game_obj, download_images=True, download_cover=True, nb_images=20):
        game_title = game_obj['title']
        ch = game_title[0].upper()
        if ch not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            ch = '#'
        if download_cover:
            if 'igdb-cover' in game_obj:
                cover_path = 'static/Covers New/' + game_obj['path'] + ' Cover.jpg'
                response = requests.get(game_obj['igdb-cover'])
                with open(cover_path, 'wb') as img_file:
                    img_file.write(response.content)

        if download_images:
            image_list = []
            for image_key in ['giantbomb-screenshots', 'igdb-screenshots', 'steam-images']:
                if image_key in game_obj:
                    image_list.extend(game_obj[image_key])
            
            if 'gamesdb-images' in game_obj:
                for lst in game_obj['gamesdb-images'].values():
                    if lst[0] == 'Screenshot - Gameplay':
                        image_list.extend(lst[1:])

            image_size = 50000
            if len(image_list) > 0:
                random.shuffle(image_list)
                count = 1
                for img in image_list:
                    try:
                        image_path = 'static/Temp/' + ch + '/' + game_obj['path'] + ' ' + str(count) + '.jpg'
                        response = requests.get(img)
                        if len(response.content) < image_size:
                            continue
                        pil_img = self.convert_url_img_to_pil(response)
                        img_embedding = self.get_embedding(pil_img)

                        if self.add_or_not(img_embedding, image_path):
                            with open(image_path, 'wb') as img_file:
                                img_file.write(response.content)
                                count += 1
                                if count > nb_images:
                                    break
                    except Exception as e:
                        print(e)


'''
def orb_feature_similarity(img1, img2):
    # Feature-based similarity using ORB keypoints and descriptors
    orb = cv2.ORB_create(nfeatures=1000)
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)
    if des1 is None or des2 is None:
        return 0
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    return len(matches) / max(len(kp1), len(kp2))  # normalized 0-1


def compare_images(img1, img2):
    results = {
        'ORB feature similarity': orb_feature_similarity(img1, img2),
    }
    return results


def check_if_new(image_lst, new_image, threshold=0.4):
    for img in image_lst:
        res = compare_images(img, new_image)
        if res['ORB feature similarity'] > threshold:
            return False
        if round(res['ORB feature similarity'], 2) > 0.2 and round(res['Histogram similarity'], 2) > 0.5:
            return False
    return True

def download_10_images(game_obj, download_cover=True):
    game_title = game_obj['title']
    ch = game_title[0].upper()
    if ch not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        ch = '#'
    if download_cover:
        if 'igdb-cover' in game_obj:
            cover_path = 'static/Covers New/' + game_obj['path'] + ' Cover.jpg'
            response = requests.get(game_obj['igdb-cover'])
            with open(cover_path, 'wb') as img_file:
                img_file.write(response.content)

    image_list = []
    for image_key in ['giantbomb-screenshots', 'igdb-screenshots', 'steam-images']:
        if image_key in game_obj:
            image_list.extend(game_obj[image_key])
    
    if 'gamesdb-images' in game_obj:
        for lst in game_obj['gamesdb-images'].values():
            if lst[0] == 'Screenshot - Gameplay':
                image_list.extend(lst[1:])

    image_size = 50000
    unique_list = []
    if len(image_list) > 0:
        random.shuffle(image_list)
        count = 1
        for img in image_list:
            try:
                images_path = 'static/New Temp/' + ch + '/' + game_obj['path'] + ' ' + str(count) + '.jpg'
                response = requests.get(img)
                if len(response.content) < image_size:
                    continue
                # Convert bytes to numpy array
                img_array = np.frombuffer(response.content, np.uint8)

                # Decode into cv2 image (BGR format)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

                if check_if_new(unique_list, img):

                    with open(images_path, 'wb') as img_file:
                        img_file.write(response.content)
                        count += 1
                        if count > 10:
                            break
                    unique_list.append(img)
            except Exception as _:
                pass
'''


if __name__ == '__main__':
    image_utility = ImageUtility()
    for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        print('Processing:', ch)
        image_utility.clean_images_path('static/New Temp/' + ch + '/')
        print('-----------------------------------------------------------------')
