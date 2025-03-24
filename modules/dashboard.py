import streamlit as st
from PIL import Image
import numpy as np
import modules.js_utils as js_utils
from modules.navigation import overview, commands, alarms, account
from modules.utils import get_from_database, get_from_alarms
import time

# Open the image file
image = Image.open(r"/mount/src/solsync-streamlit/images/solsync_logo.png")  # Replace with the path to your image
# Convert the image to a NumPy array
image_array = np.array(image)

selected_columns = ['grid_voltage_input', 'grid_frequency_input',
                    'ac_output_voltage', 'ac_output_frequency',
                    'ac_output_apparent_power', 'ac_output_active_power',
                    'ac_output_power_percentage', 'battery_voltage',
                    'battery_charging_current', 'battery_charging_power',
                    'battery_discharging_current', 'inverter_temperature',
                    'pv_input_voltage', 'pv_input_current',
                    'pv_input_power']
# -------------------------------------
# Dashboard Layout and Navigation
# -------------------------------------

def dashboard(user_id, username, supabase):
    if "Account_Page" not in st.session_state:
        st.session_state["Account_Page"] = False
    st.markdown("---")
    # -------------------------------
    # SIDEBAR
    # -------------------------------
    with st.sidebar:
        # (Optional) Display a logo image at the top
        st.image(image_array, width=150)

        # Welcome the user
        st.markdown(f"## 👋 Welcome, {username}!")

        # Navigation menu
        with st.expander("Navigation", icon="📃"):
            if 'navigation' not in st.session_state:
                st.session_state['navagation'] = ["Overview", "Control & Commands", "Alarms & Warnings"]           
            choice = st.radio("", st.session_state['navagation'], index=0)

        with st.expander("Filters", icon="⚡️"):
            # Filter the data displayed in the dashboard further
            data = supabase.table("company_inverters").select("inverter_id").eq("user_id", user_id).execute()
            inverter_ids = [item["inverter_id"] for item in data.data]
            device_filter = st.selectbox("Select Inverter", options=inverter_ids)

        with st.expander("Settings", icon="⚙️"):
            Account_button = st.button("👤 Account Preferences", use_container_width=True)
            if Account_button:
                st.session_state["Account_Page"] = True
            if st.button(":unlock: Sign Out", use_container_width=True):
                # Clear sign-in flags and tokens.
                js_utils.save_to_storage("sessionStorage", "is_signed", False)
                js_utils.save_to_storage("sessionStorage", "user_email", "")
                js_utils.save_to_storage("localStorage", "access_token", "")
                js_utils.refresh()  # Force a browser-level refresh via JS helper.
                st.rerun()

        st.markdown("### Contact & Support")
        st.info("Email: solsync-support@proton.me")
        st.markdown("© 2025 SolSync")

    # -------------------------------
    # MAIN CONTENT (depending on sidebar choice)
    # -------------------------------
    data_placeholder = st.empty()
    with data_placeholder:
        if st.session_state["Account_Page"]:
            with data_placeholder.container():
                # Create a placeholder for the text box where data will be refreshed
                account(supabase, user_id, inverter_ids)
        elif choice == st.session_state['navagation'][0]:
            last_param = get_from_database(supabase, user_id, device_filter)
            while True:
                with data_placeholder.container():
                    parameters = get_from_database(supabase, user_id, device_filter)
                    delta = parameters[selected_columns] - last_param[selected_columns]
                    AL1 = get_from_alarms(supabase, device_filter, "critical_alarms")
                    AL2 = get_from_alarms(supabase, device_filter, "maintenance_warnings")
                    overview(parameters, delta, AL1, AL2)
                    last_param[selected_columns] = parameters[selected_columns]
                    time.sleep(10)
        elif choice == st.session_state['navagation'][1]:
            with data_placeholder.container():
                commands(supabase, device_filter)
        elif choice == st.session_state['navagation'][2]:
            with data_placeholder.container():
                alarms(supabase, device_filter)

# For demonstration, you might call the dashboard like so:
if __name__ == "__main__":
    # Example user information. In a real app, you'd retrieve these from your authentication logic.
    demo_user_id = 123
    demo_username = "SolSync_User"
    # st_autorefresh(interval=5000, limit=100, key="data_refresh")
    dashboard(demo_user_id, demo_username)
