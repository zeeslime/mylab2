import tensorflow as tf
import random
import os
import numpy as np

from tensorflow import keras
from time import sleep

import pathlib

saved_model = tf.keras.models.load_model(
    "saved_model/my_model"
)  # load the saved model from the saved_model directory

img_height = 180
img_width = 180

dataset_url = "https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz"
data_dir = tf.keras.utils.get_file("flower_photos", origin=dataset_url, untar=True)
data_dir = pathlib.Path(data_dir)

# image_count = len(list(data_dir.glob("*/*.jpg")))
# print(image_count)

train_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=(img_height, img_width),
    batch_size=32,
)

class_names = train_ds.class_names


def predict(model):
    filename_list = []
    num_of_prediction = 100

    base_add = os.getcwd()
    base_dir = os.path.join(base_add, "flower_predict_data")
    for filename in os.listdir(base_dir):
        filename_list.append(filename)

    for _ in range(num_of_prediction):
        filename = random.choice(filename_list)
        flower_path = os.path.join(base_dir, filename)
        # sunflower_url = "https://storage.googleapis.com/download.tensorflow.org/example_images/592px-Red_sunflower.jpg"

        # flower_path = tf.keras.utils.get_file("Red_sunflower", origin=flower_url)

        img = tf.keras.utils.load_img(flower_path, target_size=(180, 180))
        img_array = tf.keras.utils.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)  # Create a batch

        predictions = model.predict(img_array)
        score = tf.nn.softmax(predictions[0])

        print(
            "This image {} most likely belongs to {} with a {:.2f} percent confidence.".format(
                filename, class_names[np.argmax(score)], 100 * np.max(score)
            )
        )
        sleep(2)


# predict(saved_model)
