from supabase import create_client, Client
import streamlit as st

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def sign_in_with_email(email, password):
    return supabase.auth.sign_in_with_password({"email": email, "password": password})

def sign_up_with_email(email, password, age):
    result = supabase.auth.sign_up({"email": email, "password": password})
    user_id = result.user.id
    supabase.table("profiles").insert({"id": user_id, "age": age}).execute()
    return result

def sign_out():
    supabase.auth.sign_out()

def get_user_session():
    return supabase.auth.get_session()

def insert_chat_history(user_id, room, message, response):
    supabase.table("chat_history").insert({
        "user_id": user_id,
        "room": room,
        "message": message,
        "response": response
    }).execute()

def fetch_chat_history(user_id, room):
    result = supabase.table("chat_history") \
        .select("*") \
        .eq("user_id", user_id) \
        .eq("room", room) \
        .order("created_at", desc=False) \
        .execute()
    return result.data if result else []
