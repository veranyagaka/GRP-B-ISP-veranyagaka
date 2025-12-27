# srcnn_project/srcnn_project/supabase_client.py
import os
from supabase import create_client

# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")


SUPABASE_URL = "https://dxensuybapndxcbzpjnn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR4ZW5zdXliYXBuZHhjYnpwam5uIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg1MDgwMDksImV4cCI6MjA3NDA4NDAwOX0.5StkBPhTBaoc22m77LiwmM7NqZvsd8bvXygltkZSVgs"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
