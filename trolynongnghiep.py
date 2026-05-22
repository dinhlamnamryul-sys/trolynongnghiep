import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO
from datetime import datetime
import re
from gtts import gTTS

# =====================
# 1. CẤU HÌNH TRANG TỐI ƯU
# =====================
st.set_page_config(page_title="Trợ Lý Nông Nghiệp", page_icon="🌱", layout="centered", initial_sidebar_state="collapsed")

# TÍCH HỢP CSS NÂNG CAO (GIAO DIỆN CHUYÊN NGHIỆP)
st.markdown("""
    <style>
    /* Nhúng Font Be Vietnam Pro cực đẹp */
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Be Vietnam Pro', sans-serif !important;
    }

    /* Tiêu đề chính dạng App */
    .app-header {
        background: linear-gradient(135deg, #2e7d32 0%, #4caf50 100%);
        padding: 25px 15px;
        border-radius: 16px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(46, 125, 50, 0.3);
        margin-bottom: 25px;
    }
    .app-header h1 { color: white !important; font-weight: 800; font-size: 30px; margin: 0; padding: 0; line-height: 1.2; }
    .app-header p { font-size: 16px; font-weight: 500; opacity: 0.9; margin-top: 5px; margin-bottom: 0; }

    /* Lời dặn / Cảnh báo */
    .note-box {
        background-color: #fff9e6;
        border: 1px solid #ffe082;
        border-left: 6px solid #ffb300;
        padding: 18px;
        border-radius: 12px;
        color: #5c4000;
        font-size: 15px;
        line-height: 1.6;
        margin-bottom: 25px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }

    /* Các khung bước (Cards) */
    .step-card {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }
    
    .step-title {
        color: #1b5e20;
        font-weight: 700;
        font-size: 19px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
        border-bottom: 2px solid #f1f8e9;
        padding-bottom: 10px;
    }

    /* Nút bấm siêu nổi bật */
    .stButton>button {
        background: linear-gradient(to right, #f57c00, #ff9800) !important;
        color: white !important;
        border-radius: 50px !important; /* Bo tròn hoàn toàn */
        font-weight: 700 !important;
        font-size: 18px !important;
        padding: 12px 0 !important;
        border: none !important;
        box-shadow: 0 6px 15px rgba(245, 124, 0, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 20px rgba(245, 124, 0, 0.4) !important;
    }

    /* Nút tải về khác màu */
    .download-btn>button {
        background: linear-gradient(to right, #0277bd, #039be5) !important;
        box-shadow: 0 6px 15px rgba(2, 119, 189, 0.3) !important;
    }

    /* Text Area & Input to rõ */
    .stTextArea textarea { font-size: 16px !important; border-radius: 10px !important; }
    
    </style>
""", unsafe_allow_html=True)

# Khởi tạo Lịch sử
if "history" not in st.session_state:
    st.session_state.history = []

# =====================
# 2. MENU CÀI ĐẶT ẨN (SIDEBAR)
# =====================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/862/862856.png", width=60)
    st.markdown("### ⚙️ Cài đặt Quản trị")
    st.caption("Dành riêng cho ban tổ chức/kỹ thuật viên nhập API Key của Google.")
    api_key = st.text_input("🔑 Google API Key:", type="password")
    st.markdown("---")
    st.markdown("Dự án Khoa học Kỹ thuật 2026<br>Mục tiêu: Chuyển đổi số Nông nghiệp vùng cao.", unsafe_allow_html=True)

# =====================
# 3. HEADER ỨNG DỤNG
# =====================
st.markdown("""
<div class='app-header'>
    <h1>🌱 Trợ Lý Nông Nghiệp</h1>
    <p>Chẩn đoán bệnh cây trồng, vật nuôi bằng AI</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='note-box'>
    <b>👋 Lời ngỏ:</b> Ứng dụng hỗ trợ bà con tìm hiểu nhanh các loại bệnh nông nghiệp, có hỗ trợ đọc tiếng Thái và H'Mông. Lưu ý: Kết quả mang tính tham khảo, bà con cần theo dõi thực tế và báo cho cán bộ Khuyến nông/Thú y nếu bệnh nặng.
</div>
""", unsafe_allow_html=True)

# ===============================
# HÀM XỬ LÝ (Giữ nguyên logic cực chuẩn của bạn)
# ===============================
def analyze_real_image(api_key, image, prompt):
    if image.mode == "RGBA": image = image.convert("RGB")
    buf = BytesIO()
    image.save(buf, format="JPEG")
    img_b64 = base64.b64encode(buf.getvalue()).decode()

    MODEL = "gemini-2.5-flash"
    URL = f"https://generativelanguage.googleapis.com/v1/models/{MODEL}:generateContent?key={api_key}"

    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}]}]
    }
    try:
        res = requests.post(URL, json=payload)
        if res.status_code != 200: return f"❌ Lỗi: {res.status_code} - {res.text}"
        data = res.json()
        if "candidates" not in data: return "❌ Lỗi: Không nhận được câu trả lời từ AI."
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e: return f"❌ Mạng yếu hoặc lỗi kết nối: {str(e)}"

def generate_audio(text, lang_code):
    try:
        tts = gTTS(text=text, lang=lang_code)
        fp = BytesIO()
        tts.write_to_fp(fp)
        return fp.getvalue()
    except:
        try:
            tts = gTTS(text=text, lang='vi') 
            fp = BytesIO()
            tts.write_to_fp(fp)
            return fp.getvalue()
        except: return None

# ===============================
# KHU VỰC THAO TÁC CỦA BÀ CON (GIAO DIỆN MỚI)
# ===============================

# BƯỚC 1: HÌNH ẢNH
st.markdown("<div class='step-title'>📸 Bước 1: Cung cấp hình ảnh</div>", unsafe_allow_html=True)
st.markdown("<div class='step-card'>", unsafe_allow_html=True)
tab1, tab2 = st.tabs(["📷 Chụp ảnh trực tiếp", "🖼️ Tải ảnh từ thư viện"])
photo, upload = None, None
with tab1: photo = st.camera_input("Bấm vào đây để mở Camera:")
with tab2: upload = st.file_uploader("Bấm để chọn ảnh có sẵn:", type=["png", "jpg", "jpeg"])

image = None
if photo: image = Image.open(photo)
elif upload: image = Image.open(upload)

if image:
    st.success("✅ Ảnh đã được tải lên thành công!")
    with st.expander("👁️ Xem trước hình ảnh"):
        st.image(image, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)


# BƯỚC 2: THÔNG TIN & NGÔN NGỮ
st.markdown("<div class='step-title'>📝 Bước 2: Thông tin & Ngôn ngữ</div>", unsafe_allow_html=True)
st.markdown("<div class='step-card'>", unsafe_allow_html=True)
extra_info = st.text_area("Bà con mô tả thêm tình trạng (nếu có):", 
                          placeholder="Ví dụ: Gà ủ rũ 2 ngày, phân trắng... hoặc lúa bị vàng lá từ hôm qua...",
                          height=80)

st.markdown("**Chọn ngôn ngữ muốn máy đọc và dịch:** (Tiếng Việt luôn có sẵn)")
col_lang1, col_lang2 = st.columns(2)
with col_lang1: use_hmong = st.checkbox("🏔️ Tiếng H’Mông", value=True)
with col_lang2: use_thai = st.checkbox("🇹🇭 Tiếng Thái", value=True)
st.markdown("</div>", unsafe_allow_html=True)


# BƯỚC 3: NÚT XỬ LÝ
st.markdown("<br>", unsafe_allow_html=True)
submit_btn = st.button("🚀 BẮT ĐẦU CHẨN ĐOÁN NGAY")

# ===============================
# XỬ LÝ KẾT QUẢ & ÂM THANH
# ===============================
if submit_btn:
    if not image:
        st.error("⚠️ Vui lòng chụp hoặc tải ảnh lên ở Bước 1!")
    elif not api_key:
        st.error("⚠️ Ban giám khảo/Kỹ thuật viên vui lòng nhập API Key ở Menu bên trái để chạy thử nghiệm!")
    else:
        st.markdown("---")
        with st.spinner("⏳ Hệ thống AI đang phân tích hình ảnh và chuẩn bị giọng đọc. Vui lòng chờ vài giây..."):
            
            langs = ["Việt"]
            if use_hmong: langs.append("H’Mông")
            if use_thai: langs.append("Thái")
            lang_str = " – ".join(langs)
            extra_prompt = f"\n- Lời kể của bà con: {extra_info}" if extra_info else ""

            prompt_text = fr"""
Bạn là chuyên gia nông nghiệp và bác sĩ thú y vùng cao. Hãy quan sát ảnh và chẩn đoán bệnh, khuyên DỄ HIỂU bằng ({lang_str}).{extra_prompt}

⚠️ QUY TẮC:
- Nếu ảnh mờ/không đúng: Báo "Ảnh không rõ, vui lòng chụp lại". Không đoán bừa.
- Luôn khuyên báo cán bộ xã.
- Không dùng từ hàn lâm. BẮT BUỘC chia rõ các thẻ:
[VI] 
(Nội dung tiếng Việt)
[HMN] 
(Nội dung H'Mông - nếu có)
[TH] 
(Nội dung Thái - nếu có)
"""
            result = analyze_real_image(api_key, image, prompt_text)
            
            if result.startswith("❌"):
                st.error(result)
            else:
                st.balloons()
                st.success("🎉 PHÂN TÍCH THÀNH CÔNG! MỜI BÀ CON XEM KẾT QUẢ:")
                
                # Cắt văn bản
                vi_match = re.search(r'\[VI\](.*?)(?=\[HMN\]|\[TH\]|$)', result, re.DOTALL)
                hmn_match = re.search(r'\[HMN\](.*?)(?=\[TH\]|$)', result, re.DOTALL)
                th_match = re.search(r'\[TH\](.*?)$', result, re.DOTALL)
                
                vi_text = vi_match.group(1).strip() if vi_match else result
                hmn_text = hmn_match.group(1).strip() if hmn_match else ""
                th_text = th_match.group(1).strip() if th_match else ""

                display_text = result.replace("[VI]", "🇻🇳 **Tiếng Việt:**\n").replace("[HMN]", "\n---\n🏔️ **Tiếng H'Mông:**\n").replace("[TH]", "\n---\n🇹🇭 **Tiếng Thái:**\n")
                
                # In kết quả
                st.markdown("<div class='step-card' style='border-top: 4px solid #4caf50;'>", unsafe_allow_html=True)
                st.markdown(display_text)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Phát âm thanh
                st.markdown("<div class='step-title'>🔊 Nghe máy đọc kết quả</div>", unsafe_allow_html=True)
                st.markdown("<div class='step-card'>", unsafe_allow_html=True)
                if use_hmong and hmn_text:
                    st.write("🏔️ **Giọng H'Mông:**")
                    audio_hmn = generate_audio(hmn_text, 'hmn')
                    if audio_hmn: st.audio(audio_hmn, format="audio/mp3")
                
                if use_thai and th_text:
                    st.write("🇹🇭 **Giọng Thái:**")
                    audio_th = generate_audio(th_text, 'th')
                    if audio_th: st.audio(audio_th, format="audio/mp3")
                st.markdown("</div>", unsafe_allow_html=True)

                # Lưu lịch sử
                st.session_state.history.insert(0, {"time": datetime.now().strftime("%d/%m/%Y %H:%M"), "result": display_text})
                
                # Nút tải
                st.markdown("<div class='download-btn'>", unsafe_allow_html=True)
                st.download_button("📥 Tải bản chẩn đoán này về máy", display_text, f"DonThuoc_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
                st.markdown("</div>", unsafe_allow_html=True)

# ===============================
# LỊCH SỬ BÊN DƯỚI
# ===============================
if st.session_state.history:
    st.markdown("<br><div class='step-title' style='color:#f57c00; border-bottom: 2px solid #ffe0b2;'>🕒 Lịch sử khám bệnh hôm nay</div>", unsafe_allow_html=True)
    for item in st.session_state.history[:3]:
        with st.expander(f"📌 Chẩn đoán lúc: {item['time']}"):
            st.markdown(item['result'])
