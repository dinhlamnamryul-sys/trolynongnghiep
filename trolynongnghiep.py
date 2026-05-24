import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO
from datetime import datetime
import re
from gtts import gTTS

# =====================
# 1. CẤU HÌNH TRANG TỐI ƯU & ẨN GIAO DIỆN MẶC ĐỊNH
# =====================
st.set_page_config(page_title="Trợ Lý Nông Nghiệp Tây Bắc", page_icon="🌿", layout="centered", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Be Vietnam Pro', sans-serif !important; }
    .stApp { background-color: #f4f7f6; }
    
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .hero-banner {
        background: linear-gradient(135deg, #047857 0%, #10b981 100%);
        border-radius: 20px;
        padding: 40px 20px;
        text-align: center;
        color: white;
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.2);
        margin-bottom: 25px;
        margin-top: -30px;
    }
    .hero-banner h1 { color: white !important; font-weight: 800; font-size: 34px; margin-bottom: 10px; }
    .hero-banner p { font-size: 16px; font-weight: 500; opacity: 0.9; margin: 0; }

    .status-badge-container { display: flex; justify-content: center; margin-bottom: 30px; }
    .status-badge {
        background-color: #d1fae5; color: #06
