import streamlit as st
from landing_modules import home as Home, pricing, products, login
from modules.dashboard import *
from PIL import Image
import modules.js_utils as js_utils
from time import sleep
from supabase import create_client

# Initialize Supabase client using secrets.
url = st.secrets.url
key = st.secrets.anon_key
supabase = create_client(url, key)

# Open the image file
image = Image.open(r".\images\solsync_logo.png")  # Replace with the path to your image
# Convert the image to a NumPy array
image_array = np.array(image)

def main():
    st.set_page_config(page_title="SolSync", page_icon="🔆", layout="wide")
    if 'title' not in st.session_state:
        st.session_state['title'] = "Home"
    
    inv1, inv2, inv3, inv4, inv5 = st.columns([0.35,0.1,0.1,0.1,0.35], vertical_alignment='center')

    with inv1:
        st.image(image_array, width=200)
    # Load stored sign-in status and convert to boolean robustly.
    with inv2:
        session_value_raw = js_utils.load_from_session_storage("is_signed")
    session_value = session_value_raw.lower() == "true" if session_value_raw and isinstance(session_value_raw, str) else False

    # Load access token (for "remember me") and user email (if available) from storage.
    with inv3:
        local_value = js_utils.load_from_local_storage("access_token")
    with inv4:
        user_email = js_utils.load_from_session_storage("user_email")  # Ensure you save this during login

    sleep(2)
    
    # If the user is signed in either via the session flag or via a persistent token.
    if session_value or (local_value and local_value.strip() != ""):
        if 'user_id' not in st.session_state:
            # Use the access token if available; otherwise, lookup by email.
            if local_value and local_value.strip() != "":
                data = supabase.table("user_authentication").select("id", "username").eq("access_token", local_value).execute()
            elif user_email and user_email.strip() != "":
                data = supabase.table("user_authentication").select("id", "username").eq("email", user_email).execute()
            else:
                st.error("User identifier missing.")
                return

            if data.data and len(data.data) > 0:
                st.session_state['user_id'] = data.data[0]['id']
                st.session_state['username'] = data.data[0]['username']

            else:
                st.error("Could not retrieve user ID from the database.")
                return
            
        dashboard(user_id=st.session_state['user_id'], username=st.session_state['username'], supabase=supabase)
    
    else:
        # Create a dictionary of pages.
        pages = {
            "Home": Home.home,
            "Products": products.products,
            "Pricing": pricing.pricing,
            "Login": login.login
        }
        page_selection = [pages["Home"],
                          pages["Products"],
                          pages["Pricing"],
                          pages["Login"]]

        if 'page' not in st.session_state:
            st.session_state['page'] = 0

        # --------------------------------------------------------------------------------
        # HEADER SECTION
        # --------------------------------------------------------------------------------
        with inv5:
            col1, col2, col3, col4 = st.columns(4, vertical_alignment="center")

            with col1:
                if st.button("Home", use_container_width=True):
                    st.session_state['title'] = "Home"
                    st.session_state['page'] = 0
                    st.rerun()
            with col2:
                if st.button("Products", use_container_width=True):
                    st.session_state['title'] = "Products"
                    st.session_state['page'] = 1
                    st.rerun()
            with col3:
                if st.button("Pricing", use_container_width=True):
                    st.session_state['title'] = "Pricing"
                    st.session_state['page'] = 2
                    st.rerun()
            with col4:
                if st.button("Account", use_container_width=True):
                    st.session_state['title'] = "Account"
                    st.session_state['page'] = 3
                    st.rerun()

        # Render the selected page.
        if st.session_state['page'] == 3:
            page_selection[st.session_state['page']](supabase)
        else:
            page_selection[st.session_state['page']]()

if __name__ == "__main__":
    main()
