from AI_chatbot import get_age_by_email, get_age_by_id
import streamlit as st

age = get_age_by_id("fd5a8287-e65e-466a-8ef2-b99ab5808d81")
st.text(age)
