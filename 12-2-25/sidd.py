import streamlit as st
import pandas as pd
import pickle
import pymongo

# 🔹 Load pickle files (Product Data & Similarity Matrix)
with open("product_list.pkl", "rb") as f:
    df = pickle.load(f)  # DataFrame containing product names, prices, etc.

with open("similarity.pkl", "rb") as f:
    similarity = pickle.load(f)  # NumPy similarity matrix

# 🔹 MongoDB Connection
MONGO_URI = ""  # Replace with your MongoDB Atlas URI
client = pymongo.MongoClient(MONGO_URI)
db = client["prachikoli"]  # Replace with your database name
collection = db["products"]  # Replace with your collection name

# 🔹 Streamlit UI
st.title("🛒 Grocery Product Recommendation")

# 🔹 Search bar
product_name = st.text_input("Enter a product name:", "")

# 🔹 Checkbox for recommendations
show_recommendations = st.checkbox("Show Recommendations")

# 🔹 Fetch Product Image URL from Cloudinary
def get_product_info(product_name):
    """Fetch product image URL from MongoDB (Cloudinary storage)."""
    product = collection.find_one({"name": product_name})
    if product:
        # Extract Cloudinary image URL from 'images' array
        images = product.get("images", [])  # Ensure 'images' is a list
        img_url = images[0].get("url") if images and isinstance(images[0], dict) else None  # Extract URL safely
        product_url = product.get("url", "#")  # Default to "#" if URL is missing
        return img_url, product_url
    return None, "#"


# 🔹 Recommendation Function
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

            cols = st.columns(5)  # 5-column layout

            for i, row in recommendations.iterrows():
                with cols[i % 5]:  # Place items in columns
                    # Fetch image URL & product URL
                    img_url, product_url = get_product_info(row["name"])
                    
                    # Display clickable product name
                    st.markdown(f"[**{row['name']}**]({product_url})", unsafe_allow_html=True)

                    # Display product image from Cloudinary
                    if img_url:
                        st.image(img_url, use_container_width=True)
                    else:
                        st.write("🚫 No Image Available")

                    # Redirect Button (Optional)
                    if st.button(f"View {row['name']}", key=f"btn_{i}"):
                        st.write(f"🔗 Redirecting to [Product Page]({product_url})...")
                        st.experimental_rerun()
    else:
        st.warning("⚠️ Please enter a product name to get recommendations.")
