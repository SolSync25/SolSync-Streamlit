import streamlit as st


def side_title():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"]::before {
                content: "Navigation";
                margin-left: 20px;
                margin-top: 20px;
                font-size: 30px;
                position: relative;
                top: 0px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Set the background color of the container
container="""
    <style>
    .st-key-col2 {
        background-color: #ff2b2b;
        text-align: center;
        text-align-last: center;
        padding: 15% 10px;
        border-radius: 5px;
    }
    </style>
    """

# Set the styles for the button
button_light="""
    <style>
    .st-emotion-cache-12h5x7g {
        background-color: #ff2b2b;  /* Background color of the button */
        color: #ffffff;  /* Text color inside the button */
        padding: 10px 10px;  /* Vertical padding 15px, horizontal padding 20px */
        margin: 10px 0;  /* Vertical margin 10px, no horizontal margin */
        border: 2px solid #ffffff;
        border-radius: 5px;
        font-size: 16px;
    }

    .st-emotion-cache-15hul6a:hover {
        background-color: #ffffff;  /* Change background color on hover */
        color: #ff2b2b;
    }

    </style>
    """

# Set the styles for the button
button_dark="""
    <style>
    .st-emotion-cache-15hul6a {
        background-color: #ff2b2b;  /* Background color of the button */
        color: #ffffff;  /* Text color inside the button */
        padding: 10px 10px;  /* Vertical padding 15px, horizontal padding 20px */
        margin: 10px 0;  /* Vertical margin 10px, no horizontal margin */
        border: 2px solid #ffffff;
        border-radius: 5px;
        font-size: 16px;
    }

    .st-emotion-cache-15hul6a:hover {
        background-color: #ffffff;  /* Change background color on hover */
        color: #ff2b2b;
    }

    </style>
    """