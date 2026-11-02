import streamlit as st
from supabase import create_client


def get_supabase_client():
    """Create one Supabase client for each Streamlit user session."""

    if "supabase_client" not in st.session_state:
        supabase_url = st.secrets["SUPABASE_URL"]
        supabase_key = st.secrets["SUPABASE_KEY"]

        st.session_state.supabase_client = create_client(
            supabase_url,
            supabase_key
        )

    return st.session_state.supabase_client