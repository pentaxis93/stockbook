"""
StockBook - Personal Stock Trading Tracker
Main Streamlit application entry point
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from config import config

# Page configuration from centralized config
st.set_page_config(**config.streamlit_config)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    # Add more session state variables as needed

# Main app


def main():
    # Title and header
    st.title("📈 StockBook")
    st.markdown("*Personal Stock Trading Tracker*")

    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Go to",
            ["Dashboard", "Add Trade", "Portfolio", "History", "Settings"]
        )

    # Page routing
    if page == "Dashboard":
        show_dashboard()
    elif page == "Add Trade":
        show_add_trade()
    elif page == "Portfolio":
        show_portfolio()
    elif page == "History":
        show_history()
    elif page == "Settings":
        show_settings()


def show_dashboard():
    st.header("Dashboard")
    st.info("📊 Dashboard coming soon! This will show your portfolio overview.")


def show_add_trade():
    st.header("Add Trade")
    st.info("📝 Trade entry form coming soon!")


def show_portfolio():
    st.header("Portfolio")
    st.info("💼 Portfolio view coming soon!")


def show_history():
    st.header("Trade History")
    st.info("📅 Trade history coming soon!")


def show_settings():
    st.header("Settings")
    st.info("⚙️ Settings page coming soon!")


if __name__ == "__main__":
    main()
