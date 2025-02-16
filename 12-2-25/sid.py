import streamlit as st
import pandas as pd
import pickle
import numpy as np

# Load pickle files
with open("product_list.pkl", "rb") as f:
    df = pickle.load(f)  # DataFrame containing product names, prices, etc.

with open("similarity.pkl", "rb") as f:
    similarity = pickle.load(f)  # NumPy similarity matrix

# 🔹 Streamlit UI
st.title("🛒 Grocery Product Recommendation")

# 🔹 Search bar
product_name = st.text_input("Enter a product name:", "")

# 🔹 Checkbox for recommendations
show_recommendations = st.checkbox("Show Recommendations")

# 🔹 Define recommendation function
def recommend_products(product_name, top_n=5):
    if product_name not in df["name"].values:
        return pd.DataFrame()  # Return empty DataFrame if product not found

    # Get the index of the given product
    product_index = df[df["name"] == product_name].index[0]

    # Get similarity scores for the product and sort them
    similarity_scores = list(enumerate(similarity[product_index]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]  # Exclude self

    # Get recommended products
    recommended_products = df.iloc[[i[0] for i in similarity_scores]]

    return recommended_products

# 🔹 Display Recommendations
if show_recommendations:
    if product_name:
        recommendations = recommend_products(product_name)

        if recommendations.empty:
            st.error(f"❌ Product '{product_name}' not found. Please try another name.")
        else:
            st.subheader("🔹 Recommended Products:")

            # Create columns (grid layout)
            cols = st.columns(5)  # 5-column layout

            for i, row in recommendations.iterrows():
                with cols[i % 5]:  # Place items in columns
                    st.write(f"**{row['name']}**")  # Display product name
                    
    else:
        st.warning("⚠️ Please enter a product name to get recommendations.")
