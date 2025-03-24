import streamlit as st
from PIL import Image
import os

def pricing():
    # --------------------------------------------------------------------------------
    # HEADER & INTRODUCTION
    # --------------------------------------------------------------------------------
    st.markdown("<h2 style='text-align: center; color: gray;'>Transparent Pricing Plans</h2>", unsafe_allow_html=True)
    st.write(
        """
        At SolSync, we believe in making solar energy accessible to everyone.
        Our pricing plans are designed with flexibility and simplicity in mind,
        ensuring that whether you’re just starting out or ramping up your solar enterprise,
        you'll find a solution that fits your needs.
        """
    )

    # --------------------------------------------------------------------------------
    # HERO IMAGE FOR PRICING (if available)
    # --------------------------------------------------------------------------------
    try:
        if os.path.exists(r"/mount/src/solsync-streamlit/images/pricing_banner.jpg"):
            image_path = r"/mount/src/solsync-streamlit/images/pricing_banner.jpg"
        else:
            current_directory = os.getcwd()
            image_path = os.path.join(current_directory, "images", "pricing_banner.jpg")
        st.image(Image.open(image_path))
    except Exception:
        st.info("Pricing banner image not found. Add 'pricing_banner.jpg' in your images directory.")

    # --------------------------------------------------------------------------------
    # PRICING TABLE & DETAILS
    # --------------------------------------------------------------------------------
    st.markdown("## Choose a Plan That Suits You")
    st.markdown(
        """
        | **Plan**      | **Monthly Price** | **Features**                                                                                 |
        |---------------|-------------------|----------------------------------------------------------------------------------------------|
        | **Starter**   | $0                | Basic solar monitoring, limited inverter controls, community support                         |
        | **Pro**       | Coming Soon       | Advanced analytics, full inverter control, priority support, real-time alerts                  |
        | **Enterprise**| Custom Pricing    | Dedicated account management, bespoke integrations, enhanced security features                 |
        """
    )

    st.markdown("### Why Our Plans Stand Out")
    st.write(
        """
        Every plan comes with the reliability and precision you expect from SolSync. Our commitment
        is to support your journey to a smarter, sustainable future. Whether it's your first step into
        solar energy or you're looking for scalable solutions, our pricing is transparent and designed
        with you in mind.
        """
    )

    # --------------------------------------------------------------------------------
    # FINAL CALL-TO-ACTION
    # --------------------------------------------------------------------------------
    if st.button("Get Started for Free"):
        # This is a placeholder for your sign-up redirection logic
        st.session_state['page'] = 3
        st.rerun()