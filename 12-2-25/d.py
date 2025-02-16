import pickle
import pandas as pd
import numpy as np

# Load pickle files
with open("product_list.pkl", "rb") as f:
    df = pickle.load(f)  # DataFrame containing product names

with open("similarity.pkl", "rb") as f:
    similarity = pickle.load(f)  # NumPy similarity matrix

# Function to get recommendations
def recommend_products(product_name, top_n=5):
    if product_name not in df["name"].values:
        return f"Product '{product_name}' not found."

    # Get the index of the given product
    product_index = df[df["name"] == product_name].index[0]

    # Get similarity scores for the product and sort them
    similarity_scores = list(enumerate(similarity[product_index]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]  # Exclude self

    # Get recommended product names
    recommended_products = [df.iloc[i[0]]["name"] for i in similarity_scores]

    return recommended_products

# Example Usage
product_name = "MDH Dal Makhni Masala"  # Change this to test
recommendations = recommend_products(product_name)
print("Recommended Products:", recommendations)
