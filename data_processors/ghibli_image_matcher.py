import os
import pandas as pd

CSV_PATH = "../data/processed/ghibli_interest_labels.csv"
IMAGE_DIR = "../data/movie_images"

df = pd.read_csv(CSV_PATH)

image_paths = []

for _, row in df.iterrows():

    folder_name = row["title"].replace(" ", "_")

    folder = os.path.join(IMAGE_DIR, folder_name)

    image_file = None

    if os.path.exists(folder):

        for file in os.listdir(folder):

            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                image_file = os.path.join(folder, file)
                break

    image_paths.append(image_file)

df["image_path"] = image_paths

df.to_csv(CSV_PATH, index=False)

print("Updated CSV with image paths.")