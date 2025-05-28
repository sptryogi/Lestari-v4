from supabase import create_client, Client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your-service-role-key")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def sign_in_with_email(email, password):
    return supabase.auth.sign_in_with_password({"email": email, "password": password})

def get_user_session():
    return supabase.auth.get_session()

def insert_chat_history(user_id, message, response):
    supabase.table("chat_history").insert({
        "user_id": user_id,
        "message": message,
        "response": response
    }).execute()

def fetch_chat_history(user_id):
    result = supabase.table("chat_history").select("*").eq("user_id", user_id).order("created_at", desc=False).execute()
    return result.data if result else []
