import streamlit as st
import pandas as pd
import pickle
import pymongo

# Step 1: Load pickle files (Product Data & Similarity Matrix)
with open("product_list.pkl", "rb") as f:
    df = pickle.load(f)  # DataFrame containing product names, prices, etc.

with open("similarity.pkl", "rb") as f:
    similarity = pickle.load(f)  # NumPy similarity matrix

# Step 2: MongoDB Connection
MONGO_URI = "mongodb+srv://prachikoli:grocerease5@cluster0.ebrmr.mongodb.net/prachikoli"  # Replace with your MongoDB Atlas URI
client = pymongo.MongoClient(MONGO_URI)
db = client["prachikoli"]  # Replace with your database name
collection = db["products"]  # Replace with your collection name

# Step 3: Define Local or Deployed URL for MERN Site
LOCAL_HOST = "http://localhost:3000"  # Change port if needed
deployed_url = "https://your-mern-site.com"  # Replace after deployment

# Step 4: Streamlit UI Setup
st.title("🛒 Grocery Product Recommendation")

# Step 5: User Input - Search bar
product_name = st.text_input("Enter a product name:", "")

# Step 6: Checkbox to Show Recommendations
show_recommendations = st.checkbox("Show Recommendations")

# Step 7: Fetch Product Image URL, Price, and ID from MongoDB
def get_product_info(product_name):
    """Fetch product image URL, price, and product ID for redirection."""
    product = collection.find_one({"name": product_name})
    if product:
        images = product.get("images", [])
        img_url = images[0].get("url") if images and isinstance(images[0], dict) else None
        product_id = str(product.get("_id"))  # Convert ObjectId to string
        product_url = f"{LOCAL_HOST}/product/{product_id}"  # Local testing URL
        price = product.get("discountPrice", "N/A")  # Fetch price, default to 'N/A' if missing
        return img_url, product_url, price
    return None, "#", "N/A"

# Step 8: Recommendation Function
def recommend_products(product_name, top_n=5):
    if product_name not in df["name"].values:
        return pd.DataFrame()  # Return empty DataFrame if product not found

    product_index = df[df["name"] == product_name].index[0]
    similarity_scores = list(enumerate(similarity[product_index]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]  # Exclude self
    recommended_products = df.iloc[[i[0] for i in similarity_scores]]
    return recommended_products

# Step 9: Display Recommendations
if show_recommendations:
    if product_name:
        recommendations = recommend_products(product_name)

        if recommendations.empty:
            st.error(f"❌ Product '{product_name}' not found. Please try another name.")
        else:
            st.subheader("🔹 Recommended Products:")
            cols = st.columns(5)  # 5-column layout

            for i, row in recommendations.iterrows():
                with cols[i % 5]:
                    img_url, product_url, price = get_product_info(row["name"])
                    
                    # Step 10: Display Clickable Product Name with Redirection
                    st.markdown(f"[**{row['name']}**]({product_url})", unsafe_allow_html=True)
                    
                    # Step 11: Display Product Image
                    if img_url:
                        st.image(img_url, use_container_width=True)
                    else:
                        st.write("🚫 No Image Available")
                    
                    # Step 12: Display Price
                    st.write(f" Price: ₹{price}")

                    # Step 13: Redirect Button (Opens in a new tab)
                    st.markdown(f'<a href="{product_url}" target="_blank"><button>View {row["name"]}</button></a>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ Please enter a product name to get recommendations.")
