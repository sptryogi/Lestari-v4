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

def insert_chat_message(user_id: str, message: str, response: str, room: str = "default"):
    """Insert a new chat message into the database"""
    return supabase.table("chat_history").insert({
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "message": message,
        "response": response,
        "room": room
    }).execute()

def get_chat_history(user_id: str, room: str = "default", limit: int = 50):
    """Retrieve chat history for a user in a specific room"""
    return supabase.table("chat_history") \
        .select("*") \
        .eq("user_id", user_id) \
        .eq("room", room) \
        .order("created_at", desc=False) \
        .limit(limit) \
        .execute()

def delete_chat_message(message_id: str):
    """Delete a chat message by ID"""
    return supabase.table("chat_history") \
        .delete() \
        .eq("id", message_id) \
        .execute()

def update_chat_message(message_id: str, new_message: str):
    """Update a chat message"""
    return supabase.table("chat_history") \
        .update({"message": new_message}) \
        .eq("id", message_id) \
        .execute()
