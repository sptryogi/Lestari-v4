from AI_chatbot import get_age_by_email
import streamlit as st

age = get_age_by_email(coba@gmail.com)
st.text(age)
