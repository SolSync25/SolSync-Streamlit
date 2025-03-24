import streamlit as st
from PIL import Image
import os

def products():
    # --------------------------------------------------------------------------------
    # HEADER & INTRODUCTION
    # --------------------------------------------------------------------------------
    st.markdown("<h2 style='text-align: center; color: gray;'>Innovative Solar Solutions</h2>", unsafe_allow_html=True)
    st.write(
        """
        At SolSync, we offer cutting-edge products that empower you to take full control
        of your solar energy journey. Our diverse range includes intelligent inverters, advanced monitoring devices,
        and robust energy storage solutions, crafted to deliver superior performance and user-friendly control.
        """
    )

    # --------------------------------------------------------------------------------
    # HERO IMAGE FOR PRODUCTS (if available)
    # --------------------------------------------------------------------------------
    try:
        if os.path.exists(r"/mount/src/solsync-streamlit/images/products_banner.jpg"):
            image_path = r"/mount/src/solsync-streamlit/images/products_banner.jpg"
        else:
            current_directory = os.getcwd()
            image_path = os.path.join(current_directory, "images", "products_banner.jpg")
        st.image(Image.open(image_path))
    except Exception:
        st.info("Products banner image not found. Add 'products_banner.jpg' in your images directory.")

    # --------------------------------------------------------------------------------
    # PRODUCT HIGHLIGHTS SECTION
    # --------------------------------------------------------------------------------
    st.markdown("## Our Product Range")
    st.markdown(
        """
        - **Smart Inverters:**  
          Experience seamless control with real-time monitoring and innovative management features.
        - **Advanced Monitoring Devices:**  
          Track and analyze your solar performance with precision engineered sensors and software.
        - **Energy Storage Solutions:**  
          Secure your harvested energy with durable, high-capacity battery systems that keep you powered,
          even after sunset.
        """
    )