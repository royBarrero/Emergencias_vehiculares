from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ngryigfpjkumlpersjyi.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5ncnlpZ2Zwamt1bWxwZXJzanlpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3Njk5NTgwNSwiZXhwIjoyMDkyNTcxODA1fQ.NBh1ZuTeIZByl3pQhYsRmBF2UZg_q82iSzRdzHm8Bp4")
SUPABASE_BUCKET = "evidencias"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyC_Sr7VNMnHc-LNPeev2epLcRZ9EKrd9kY")