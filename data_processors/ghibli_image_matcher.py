# import os
# import numpy as np
# import pandas as pd
# import torch
#
# from PIL import Image
# from transformers import CLIPProcessor, CLIPModel
#
# # =========================================================
# # LOAD MODEL
# # =========================================================
# model = CLIPModel.from_pretrained(
#     "openai/clip-vit-base-patch32"
# )
#
# processor = CLIPProcessor.from_pretrained(
#     "openai/clip-vit-base-patch32"
# )
#
# # =========================================================
# # SETTINGS
# # =========================================================
# IMAGE_DIR = "data/movie_images"
# EMBEDDINGS_PATH = "data/movie_image_embeddings.pkl"
#
# # =========================================================
# # IMAGE EMBEDDING
# # =========================================================
# def get_image_embedding(image_path):
#
#     image = Image.open(image_path).convert("RGB")
#
#     inputs = processor(
#         images=image,
#         return_tensors="pt"
#     )
#
#     with torch.no_grad():
#         embedding = model.get_image_features(**inputs)
#
#     # normalize
#     embedding = embedding / embedding.norm(
#         dim=-1,
#         keepdim=True
#     )
#
#     return embedding.squeeze().numpy()
#
# # =========================================================
# # BUILD EMBEDDING DATABASE
# # =========================================================
# def build_embedding_database():
#
#     rows = []
#
#     for movie in os.listdir(IMAGE_DIR):
#
#         movie_dir = os.path.join(IMAGE_DIR, movie)
#
#         if not os.path.isdir(movie_dir):
#             continue
#
#         for file in os.listdir(movie_dir):
#
#             path = os.path.join(movie_dir, file)
#
#             try:
#                 emb = get_image_embedding(path)
#
#                 rows.append({
#                     "movie": movie,
#                     "image_path": path,
#                     "embedding": emb
#                 })
#
#                 print("Processed:", path)
#
#             except Exception as e:
#                 print("Failed:", path, e)
#
#     df = pd.DataFrame(rows)
#
#     df.to_pickle(EMBEDDINGS_PATH)
#
#     print("\nSaved embeddings:")
#     print(EMBEDDINGS_PATH)
#
# # =========================================================
# # LOAD EMBEDDINGS
# # =========================================================
# def load_embeddings():
#
#     if not os.path.exists(EMBEDDINGS_PATH):
#
#         print("Embedding file not found.")
#         print("Building embeddings...\n")
#
#         build_embedding_database()
#
#     return pd.read_pickle(EMBEDDINGS_PATH)
#
# # =========================================================
# # COSINE SIMILARITY
# # =========================================================
# def cosine_similarity(a, b):
#     return np.dot(a, b)
#
# # =========================================================
# # RECOMMEND MOVIES
# # =========================================================
# def recommend_movies(user_image_path, top_k=5):
#
#     df = load_embeddings()
#
#     user_emb = get_image_embedding(user_image_path)
#
#     scores = []
#
#     for _, row in df.iterrows():
#
#         score = cosine_similarity(
#             user_emb,
#             row["embedding"]
#         )
#
#         scores.append({
#             "movie": row["movie"],
#             "score": score
#         })
#
#     result = (
#         pd.DataFrame(scores)
#         .groupby("movie")["score"]
#         .max()
#         .sort_values(ascending=False)
#         .head(top_k)
#     )
#
#     return result
#
# # =========================================================
# # EXAMPLE USAGE
# # =========================================================
# if __name__ == "__main__":
#
#     # only needed first time
#     # build_embedding_database()
#
#     results = recommend_movies(
#         "user_upload.jpg",
#         top_k=5
#     )
#
#     print("\nTop Matches:")
#     print(results)

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