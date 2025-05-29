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

def create_chat_room(user_id, room_name):
    # Tidak perlu insert ke tabel baru, cukup gunakan nama di chat_history
    return room_name

def get_user_chat_rooms(user_id):
    result = supabase.table("chat_history") \
        .select("room") \
        .eq("user_id", user_id) \
        .execute()
    if result.data:
        rooms = list(set([r["room"] for r in result.data]))
        return sorted(rooms)
    return []

def delete_chat_room(user_id, room_name):
    supabase.table("chat_history") \
        .delete() \
        .eq("user_id", user_id) \
        .eq("room", room_name) \
        .execute()

def delete_message_by_id(message_id):
    supabase.table("chat_history") \
        .delete() \
        .eq("id", message_id) \
        .execute()

def edit_message_by_id(message_id, new_message):
    supabase.table("chat_history") \
        .update({"message": new_message}) \
        .eq("id", message_id) \
        .execute()
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
