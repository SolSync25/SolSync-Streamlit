import streamlit as st
import modules.styles as styles
from postgrest.exceptions import APIError
from time import sleep
import modules.utils as utils
import modules.js_utils as js_utils

def login(supabase):
    # Initialize session state values if not already set.
    if 'is_signin' not in st.session_state:
        st.session_state['is_signin'] = True  # True: Show Sign In, False: Show Sign Up
    if 'email_token' not in st.session_state:
        st.session_state['email_token'] = ""
    if 'remember_me' not in st.session_state:
        st.session_state['remember_me'] = False
    if 'toggle_label' not in st.session_state:
        st.session_state['toggle_label'] = "Sign Up"
    if 'toggle_text' not in st.session_state:
        st.session_state['toggle_text'] = "Don't have an account?"
    if "clicked_once" not in st.session_state:
        st.session_state["clicked_once"] = False
    if "recovery_code" not in st.session_state:
        st.session_state["recovery_code"] = ""
    if 'flags' not in st.session_state:
        st.session_state['flags'] = {
            "invalid_email": False,
            "invalid_inverter_id": False,
            "invalid_pin_code": False,
            "user_already_exists": False,
            "passwords_do_not_match": False,
            "password_too_short": False,
            "missing_data": False,
            "incorrect_credentials": False,
            "inverter_wrong_info": False,
            "sign_up_success": False,
            "sign_in_success": False
        }
    
    # Apply custom CSS styles from your styles module.
    st.markdown(styles.container, unsafe_allow_html=True)
    st.markdown(styles.button_dark, unsafe_allow_html=True)
    # st.markdown(styles.button_light, unsafe_allow_html=True)

    # Main container.
    with st.container(border=True):
        col1, col2 = st.columns([0.45, 0.55])
        with col1:
            if st.session_state['is_signin']:
                signin(supabase)
            else:
                signup(supabase)
        with col2:
            with st.container(key="col2"):
                st.header("Welcome to SolSync")
                st.write(st.session_state['toggle_text'])
                if st.button(st.session_state['toggle_label']):
                    # Toggle between Sign In and Sign Up.
                    st.session_state['is_signin'] = not st.session_state['is_signin']
                    if st.session_state['is_signin']:
                        st.session_state['toggle_label'] = "Sign Up"
                        st.session_state['toggle_text'] = "Don't have an account?"
                    else:
                        st.session_state['toggle_label'] = "Sign In"
                        st.session_state['toggle_text'] = "Already have an account?"
                    st.rerun()
        
        # Display error messages if present.
        error_msg = utils.generate_error_message(st.session_state['flags'])
        if error_msg:
            st.error(error_msg, icon="🚨")
        elif st.session_state['flags']['sign_up_success']:
            st.success("Account created successfully!", icon="✅")
        elif st.session_state['flags']['sign_in_success']:
            # Mark the user as signed in (session-only).
            js_utils.save_to_storage("sessionStorage", "is_signed", True)
            # Save the user's email so that the main function can later look it up.
            js_utils.save_to_storage("sessionStorage", "user_email", st.session_state['email_token'])
            
            token = ""
            if st.session_state['remember_me']:
                # If "Remember Me" is checked, generate a token and save it in local storage.
                token = utils.hash_to_complex_string(st.session_state['email_token'])
                js_utils.save_to_storage("localStorage", "access_token", token)
                # Update Supabase user authentication record with the new token.
                supabase.table("user_authentication").update({'access_token': token}).eq("email", st.session_state['email_token']).execute()
                # Query using the token.
                data = supabase.table("user_authentication").select("id").eq("access_token", token).execute()
            else:
                # Query using the email if no token is stored.
                data = supabase.table("user_authentication").select("id").eq("email", st.session_state['email_token']).execute()
            
            if data.data and len(data.data) > 0:
                userID = data.data[0]['id']
                st.session_state['user_id'] = userID
            else:
                st.error("User lookup failed.")
                return
            
            st.success("Access granted!", icon="✅")
            sleep(0.5)
            js_utils.refresh()  # Force a browser refresh if necessary.
            st.rerun()

def signup(supabase):
    st.header("Sign Up")
    # Reset error flags at the start of the sign-up form.
    utils.reset_error_flags()
    
    # Layout for Email and Username.
    col1, col2 = st.columns(2, vertical_alignment="center")
    with col1:
        email = st.text_input("Email*", placeholder="john.doe@example.com").strip()
    with col2:
        username = st.text_input("Username*", placeholder="JohnDoe").strip()
    
    # Layout for Inverter ID and PIN Code.
    col3, col4 = st.columns(2, vertical_alignment="center")
    with col3:
        inverter_id = st.text_input("Inverter ID*", placeholder="inv###", max_chars=6).strip()
    with col4:
        pin_code = st.text_input("PIN Code*", placeholder="####", max_chars=4).strip()
    
    # Layout for Password and Confirm Password.
    col5, col6 = st.columns(2, vertical_alignment="center")
    with col5:
        password = st.text_input("Password*", type="password").strip()
    with col6:
        confirm_password = st.text_input("Confirm Password*", type="password").strip()
    
    if st.button("Sign Up", use_container_width=True):
        # Validate that all required fields are filled.
        fields_filled = all([username, password, email, inverter_id, pin_code])
        st.session_state['flags']['missing_data'] = not fields_filled
        
        # Field-specific validations.
        if email and not utils.is_valid_email(email):
            st.session_state['flags']['invalid_email'] = True
        
        if inverter_id and not utils.is_valid_inverter_id(inverter_id):
            st.session_state['flags']['invalid_inverter_id'] = True
        
        if pin_code and not utils.is_valid_pin_code(pin_code):
            st.session_state['flags']['invalid_pin_code'] = True
        
        if password and len(password) < 8:
            st.session_state['flags']['password_too_short'] = True
        
        if password and confirm_password and (password != confirm_password):
            st.session_state['flags']['passwords_do_not_match'] = True
        
        # If any flag validations fail, do not proceed.
        if any(st.session_state['flags'].values()):
            return
        
        # **Inverter Validation Step:**
        # Verify the provided inverter_id exists and that the provided pin_code matches
        # the company record before creating a new user.
        try:
            inverter_data_response = supabase.table("company_inverters") \
                .select("inverter_id", "pin_code") \
                .eq("inverter_id", inverter_id) \
                .execute()
            
            if not inverter_data_response.data:
                st.session_state['flags']['inverter_wrong_info'] = True
                st.error("Provided Inverter ID does not exist in our records.")
                return
            
            company_inverter = inverter_data_response.data[0]
            
            # Compare the entered PIN with the company's record.
            if not utils.verify_value(pin_code, company_inverter['pin_code']):
                st.session_state['flags']['inverter_wrong_info'] = True
                st.error("Provided PIN Code does not match our records for the given Inverter ID.")
                return
        except Exception as e:
            st.error(f"Error accessing company inverter data: {e}")
            return
        
        # Proceed with user registration.
        try:
            response = supabase.table("user_authentication").insert({
                "username": username,
                "password": utils.hash_value(password),
                "email": email,
            }).execute()
            
            if response.data and len(response.data) > 0:
                new_user = response.data[0]
                user_id = new_user['id']  # The id of the newly registered user.
                
                # **Link the User with the Inverter:**
                # Update the company_inverters table to link this inverter with the new user.
                link_response = supabase.table("company_inverters") \
                    .update({"user_id": user_id}) \
                    .eq("inverter_id", inverter_id) \
                    .execute()
                
                if not (link_response.data and len(link_response.data) > 0):
                    st.error("Failed to link your account with the inverter. Please try again later.")
                    return
                
                st.session_state['flags']['sign_up_success'] = True
                # Optionally, switch to the Sign In view after successful registration.
                st.session_state['is_signin'] = True
                st.session_state['toggle_label'] = "Sign Up"
                st.session_state['toggle_text'] = "Don't have an account?"
                sleep(2)
                st.rerun()
        except APIError as e:
            st.session_state['flags']['user_already_exists'] = True

# --- Placeholder for sign-in function ---
def signin(supabase):
    st.header("Sign In")
    # Reset error flags at the start of the sign-in form.
    utils.reset_error_flags()
    
    # Layout for Sign In.
    email = st.text_input("Email", placeholder="john.doe@example.com").strip()
    password = st.text_input("Password", type="password").strip()
    login_button = st.button("Sign In", use_container_width=True)
    col1, col2 = st.columns([0.6, 0.4], vertical_alignment="center")
    remember_me = col1.checkbox("Remember Me")
    st.session_state['remember_me'] = remember_me
    
    with col2:
        with st.popover("Forgot Password?", use_container_width=True, icon='🔐'):                    
            with st.form("RST", border=False):
                recovery_code = st.text_input("Recovery Code*").strip()
                new_password = st.text_input("New Password*", type="password").strip()
                confirm_password = st.text_input("Confirm Password*", type="password").strip()
                if st.form_submit_button("Reset Password", use_container_width=True):
                    # Validate that all required fields are filled.
                    fields_filled = all([email, recovery_code, new_password, confirm_password])
                    st.session_state['flags']['missing_data'] = not fields_filled
                    
                    if new_password and len(new_password) < 8:
                        st.session_state['flags']['password_too_short'] = True
                    
                    if new_password and confirm_password and (new_password != confirm_password):
                        st.session_state['flags']['passwords_do_not_match'] = True

                    flags_to_check = ["invalid_email", "passwords_do_not_match", "password_too_short", "missing_data"]
                    if all(not st.session_state['flags'][flag] for flag in flags_to_check):
                        # user_response = supabase.table("user_authentication").select("id").eq("email", email).execute()
                        if recovery_code == st.session_state["recovery_code"]:
                            supabase.table("user_authentication").update({"password":utils.hash_value(new_password)}).eq("email", email).execute()
                            st.success("Password reset")
                        else:
                            st.error("This code is wrong")
                
                if st.form_submit_button("Send Recovery Code", use_container_width=True):
                    if email:
                        if not st.session_state["clicked_once"]:
                            st.session_state["clicked_once"] = True
                            api_email = st.secrets.email
                            api_pass = st.secrets.password
                            st.session_state["recovery_code"] = utils.send_one_time_backup_code(api_email, api_pass, email.strip())
                            # st.session_state["recovery_code"] = "3VFO-S14S"
                            st.success("Recovery code sent")
                        else:
                            st.error("Code can be sent only once!")
                    else:
                        st.error("Email must be entered")
                        
    if login_button:        
        # Validate required fields.
        fields_filled = all([password, email])
        st.session_state['flags']['missing_data'] = not fields_filled

        st.session_state['email_token'] = email  # Save the email for later use.

        # Validate field constraints.
        if email and not utils.is_valid_email(email):
            st.session_state['flags']['invalid_email'] = True

        if password and len(password) < 8:
            st.session_state['flags']['password_too_short'] = True

        flags_to_check = ["invalid_email", "password_too_short", "missing_data", "incorrect_credentials"]
        if all(not st.session_state['flags'][flag] for flag in flags_to_check):
            data = supabase.table("user_authentication").select("*").eq("email", email).execute()
            if len(data.data) and utils.verify_value(password, data.data[0]['password']):
                st.session_state['flags']['sign_in_success'] = True
            else:
                st.session_state['flags']['incorrect_credentials'] = True


if __name__ == "__main__":
    login()
