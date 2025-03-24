import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone
import random
import utils
import js_utils
from time import sleep, strftime
from postgrest.exceptions import APIError

def overview(data_table, delta, AL1, AL2):
    utc_time = datetime.fromisoformat(data_table.updated_at[0])
    # Define GMT+3 timezone
    gmt_plus_three = timezone(timedelta(hours=3))
    # Convert UTC time to GMT+3
    local_time = utc_time.astimezone(gmt_plus_three)
    # Format the time to "YYYY-MM-DD HH:MM:SS"
    timeing = local_time.strftime("%Y-%m-%d %H:%M:%S")
    st.write(f"Latest update: {timeing} (GMT+3)")
    c1 = st.container()
    with c1:
        # Convert the given timestamp to a datetime object
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1.2, 2, 1, 2, 1.1, 2, 1.2, 2], vertical_alignment="center")
        col1.write("**Inverter Status:**")
        with col2:
            if data_table.online[0]:
                st.success("Online")
            else:
                st.error("Offline")
        col3.write("**Mode:**")
        with col4:
            if data_table.device_status[0] == "P":
                st.info("Power ON 🔆")
            elif data_table.device_status[0] == "S":
                st.info("Standby 💤")
            elif data_table.device_status[0] == "L":
                st.info("Line 🔌")
            elif data_table.device_status[0] == "B":
                st.info("Battery 🔋")
            else:
                st.info("None")
        col5.write("**Alarms Count:**")
        col6.error(f"{utils.count_ones_in_hex(AL1.data[0]['triggers'])} Alarms(s)")
        col7.write("**Warnings Count:**")
        col8.warning(f"{utils.count_ones_in_hex(AL2.data[0]['triggers'])} Warning(s)")

        st.write('## Grid')
        col1, col2, col3 = st.columns(3)
        col1.container(border=True).metric("Grid Voltage", f"{data_table.grid_voltage_input[0]:.2f} V",
                                           f"{delta.grid_voltage_input[0]:.2f} V")
        col2.container(border=True).metric("Grid Frequency", f"{data_table.grid_frequency_input[0]:.2f} Hz",
                                           f"{delta.grid_frequency_input[0]:.2f} Hz")
        col3.container(border=True).metric("Inverter Temperature", f"{data_table.inverter_temperature[0]:.2f} °C",
                                           f"{delta.inverter_temperature[0]:.2f} °C")

        st.write("---")
        st.write('## AC Output')
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.container(border=True).metric("AC Output Voltage", f"{data_table.ac_output_voltage[0]:.2f} V",
                                           f"{delta.ac_output_voltage[0]:.2f} V")
        col2.container(border=True).metric("AC Output Frequency", f"{data_table.ac_output_frequency[0]:.2f} Hz",
                                           f"{delta.ac_output_frequency[0]:.2f} Hz")
        col3.container(border=True).metric("AC Output Apparent Power", f"{data_table.ac_output_apparent_power[0]:.2f} VA",
                                           f"{delta.ac_output_apparent_power[0]:.2f} VA")
        col4.container(border=True).metric("AC Output Active Power", f"{data_table.ac_output_active_power[0]:.2f} W",
                                           f"{delta.ac_output_active_power[0]:.2f} W")
        col5.container(border=True).metric("AC Output Power Percentage",
                                           f"{data_table.ac_output_power_percentage[0]:.2f} %",
                                           f"{delta.ac_output_power_percentage[0]:.2f} %")

        st.write("---")
        st.write('## Battery')
        col1, col2, col3, col4 = st.columns(4)
        col1.container(border=True).metric("Battery Voltage", f"{data_table.battery_voltage[0]:.2f} V",
                                           f"{delta.battery_voltage[0]:.2f} V")
        col2.container(border=True).metric("Battery Charging Current", f"{data_table.battery_charging_current[0]:.2f} A",
                                           f"{delta.battery_charging_current[0]:.2f} A")
        col3.container(border=True).metric("Battery Charging Power", f"{data_table.battery_charging_power[0]:.2f} W",
                                           f"{delta.battery_charging_power[0]:.2f} W")
        col4.container(border=True).metric("Battery Discharging Current ",
                                           f"{data_table.battery_discharging_current[0]:.2f} A",
                                           f"{delta.battery_discharging_current[0]:.2f} A")

        st.write("---")
        st.write('## Photovoltaic')
        col1, col2, col3 = st.columns(3)
        col1.container(border=True).metric("PV Input Voltage", f"{data_table.pv_input_voltage[0]:.2f} V",
                                           f"{delta.pv_input_voltage[0]:.2f} V")
        col2.container(border=True).metric("PV Input Current", f"{data_table.pv_input_current[0]:.2f} A",
                                           f"{delta.pv_input_current[0]:.2f} A")
        col3.container(border=True).metric("PV Input Power", f"{data_table.pv_input_power[0]:.2f} W",
                                           f"{delta.pv_input_power[0]:.2f} W")

def commands(supabase, device_filter):

    st.header("Control & Commands")

    st.session_state["missing_data"] = False
    st.session_state["system_update"] = False

    # Retrieve battery data from the database for the given inverter_id.
    response = supabase.table("battery_system").select("*").eq("inverter_id", device_filter).execute()
    if response.data:
        record = response.data[0]
    else:
        # If no record is found, use default values.
        record = {
            "battery_voltage": 1,     # Default voltage (could be None if preferred)
            "battery_AH": 100,          # Default Ampere-Hour value
            "battery_type": 1,        # Default battery type-index
            "enable_commands": False  # Default commands state
        }

    # Create a form to update the values.
    with st.form("battery_form"):
        st.subheader("Battery System")
        battery_voltage = st.selectbox(
            "Battery Voltage [V]",
            options=["12", "24", "48"],
            index=["12", "24", "48"].index(str(record["battery_voltage"])) if str(record["battery_voltage"]) in ["12", "24", "48"] else 1
        )
        battery_AH = st.number_input("Battery Ampere-Hour [Ah]", min_value=0, step=10, value=int(record["battery_AH"]))
        battery_type_str = st.selectbox(
            "Battery Type",
            options=["AGM (Absorbent Glass Mat)", "Flooded battery", "User-defined battery", "Lib (Lithium-Ion Battery)"],
            index=record["battery_type"] if record["battery_type"] in range(4) else 1
        )

        col1, _, col2 = st.columns([0.2,0.55,0.25])
        with col2:
            enable_commands = st.toggle("Enable Commands", value=record["enable_commands"])
        
        with col1:
            if st.form_submit_button("Submit", use_container_width=True):
                if battery_voltage and battery_type_str:
                    # Prepare the data to save. Note that for battery voltage we convert the string to int.
                    data = {
                        "inverter_id": device_filter,
                        "battery_voltage": int(battery_voltage),
                        "battery_AH": int(battery_AH),
                        "battery_type": ["AGM (Absorbent Glass Mat)", "Flooded battery", "User-defined battery", "Lib (Lithium-Ion Battery)"].index(battery_type_str),
                        "enable_commands": enable_commands
                    }
                    supabase.table("battery_system").upsert(data, on_conflict=["inverter_id"]).execute()
                    st.session_state["system_update"] = True
                    update_values = {
                        "inverter_id":device_filter,
                        "source_priority": utils.make_int_2inices(
                            utils.battery_parameters[battery_voltage]["source_priority"]),
                        "u_max_cc": utils.make_int_3inices(utils.battery_parameters[battery_voltage]["u_max_cc"]),
                        "s_max_cc": utils.make_int_3inices(utils.battery_parameters[battery_voltage]["s_max_cc"]),
                        "battery_cov": str(round(utils.battery_parameters[battery_voltage]["battery_cov"], 1)),
                        "battery_cv": str(round(utils.battery_parameters[battery_voltage]["battery_cv"], 1)),
                        "battery_fcv": str(round(utils.battery_parameters[battery_voltage]["battery_fcv"], 1)),
                        "battery_type": utils.commands_dec[battery_type_str],
                        "buzzer_st": utils.battery_parameters[battery_voltage]["buzzer_st"],
                        "ov_bypass_st": utils.battery_parameters[battery_voltage]["ov_bypass_st"],
                        "temp_rst_st": utils.battery_parameters[battery_voltage]["temp_rst_st"],
                        "bck_light_st": utils.battery_parameters[battery_voltage]["bck_light_st"],
                        "psi_alarm_st": utils.battery_parameters[battery_voltage]["psi_alarm_st"],
                        "defult_value": False,
                        "battery_lv_th": round(utils.battery_parameters[battery_voltage]["battery_lv_th"], 1),
                        "ac_lv_th": round(utils.battery_parameters[battery_voltage]["ac_lv_th"], 1),
                        "ac_ol_th": round(utils.battery_parameters[battery_voltage]["ac_ol_th"], 1),
                        "battery_dc_th": round(utils.battery_parameters[battery_voltage]["battery_dc_th"], 1),
                        "cf": True
                    }
                    utils.upsert_to_database(supabase, device_filter, update_values)
                    js_utils.refresh()
                else:
                    st.session_state["missing_data"] = True
        
        if st.session_state["system_update"]:
            st.success('Battery system updated', icon="✅")
        elif st.session_state["missing_data"]:
            st.error('All data must be entered', icon="🚨")

    # Use a form so user changes can be submitted all at once.
    with st.form("settings_form"):
        # Initialize session_state values if not already set
        # Retrieve battery data from the database for the given inverter_id.


        response = supabase.table("commands_state").select("*").eq("inverter_id", device_filter).execute()

        if response.data:
            record = response.data[0]
        else:
            # If no record is found, use default values.
            record = utils.battery_parameters[battery_voltage]

        st.subheader("Update Settings")

        # Create input widgets for each setting.
        # We use text_input to allow changes to the command string.
        source_priority_input = st.selectbox("1. Source Priority", ["Utility First", "Solar First", "SBU"], index=int(record["source_priority"]), help="SBU: Solar>Battery>Utility")
        

        with st.container(border=True):
            st.write("Status Enable/Disable")
            col1, col2 = st.columns(2)
            with col1:
                status_input_a = st.checkbox(label="Silence Buzzer", value=record["buzzer_st"])
                status_input_b = st.checkbox(label="Overload Bypass", value=record["ov_bypass_st"])
                status_input_v = st.checkbox(label="Over Temperature Restart", value=record["temp_rst_st"])
            with col2:
                status_input_x = st.checkbox(label="Backlight ON", value=record["bck_light_st"])
                status_input_y = st.checkbox(label="Alarm ON When Primary Source Interrupt", value=record["psi_alarm_st"])
                inverter_defaults = st.checkbox(label="Setting control parameters to default value", value=record["defult_value"], help="On inverter level")
        
        utility_current_input = st.number_input("2. Utility Max Charging Current", min_value=10, max_value=100+ 1, value= int(record["u_max_cc"]), step=10)

        solar_current_input = st.number_input("3. Solar Max Charging Current", min_value=10, max_value=120+ 1, value=int(record["s_max_cc"]), step=10)
        
        battery_cutoff_input = st.number_input("4. Battery Cut-Off Voltage", min_value=utils.battery_parameters[battery_voltage]["battery_cov"] - 1, max_value=float(battery_voltage)+ 1, value=float(record["battery_cov"]), step=0.1, help="Battery under voltage")

        battery_charging_input = st.number_input("5. Battery Charging Voltage", min_value=float(battery_voltage)- 1, max_value=float(battery_voltage)*1.2 + 1, value=float(record["battery_cv"]), step=0.1, help="C.V (Constant Voltage)")
        
        battery_float_input = st.number_input("6. Battery Float Charging Voltage", min_value=float(battery_voltage)- 1, max_value=float(battery_voltage)*1.2 + 1, value=float(record["battery_fcv"]), step=0.1)
        
        battery_low_voltage_input = st.number_input("11. Battery Low Voltage Alarm", min_value=battery_cutoff_input - 1, max_value=battery_float_input + 1, value=float(record["battery_lv_th"]), step=0.1)
        
        low_ac_voltage_input = st.number_input("12. Low AC Output Voltage Alarm", min_value=160, max_value=220, value=int(record["ac_lv_th"]), step=10)
        
        high_ac_load_input = st.number_input("13. High AC Output Load Power Alarm %", min_value=50, max_value=90, value=int(record["ac_ol_th"]), step=5)
        
        high_battery_current_input = st.number_input("14. High Battery Discharge Current Alarm", min_value=20, max_value=150, value=int(record["battery_dc_th"]), step=10)

        col1, _, col2 = st.columns([0.2,0.6,0.2])
        with col1:
            submitted = st.form_submit_button("Save Changes", use_container_width=True, disabled= not enable_commands)
            if submitted :
                update_values = {
                    "source_priority": utils.commands_dec[source_priority_input],
                    "u_max_cc": utils.make_int_3inices(utility_current_input),
                    "s_max_cc": utils.make_int_3inices(solar_current_input),
                    "battery_cov": str(round(battery_cutoff_input, 1)),
                    "battery_cv": str(round(battery_charging_input, 1)),
                    "battery_fcv": str(round(battery_float_input, 1)),
                    "battery_type": utils.commands_dec[battery_type_str],
                    "buzzer_st": status_input_a,
                    "ov_bypass_st": status_input_b,
                    "temp_rst_st": status_input_v,
                    "bck_light_st": status_input_x,
                    "psi_alarm_st": status_input_y,
                    "defult_value": inverter_defaults,
                    "battery_lv_th": round(battery_low_voltage_input, 1),
                    "ac_lv_th": round(low_ac_voltage_input, 1),
                    "ac_ol_th": round(high_ac_load_input, 1),
                    "battery_dc_th":  round(high_battery_current_input, 1),
                    "cf": True
                }
                utils.update_to_database(supabase, device_filter, update_values)
        with col2:
            reseted = st.form_submit_button("Reset to Default", use_container_width=True, disabled= not enable_commands)
            if reseted:
                update_values = {
                    "source_priority": utils.make_int_2inices(utils.battery_parameters[battery_voltage]["source_priority"]),
                    "u_max_cc": utils.make_int_3inices(utils.battery_parameters[battery_voltage]["u_max_cc"]),
                    "s_max_cc": utils.make_int_3inices(utils.battery_parameters[battery_voltage]["s_max_cc"]),
                    "battery_cov": str(round(utils.battery_parameters[battery_voltage]["battery_cov"], 1)),
                    "battery_cv": str(round(utils.battery_parameters[battery_voltage]["battery_cv"], 1)),
                    "battery_fcv": str(round(utils.battery_parameters[battery_voltage]["battery_fcv"], 1)),
                    "battery_type": utils.make_int_2inices(utils.battery_parameters[battery_voltage]["battery_type"]),
                    "buzzer_st": utils.battery_parameters[battery_voltage]["buzzer_st"],
                    "ov_bypass_st": utils.battery_parameters[battery_voltage]["ov_bypass_st"],
                    "temp_rst_st": utils.battery_parameters[battery_voltage]["temp_rst_st"],
                    "bck_light_st": utils.battery_parameters[battery_voltage]["bck_light_st"],
                    "psi_alarm_st": utils.battery_parameters[battery_voltage]["psi_alarm_st"],
                    "defult_value": False,
                    "battery_lv_th": round(utils.battery_parameters[battery_voltage]["battery_lv_th"], 1),
                    "ac_lv_th": round(utils.battery_parameters[battery_voltage]["ac_lv_th"], 1),
                    "ac_ol_th": round(utils.battery_parameters[battery_voltage]["ac_ol_th"], 1),
                    "battery_dc_th":  round(utils.battery_parameters[battery_voltage]["battery_dc_th"], 1),
                    "cf": True
                }
                utils.update_to_database(supabase, device_filter, update_values)
                js_utils.refresh()

        
def alarms(supabase, device_filter):
    ch_f = False
    # Define the critical alarms and maintenance warnings
    critical_alarms = [
        {"Flag": "Battery Low Voltage", "Message": "Attention! The battery voltage is critically low. Please take immediate action to prevent potential damage.", "Triggered": False},
        {"Flag": "Low AC Output Voltage", "Message": "Alert! The AC output voltage is currently below the acceptable level. This may affect the performance of connected devices.", "Triggered": False},
        {"Flag": "High AC Output Load Power Percentage", "Message": "Warning: High AC Output Load Power! Your system is experiencing a high load. The AC output power percentage has exceeded safe limits.", "Triggered": False},
        {"Flag": "High Battery Discharging Current", "Message": "Warning: High Battery Discharging Current! The battery is discharging at a high level. Please check the load conditions.", "Triggered": False},
        {"Flag": "High Inverter Temperature", "Message": "Warning: High Inverter Temperature! The inverter temperature is above safe levels. Check ventilation immediately.", "Triggered": False},
        {"Flag": "Device Warning Status", "Message": "Warning: Inverter Fault Detected! Check the system and consult the manual for troubleshooting.", "Triggered": False},
        {"Flag": "High AC Output Frequency", "Message": "Warning: High AC Output Frequency! The frequency is above normal levels. Please check the system.", "Triggered": False},
        {"Flag": "Low AC Output Frequency", "Message": "Warning: Low AC Output Frequency! The frequency is below the normal range. Please check inverter settings.", "Triggered": False},
    ]

    maintenance_warnings = [
        {"Flag": "Full Discharge Cycle", "Message": "Warning: Full Discharge Cycle Counted! A full discharge cycle has been completed. Monitor battery health and recharge as needed.", "Triggered": False},
        {"Flag": "PV Cleaning Time", "Message": "Warning: PV Cleaning Required! It's time to clean the solar panels for optimal performance. Please schedule cleaning.", "Triggered": False},
        {"Flag": "Battery Check", "Message": "Warning: Battery Check Required! Please inspect the battery's condition and connections for safety.", "Triggered": False},
        {"Flag": "Total Statistics Display", "Message": "Warning: Total Statistics Display Alert! The total statistics are available. Please review.", "Triggered": False},
    ]

    data = supabase.table("critical_alarms").select("triggers", "updated_at").eq("inverter_id", device_filter).execute()

    # Convert the given timestamp to a datetime object
    utc_time = datetime.fromisoformat(data.data[0]['updated_at'])
    # Define GMT+3 timezone
    gmt_plus_three = timezone(timedelta(hours=3))
    # Convert UTC time to GMT+3
    local_time = utc_time.astimezone(gmt_plus_three)
    # Format the time to "YYYY-MM-DD HH:MM:SS"
    timeing = local_time.strftime("%Y-%m-%d %H:%M:%S")

    # Input the current state in \xNN format
    input_str = data.data[0]['triggers']

    # Update alarm states based on input string
    critical_alarms = utils.str_to_flags(input_str, critical_alarms)

    # Create a DataFrame for all alarms
    critical_alarms_df = pd.DataFrame(critical_alarms)

    # Display only Triggered Critical Alarms
    st.markdown("## Critical Alarms")
    st.write(f"Latest update: {timeing} (GMT+3)")
    triggered_critical_alarms = critical_alarms_df[critical_alarms_df["Triggered"]]  # Filter for triggered alarms
    if not triggered_critical_alarms.empty:
        st.dataframe(triggered_critical_alarms[["Flag", "Message"]], use_container_width=True, hide_index=True)
    else:
        st.dataframe(pd.DataFrame(columns=["Flag", "Message"]), use_container_width=True, hide_index=True)

    # ===============================================
    st.write('---')
    data = supabase.table("maintenance_warnings").select("triggers", "updated_at").eq("inverter_id", device_filter).execute()

    # Convert the given timestamp to a datetime object
    utc_time = datetime.fromisoformat(data.data[0]['updated_at'])
    # Define GMT+3 timezone
    gmt_plus_three = timezone(timedelta(hours=3))
    # Convert UTC time to GMT+3
    local_time = utc_time.astimezone(gmt_plus_three)
    # Format the time to "YYYY-MM-DD HH:MM:SS"
    timeing = local_time.strftime("%Y-%m-%d %H:%M:%S")
    # Display Maintenance Warnings
    st.markdown("## Maintenance Warnings")
    st.write(f"Latest update: {timeing} (GMT+3)")

    # Input the current state in \xNN format
    input_str = data.data[0]['triggers']

    # Update alarm states based on input string
    maintenance_warnings = utils.str_to_flags(input_str, maintenance_warnings)

    # Create a DataFrame for all alarms
    maintenance_warnings_df = pd.DataFrame(maintenance_warnings)

    # Display only Triggered Maintenance Warnings
    triggered_maintenance_warnings = maintenance_warnings_df[maintenance_warnings_df["Triggered"]]  # Filter for triggered alarms
    if not triggered_maintenance_warnings.empty:
        st.dataframe(triggered_maintenance_warnings[["Flag", "Message"]], use_container_width=True, hide_index=True)
    else:
        st.dataframe(pd.DataFrame(columns=["Flag", "Message"]), use_container_width=True, hide_index=True)

    # Reset Maintenance Warnings Button

    if st.button("Verify"):
        code = supabase.table("maintenance_warnings").update({"triggers" : "\\x00"}).eq("inverter_id", device_filter).execute()
        st.write(f"You clicked the button on iteration!")
        code = supabase.table("SOH").update({"CFDC": False, "battery_cheak": False, "clean_PV_panels": False,  "statistics_ready": False}).eq("inverter_id", device_filter).execute()
        st.rerun()
    
    # fuzzy:
    st.write("---")

    Rn = supabase.table("SOH").select("Rn").eq("inverter_id",device_filter).execute()
    Rn = Rn.data[0]['Rn']
    if Rn is not None and Rn != 0:
        with st.expander("press to View Battery Health"):
            st.subheader("State of health (SOH)")
            output_value, memberships = utils.sugeno_inference(float(Rn))
            max_value = max(memberships)
            max_index = memberships.index(max_value)
            utils.battery_wdg(output_value)



    # Display the Plotly chart
    data = supabase.table("SOH").select("statistics_ready", "statistics_ready_date", "Cday_copy", "Pday_copy").eq("inverter_id", device_filter).execute()
    # Convert the given timestamp to a datetime object
    data_cheak = len(data.data[0]['Pday_copy'])
    if data_cheak > 0:
        with st.expander("press to View Statistics"):
            st.subheader("Total Statistics Display")
            utc_time = datetime.fromisoformat(data.data[0]['statistics_ready_date'])
            # Define GMT+3 timezone
            gmt_plus_three = timezone(timedelta(hours=3))
            # Convert UTC time to GMT+3
            local_time = utc_time.astimezone(gmt_plus_three)
            # Format the time to "YYYY-MM-DD HH:MM:SS"
            timeing = local_time.strftime("%Y-%m-%d %H:%M:%S")
            date = utils.get_last_30_days(datetime.strptime(timeing, "%Y-%m-%d %H:%M:%S"))
            fig = utils.create_plotly_chart_power(date, data.data[0]['Pday_copy'], timeing)
            fig2 = utils.create_plotly_chart_dcc(date, data.data[0]['Cday_copy'], timeing)
            st.plotly_chart(fig, use_container_width=True, key="plot1")
            st.plotly_chart(fig2, use_container_width=True, key="plot2")


def account(supabase, user_id, inverter_ids):
    if 'flags' not in st.session_state:
        st.session_state['flags'] = {
            "invalid_email": False,
            "invalid_inverter_id": False,
            "invalid_pin_code": False,
            "user_already_exists": False,
            "passwords_do_not_match": False,
            "password_too_short": False,
            "missing_data": False,
            "inverter_wrong_info": False,
            "reset_success": False,
            "save_success": False,
            "link_success": False,
            "delete_all": False,
            "used_inverter": False,
            "wrong_password": False,
        }
    else:
        utils.reset_error_flags()

    col1, _, col2 = st.columns([0.7,0.15,0.15], vertical_alignment='center')
    col1.header("Account Preferences")
    back = col2.button("⬅ Back", use_container_width=True)
    if back:
        st.session_state["Account_Page"] = False
        st.rerun()
    st.write("Manage your profile, account settings, and preferences for your SolSync experience")
    
    with st.container(border=True):
        st.write("### Account Information")
        st.write("---")

        data = supabase.table("user_authentication").select("username", "email").eq("id", user_id).execute()
        username = st.text_input("Username", value=data.data[0]["username"]).strip()
        email = st.text_input("Email", value=data.data[0]["email"]).strip()

        col1, col2 = st.columns(2, vertical_alignment='center')

        save_changes = col1.button("Save Changes", use_container_width=True)
        popover = col2.popover("Reset Password", use_container_width=True, icon='🔐')

        if save_changes:
            if email and not utils.is_valid_email(email):
                st.session_state['flags']['invalid_email'] = True

            try:
                response = supabase.table("user_authentication").update({
                    "username": username,
                    "email": email,
                }).eq("id", user_id).execute()
                
                st.session_state["flags"]["save_success"] = True

            except APIError as e:
                st.session_state['flags']['user_already_exists'] = True

        with popover:
            with st.form("RST1", border=False):
                old_password = st.text_input("Old Password*", type="password").strip()
                new_password = st.text_input("New Password*", type="password").strip()
                confirm_password = st.text_input("Confirm Password*", type="password").strip()
                if st.form_submit_button("Reset Password", use_container_width=True):
                    # Validate that all required fields are filled.
                    fields_filled = all([email, old_password, new_password, confirm_password])
                    st.session_state['flags']['missing_data'] = not fields_filled
                    
                    db_pass = supabase.table("user_authentication").select("password").eq("id", user_id).execute()
                    if not utils.verify_value(old_password, db_pass.data[0]['password']):
                        st.session_state['flags']['wrong_password'] = True

                    if old_password and len(old_password) < 8:
                        st.session_state['flags']['password_too_short'] = True

                    if new_password and len(new_password) < 8:
                        st.session_state['flags']['password_too_short'] = True
                    
                    if new_password and confirm_password and (new_password != confirm_password):
                        st.session_state['flags']['passwords_do_not_match'] = True

                    flags_to_check = ["invalid_email", "passwords_do_not_match", "password_too_short", "missing_data", "wrong_password"]
                    if all(not st.session_state['flags'][flag] for flag in flags_to_check):
                        # user_response = supabase.table("user_authentication").select("id").eq("email", email).execute()
                        supabase.table("user_authentication").update({"password":utils.hash_value(new_password)}).eq("email", email).execute()
                        st.session_state["flags"]["reset_success"] = True


        error_msg = utils.generate_error_message(st.session_state['flags'])
        if error_msg:
            st.error(error_msg, icon="🚨")
        elif st.session_state['flags']['wrong_password']:
            st.error("Password is incorrect", icon="🚨")
        elif st.session_state["flags"]["reset_success"]:
            st.success("Password reset", icon="✅")
        elif st.session_state["flags"]["save_success"]:
            st.success("Changes saved!", icon="✅")
            sleep(0.5)
            st.rerun()
    
    with st.container(border=True):
        st.write("### Manage Inverters")
        st.write("---")
        table_data = {"Inverters": inverter_ids}
        df = st.dataframe(table_data, use_container_width=True, on_select="rerun")
        
        with st.form(key="MAN", border=False):
            # Layout for Inverter ID and PIN Code.
            col1, col2 = st.columns(2, vertical_alignment="center")
            with col1:
                inverter_id = st.text_input("Inverter ID*", placeholder="inv###", max_chars=6).strip()
            with col2:
                pin_code = st.text_input("PIN Code*", placeholder="####", max_chars=4).strip()

            col3, col4 = st.columns(2, vertical_alignment="center")
            with col3:
                if st.form_submit_button("Add Inverter", use_container_width=True):
                    if inverter_id and pin_code:
                        # Query the Supabase table
                        result = supabase.table("company_inverters").select("inverter_id", "pin_code", "user_id").eq("inverter_id", inverter_id).execute()
                        if result and result.data:
                            # The inverter exists and matches the pin code
                            if utils.verify_value(pin_code, result.data[0]['pin_code']):
                                if result.data[0]['user_id'] == None:
                                    # Update the inverter to link it to the user_id
                                    update_result = supabase.table("company_inverters").update({"user_id": user_id}).eq("inverter_id", inverter_id).execute()
                                    if update_result:
                                        st.session_state["flags"]["link_success"] = True
                                else:
                                    st.session_state['flags']["used_inverter"] = True
                            else:
                                st.session_state['flags']["inverter_wrong_info"] = True
                        else:
                            st.session_state['flags']["inverter_wrong_info"] = True
                    else:
                        st.session_state['flags']["missing_data"] = True

        with col4:
            if st.form_submit_button("Delete Selection", use_container_width=True, type='secondary'):
                if "selection" in df and df["selection"]["rows"]:
                    selected_rows = df["selection"]["rows"]  # Get the selected rows (indexes)
                    selected_inverter_ids = [table_data["Inverters"][row] for row in selected_rows]

                    # Ensure at least one inverter remains
                    total_inverters = len(table_data["Inverters"])  # Total number of inverters
                    if total_inverters - len(selected_inverter_ids) < 1:
                        st.session_state["flags"]["delete_all"] = True
                    else:
                        if selected_inverter_ids:
                            # Perform delete operation in Supabase
                            for inverter_id in selected_inverter_ids:
                                delete_result = supabase.table("company_inverters").update({"user_id": None}).eq("inverter_id", inverter_id).execute()
                                st.rerun()
                    
                    
        error_msg = utils.generate_error_message(st.session_state['flags'])
        if error_msg:
            st.error(error_msg, icon="🚨")
        elif st.session_state["flags"]["link_success"]:
            st.success("Inverter successfully linked to the user", icon="✅")
            sleep(0.5)
            st.rerun()
        elif st.session_state["flags"]["delete_all"]:
            st.error("You must keep at least one inverter", icon="🚨")
        elif st.session_state["flags"]["used_inverter"]:
            st.error("Inverter already in use", icon="🚨")
                            
    with st.container(border=True):
        st.write("### DANGER ZONE")
        st.write("---")
        st.error("""**Request for account deletion**
                
Deleting your account is permanent and cannot be undone.
Your data will be deleted, except we may retain some metadata and logs for longer where required or permitted by law.
                """, icon="🚨")
        
        if st.button("⛔ Delete Account"):
            confirm(supabase, user_id)
    

# ============================================================================
#   Helper Functions
# ============================================================================
@st.dialog("Are you sure you want to delete your account?")
def confirm(supabase, user_id):
    col1, col2 = st.columns(2, vertical_alignment='center')
    with col1:
        if st.button("Proceed", use_container_width=True):
            # 1. Update company_inverters table: Set user_id to null for all rows associated with the user
            update_response = supabase.table("company_inverters")\
                                    .update({"user_id": None})\
                                    .eq("user_id", user_id)\
                                    .execute()
            # 2. Delete user from user_authentication table
            delete_response = supabase.table("user_authentication")\
                                    .delete()\
                                    .eq("id", user_id)\
                                    .execute()
            # 3. Optionally perform further cleanup like logging user out, redirecting, etc.
            js_utils.save_to_storage("sessionStorage", "is_signed", False)
            js_utils.save_to_storage("sessionStorage", "user_email", "")
            js_utils.save_to_storage("localStorage", "access_token", "")
            js_utils.refresh()  # Force a browser-level refresh via JS helper.
            st.rerun()

    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()

def gauge(value=450, title='Speed', delta_reference=380, axis_range=[None, 500], threshold=490):
    # Compute the boundaries based on thirds of the axis rang
    min_val, max_val = axis_range
    range_span = max_val - min_val
    first_third = min_val + range_span / 3
    second_third = min_val + 2 * range_span / 3
        
    fig = go.Figure(go.Indicator(
    domain = {'x': [0, 0.8], 'y': [0, 1]},
    value = value,
    mode = "gauge+number+delta",
    title = {'text': title},
    delta = {'reference': delta_reference},
    gauge = {'axis': {'range': axis_range},
            'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': threshold},
            "bar": {"color": (
                "red" if value <= first_third else
                "yellow" if value <= second_third else
                "green"
            )}
            }))
    return fig