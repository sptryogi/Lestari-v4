from AI_chatbot import get_age_by_email, get_age_by_id
import streamlit as st

age = get_age_by_id("st.session_state["email"]")
st.text(age)
