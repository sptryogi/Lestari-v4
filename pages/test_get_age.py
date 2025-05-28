from AI_chatbot import get_age_by_email, get_age_by_id
import streamlit as st

age = get_age_by_id("8782f5db-881c-4461-a4a1-a639d126c5f3")
st.text(age)
