import streamlit as st
from PIL import Image

def home():
    st.markdown("<h2 style='text-align: center; color: gray;'>Navigate Your Solar Future</h2>", unsafe_allow_html=True)
    st.write(
        """
        Your smart solution to monitor and control your solar inverters.
        Experience real-time insights, streamlined management, and unmatched control over your renewable energy systems.
        """
    )

    # --------------------------------------------------------------------------------
    # HERO SECTION: Title, Tagline, and Main Visual
    # --------------------------------------------------------------------------------
    # If you have a hero image or banner, display it here.
    try:
        hero_image = Image.open("hero.jpg")  # Replace with path to your banner image.
        st.image(hero_image, use_container_width=True)
    except Exception:
        st.info("Hero image not found. Add 'hero.jpg' in your project directory.")

    # --------------------------------------------------------------------------------
    # BENEFITS SECTION: Why Choose SunPilot?
    # --------------------------------------------------------------------------------
    st.markdown("## Why Choose SolSync?")
    st.markdown(
        """
        - **Real-Time Monitoring:** Stay informed with live data on energy production and system performance.
        - **Intuitive Inverter Management:** Easily add, configure, and control your solar inverters.
        - **Data-Driven Decisions:** Leverage powerful analytics and historical data to optimize your energy use.
        - **Robust Security:** Enjoy peace of mind with industry-level security for all your data.
        """,)

    # --------------------------------------------------------------------------------
    # HOW IT WORKS SECTION: A Simple 3-Step Process
    # --------------------------------------------------------------------------------
    st.markdown("## How It Works")
    st.markdown(
        """
        **1. Sign Up & Connect:**  
        Get started by creating an account and linking your solar inverter with our guided setup.

        **2. Monitor:**  
        Access a rich, real-time dashboard that visualizes both live performance and historical trends.

        **3. Control & Optimize:**  
        Remotely send commands to adjust settings, perform resets, or calibrate your system for peak efficiency.
        """
    )

    # Optionally, include an informative graphic illustrating these steps.
    try:
        workflow_image = Image.open("workflow_diagram.png")  # Replace with a workflow diagram image.
        st.image(workflow_image, caption="A streamlined workflow for harnessing your solar power", width=1000)
    except Exception:
        st.info("Workflow diagram image not found. Consider adding 'workflow_diagram.png'.")

    # --------------------------------------------------------------------------------
    # SUCCESS STORIES SECTION: Testimonials & Social Proof
    # --------------------------------------------------------------------------------
    st.markdown("## Success Stories")
    st.markdown(
        """
        > "SolSync transformed the way I manage my solar system. The interface is seamless and the real-time data is a game changer!"  
        > *– Alex M.*

        > "The analytics provided by SolSync helped me optimize my energy usage and cut down on costs. I can't imagine going back."  
        > *– Jamie T.*
        """
    )

    # --------------------------------------------------------------------------------
    # CALL-TO-ACTION SECTION: Invite Visitors to Take the Next Step
    # --------------------------------------------------------------------------------
    st.markdown("## Ready to Embrace the Future of Energy?")
    st.write(
        """
        At SolSync, we believe every ray of sunlight is an opportunity. With our innovative approach, your solar journey can be as efficient
        and empowering as possible.
        """
    )
    if st.button("Get Started for Free"):
        # This is a placeholder for your sign-up redirection logic
        st.session_state['page'] = 3
        st.rerun()

    # --------------------------------------------------------------------------------
    # FINAL STATEMENT: Vision Statement / Inspiration
    # --------------------------------------------------------------------------------
    st.markdown("### Navigate, Monitor, and Master Your Solar Energy")
    st.write(
        """
        **SolSync** puts you in complete control of your renewable energy portfolio. Embrace smarter energy management
        and join the movement towards a more sustainable future.
        """
    )