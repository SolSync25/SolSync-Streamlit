import re
import bcrypt
import hashlib
import base64
import streamlit as st
from protonmail import ProtonMail
import secrets
import string
import streamlit as st
import pandas as pd
import random
import skfuzzy as fuzz
import numpy as np

def str_to_flags(input_str, flags_list):
    """
    Convert a hexadecimal string (e.g., "\\x00") into the "Triggered" states 
    of a list of flags.

    Parameters:
    ----------
    input_str : str
        The hexadecimal string in \\xNN format where each bit represents the
        state (True/False) of a corresponding flag. Example: "\\x12".
    flags_list : list of dict
        A list of dictionaries where each dictionary represents a flag with
        at least a "Triggered" key that stores the state of the flag.

    Returns:
    -------
    list of dict
        The updated list of flag dictionaries with the "Triggered" state set 
        based on the corresponding bit in the input hexadecimal string.

    Example:
    --------
    Input:
        input_str = "\\x12"  # 00010010 in binary
        flags_list = [
            {"Flag": "Flag1", "Triggered": False},
            {"Flag": "Flag2", "Triggered": False},
            {"Flag": "Flag3", "Triggered": False},
            ...
        ]
    Output:
        flags_list = [
            {"Flag": "Flag1", "Triggered": False},
            {"Flag": "Flag2", "Triggered": True},  # Bit 1 is True
            {"Flag": "Flag3", "Triggered": False},
            {"Flag": "Flag4", "Triggered": False},
            {"Flag": "Flag5", "Triggered": True},  # Bit 4 is True
            ...
        ]
    """
    # Convert the hex string (e.g., \\x12) to an integer (e.g., 18)
    byte_value = int.from_bytes(bytes.fromhex(input_str[2:]), byteorder='big')

    # Map each bit of the byte to the "Triggered" state of the corresponding flag
    for i, flag in enumerate(flags_list):
        flag["Triggered"] = bool((byte_value >> i) & 1)

    return flags_list


def flags_to_str(flags_list):
    """
    Convert a list of flags with "Triggered" states into a hexadecimal string 
    (e.g., "\\x00").

    Parameters:
    ----------
    flags_list : list of dict
        A list of dictionaries where each dictionary represents a flag with
        a "Triggered" key that stores its current state (True/False).

    Returns:
    -------
    str
        The hexadecimal string in \\xNN format where each bit represents the
        state (1 for True, 0 for False) of the corresponding flag.

    Example:
    --------
    Input:
        flags_list = [
            {"Flag": "Flag1", "Triggered": False},
            {"Flag": "Flag2", "Triggered": True},   # Bit 1
            {"Flag": "Flag3", "Triggered": False},
            {"Flag": "Flag4", "Triggered": False},
            {"Flag": "Flag5", "Triggered": True},   # Bit 4
        ]
    Output:
        "\\x12"  # 00010010 in binary, 0x12 in hex
    """
    # Initialize a byte value to store the binary state of flags
    byte_value = 0

    # Traverse each flag and set the corresponding bit in the byte if "Triggered" is True
    for i, flag in enumerate(flags_list):
        if flag["Triggered"]:
            byte_value |= (1 << i)

    # Convert the byte to a hexadecimal string in \\xNN format
    return "\\x" + byte_value.to_bytes(1, byteorder='big').hex()

def get_from_alarms(supabase, inverter_id, table):
    return supabase.table(table).select("triggers").eq("inverter_id", inverter_id).execute()
    

def get_from_database(supabase, user_id, inverter_id):
    response = supabase.rpc('fetch_data_for_user_inv', {'uid': user_id, 'inv_id': inverter_id}).execute()
    data = response.data
    if data:
        df = pd.DataFrame(data)
        return df

def send_one_time_backup_code(proton_username, proton_password, recipient_email, code_length=8):
    """
    Generates a one-time backup code, creates a styled HTML email, logs into ProtonMail,
    and sends the code via email.
    
    Parameters:
      proton_username (str): Your ProtonMail email address.
      proton_password (str): Your ProtonMail password.
      recipient_email (str): The email address where the backup code will be sent.
      code_length (int): Length of the backup code (default is 8).
    
    Returns:
      str: The generated backup code.
    """
    # Generate backup code using a secure random selection from uppercase letters and digits
    pool = string.ascii_uppercase + string.digits
    backup_code = ''.join(secrets.choice(pool) for _ in range(code_length))
    
    # Optionally, if the length is 8 characters, format it into two groups (e.g., "ABCD-1234")
    if code_length == 8:
        backup_code = backup_code[:4] + '-' + backup_code[4:]
    
    # Prepare the HTML email content with inline CSS styling
    html = f"""
    <html>
      <head>
        <style>
          body {{
              font-family: Arial, sans-serif;
              background-color: #f9f9f9;
              margin: 0;
              padding: 20px;
          }}
          .container {{
              background-color: #ffffff;
              padding: 20px;
              border: 1px solid #dddddd;
              border-radius: 5px;
              max-width: 600px;
              margin: auto;
          }}
          h2 {{
              color: #333333;
          }}
          p {{
              color: #555555;
              font-size: 14px;
              line-height: 1.6;
          }}
          .code {{
              font-size: 24px;
              font-weight: bold;
              color: #ff2b2b;
              padding: 10px;
              border: 2px dashed #ff2b2b;
              display: inline-block;
              margin-top: 10px;
          }}
        </style>
      </head>
      <body>
        <div class="container">
          <h2>Your One-Time Backup Code</h2>
          <p>
            Please use the following one-time backup code for your account recovery.
            This code is valid for one use only. Make sure to store it securely.
          </p>
          <div class="code">{backup_code}</div>
          <p style="margin-top: 20px;">If you did not request this code, please ignore this email.</p>
          <p>Best,<br />Solsync Support Team</p>
        </div>
      </body>
    </html>
    """
    
    # Log in to ProtonMail
    proton = ProtonMail()
    proton.login(proton_username, proton_password)
    
    # Create the message with HTML content
    message = proton.create_message(
        recipients=[recipient_email],
        subject="Your One-Time Backup Code",
        body=html  # HTML formatted email body
    )
    
    # Send the message via ProtonMail
    sent_message = proton.send_message(message)
    
    # Optionally, you can check sent_message for confirmation details.
    return backup_code

def reset_error_flags():
    """Reset all error flags in session state."""
    if 'flags' in st.session_state:
        for key in st.session_state['flags']:
            st.session_state['flags'][key] = False

def is_valid_email(email):
    """Return True if email matches a basic email pattern."""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_regex, email))

def is_valid_pin_code(pin_code):
    """Return True if the PIN code is exactly four digits."""
    return len(pin_code) == 4 and pin_code.isdigit()

def is_valid_inverter_id(inverter_id):
    """Return True if the inverter ID starts with 'inv' and is followed by three digits."""
    return inverter_id.startswith("inv") and len(inverter_id) == 6 and inverter_id[3:].isdigit()

def generate_error_message(flags):
    """Return a combined error message for every flag that is True."""
    error_messages = {
        "invalid_email": "Invalid email address",
        "invalid_inverter_id": "Invalid inverter ID",
        "invalid_pin_code": "Invalid PIN code",
        "user_already_exists": "User with the same Email or Inverter already exists",
        "passwords_do_not_match": "Passwords do not match",
        "password_too_short": "Password must be at least 8 characters",
        "missing_data": "All data must be entered",
        "incorrect_credentials": "Incorrect email or password",
        "inverter_wrong_info": "Incorrect inverter ID or PIN code"
    }
    # Join the messages for flags that are True.
    combined_error = " | ".join(
        message for key, message in error_messages.items() if flags.get(key)
    )
    return combined_error

def hash_value(value: str) -> str:
    """
    Hash a given value (e.g., password or PIN code) using bcrypt.
    
    Returns:
        The hashed value as a UTF-8 decoded string.
    """
    # Convert the value to bytes.
    value_bytes = value.encode('utf-8')
    # Generate salt and compute hash.
    hashed = bcrypt.hashpw(value_bytes, bcrypt.gensalt())
    # Return hashed value as a string.
    return hashed.decode('utf-8')

def verify_value(plain_value: str, hashed_value: str) -> bool:
    """
    Verify that a plain text value matches the hashed value.
    
    Args:
        plain_value: The original password or PIN code.
        hashed_value: The stored hashed value.
    
    Returns:
        True if they match; otherwise, False.
    """
    return bcrypt.checkpw(plain_value.encode('utf-8'), hashed_value.encode('utf-8'))

def hash_to_complex_string(input_string, length=12):
    """
    Hashes the input string and converts it to a complex alphanumeric string.

    Parameters:
      input_string: The string to hash.
      length: Desired length of the resulting string.

    Returns:
      A string of the specified length containing alphanumeric characters.
    """
    # Generate an SHA-256 hash of the input string
    hash_object = hashlib.sha256(input_string.encode())
    hash_bytes = hash_object.digest()

    # Convert the hash to a base64-encoded string
    base64_hash = base64.urlsafe_b64encode(hash_bytes).decode('utf-8')
    
    # Truncate or pad the string to the desired length
    return base64_hash[:length]

battery_parameters = {
    "12": {
        "source_priority": 0,
        "battery_type": 1,
        "buzzer_st": False,
        "ov_bypass_st": False,
        "temp_rst_st": False,
        "bck_light_st": False,
        "psi_alarm_st": False,
        "u_max_cc":     30,
        "s_max_cc":         20,
        "battery_cov":  10.5,
        "battery_cv":   14.4,
        "battery_fcv":      13.5,
        "battery_lv_th":11.0,
        "ac_lv_th":     176,
        "ac_ol_th":           85,
        "battery_dc_th":      100
    },
    "24": {
        "source_priority": 0,
        "battery_type": 1,
        "buzzer_st": False,
        "ov_bypass_st": False,
        "temp_rst_st": False,
        "bck_light_st": False,
        "psi_alarm_st": False,
        "u_max_cc":        40,
        "s_max_cc":        30,
        "battery_cov":     21.0,
        "battery_cv":      28.8,
        "battery_fcv":     27.0,
        "battery_lv_th":   22.0,
        "ac_lv_th":        176,
        "ac_ol_th":       85,
        "battery_dc_th":  100
    },
    "48": {
        "source_priority": 0,
        "battery_type": 1,
        "buzzer_st": False,
        "ov_bypass_st": False,
        "temp_rst_st": False,
        "bck_light_st": False,
        "psi_alarm_st": False,
        "u_max_cc":   50,
        "s_max_cc":   40,
        "battery_cov":42.0,
        "battery_cv": 57.6,
        "battery_fcv":54.0,
        "battery_lv_th":44.0,
        "ac_lv_th":     176,
        "ac_ol_th":      85,
        "battery_dc_th": 100
    }
}
commands_dec = {
    "Utility First": "00",
    "Solar First": "01",
    "SBU": "02",
    "AGM (Absorbent Glass Mat)": "00",
    "Flooded battery": "01",
    "User-defined battery": "02",
    "Lib (Lithium-Ion Battery)": "08"
}

battery_state = ['accepted', 'weak', 'healthy', 'bad']

def update_to_database(supabase, inverter_id, update_values):
    table_name = "commands_state"  # Replace with your table name
    record_id = inverter_id  # Replace with the ID of the record you want to update
    # Update the record
    response = supabase.table(table_name).update(update_values).eq('inverter_id', record_id).execute()
def make_int_3inices(num):
    if num < 100:
        strn = "0"+str(num)
    else:
        strn = str(num)
    return strn
def make_int_2inices(num):
    if num < 10:
        strn = "0"+str(num)
    else:
        strn = str(num)
    return strn

def upsert_to_database(supabase, inverter_id, update_values):
    #update_values['inverter_id'] = inverter_id
    # Update the record
    response = supabase.table("commands_state").upsert(update_values, on_conflict=["inverter_id"]).execute()
def generate_random_key(length=8):
    """Generate a random key composed of lowercase letters and digits."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# ----------------------------
# Define the fuzzy inference function
# ----------------------------
def sugeno_inference(Rn_value):
    # ----------------------------
    # Define the universe for the input variable Rn
    # ----------------------------
    x_Rn = np.arange(0, 15.1, 0.1)

    # ----------------------------
    # Define membership functions for Rn
    # ----------------------------
    # "s": Triangular membership function with points [0.5, 3.5, 4]
    mf_s = fuzz.trimf(x_Rn, [0.5, 3.5, 4])
    # "m": Triangular membership function with points [3, 6, 12]
    mf_m = fuzz.trimf(x_Rn, [3, 6, 12])
    # "vs": Trapezoidal membership function with points [-4, -1.25, 1.25, 4]
    mf_vs = fuzz.trapmf(x_Rn, [-4, -1.25, 1.25, 4])
    # "l": Trapezoidal membership function with points [4, 10, 16.5, 28.5]
    mf_l = fuzz.trapmf(x_Rn, [4, 10, 16.5, 28.5])
    out_bad = 0
    out_weak = 0.58
    out_accepted = 0.7
    out_healthy = 1

    if Rn_value > 15.0:
        Rn_value = 15.0
    # Calculate membership degrees for the input value
    # get the membership degrees for a given input value
    deg_s = fuzz.interp_membership(x_Rn, mf_s, Rn_value)
    deg_m = fuzz.interp_membership(x_Rn, mf_m, Rn_value)
    deg_vs = fuzz.interp_membership(x_Rn, mf_vs, Rn_value)
    deg_l = fuzz.interp_membership(x_Rn, mf_l, Rn_value)

    # Define the rule outputs and their firing strengths.
    # Each rule fires with a strength equal to the membership degree of its antecedent.
    # Rule 1: if Rn is vs then SOH = healthy (1)
    w1 = deg_vs
    # Rule 2: if Rn is s then SOH = accepted (0.7)
    w2 = deg_s
    # Rule 3: if Rn is m then SOH = weak (0.58)
    w3 = deg_m
    # Rule 4: if Rn is l then SOH = bad (0)
    w4 = deg_l

    # Calculate weighted average (Sugeno defuzzification):
    numerator = w1 * out_healthy + w2 * out_accepted + w3 * out_weak + w4 * out_bad
    denominator = w1 + w2 + w3 + w4

    # Avoid division by zero; if no rule fires, return None or some default value.
    if denominator == 0:
        return None, (deg_s, deg_m, deg_vs, deg_l)

    output = numerator / denominator
    return output, (deg_s, deg_m, deg_vs, deg_l)

def count_ones_in_hex(hex_string):
    try:
        # Convert the hexadecimal part of the string to an integer
        hex_value = int(hex_string[2:], 16)
        # Convert the integer to binary and count the number of ones
        ones_count = bin(hex_value).count('1')
        return ones_count
    except ValueError:
        return "Invalid input! Please provide a string in the format '\\xNN'."
