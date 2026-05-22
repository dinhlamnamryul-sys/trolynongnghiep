import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO
import json
from datetime import datetime
import re
from gtts import gTTS

# =====================
# 1. CẤU HÌNH TRANG & CSS
# =====================
st.set_page_config(page_title="Trợ Lý Nông Nghiệp Bản Làng", page_icon="🌾", layout="centered")

# CSS tùy chỉnh tối ưu cho di động & bà con nông dân (Chữ to, Nút nổi, Phân vùng rõ ràng)
st.markdown("""
    <style>
    /* Tiêu đề chính */
    .main-title { color: #1b5e20; text-align: center; font-weight: 900; font-size: 32px; margin-bottom: 5px; }
    .sub-title { text-align: center; color: #4caf50; font-size: 16px; font-weight: 500; margin-bottom: 25px; }
    
    /* Hộp cảnh báo mộc mạc */
    .warning-box { background-color: #fff8e1; color: #b71c1c; padding: 15px; border-left: 6px solid #ffca28; border-radius: 8px; margin-bottom: 25px; font-size: 15px; line-height: 1.5; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    
    /* Tiêu đề từng bước */
    .step-header { background-color: #e8f5e9; color: #2e7d32; padding: 12px 15px; border-radius: 8px; font-weight: bold; font-size: 18px; margin-top: 15px; margin-bottom: 15px; border-left: 6px solid #4caf50; }
    
    /* Nút bấm siêu to, dễ ấn trên điện thoại */
    .stButton>button { background-color: #f57c00 !important; color: white !important; border-radius: 12px !important; font-weight: bold !important; font-size: 18px !important; padding: 15px 0 !important; width: 100%; transition: 0.3s; border: none !important; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .stButton>button:hover { background-color: #ef6c00 !important; transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.15); }
    
    /* Nút tải về nhẹ nhàng hơn */
    .download-btn>button { background-color: #0288d1 !important; }
    .download-btn>button:hover { background-color: #0277bd !important; }
    </style>
""", unsafe_allow_html=True)

# Khởi tạo Lịch sử nếu chưa có
if "history" not in st.session_state:
    st.session_state.history = []

# =====================
# 2. CẤU HÌNH API (SIDEBAR)
# =====================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/862/862856.png", width=70)
    st.header("⚙️ Dành cho Cán Bộ/Kỹ thuật")
    st.markdown("Vui lòng nhập API Key để kích hoạt AI.")
    api_key = st.text_input("🔑 Google API Key:", type="password")
    
    with st.expander("👉 Cách lấy API Key (Miễn phí)"):
        st.markdown("""
        1. Vào [Google AI Studio](https://aistudio.google.com/app/apikey)
        2. Đăng nhập Gmail
        3. Nhấn **Create API key**
        4. Copy và dán vào ô trên
        """)
    st.markdown("---")
    st.caption("Ứng dụng vì cộng đồng 🌾")

# =====================
# 3. GIAO DIỆN CHÍNH
# =====================
st.markdown("<div class='main-title'>🌾 Trợ Lý Nông Nghiệp</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Hỏi đáp dịch bệnh (Việt - H’Mông - Thái)</div>", unsafe_allow_html=True)

st.markdown("""
<div class='warning-box'>
    <b>⚠️ Lời dặn bà con:</b><br> 
    Máy tính chỉ đoán bệnh dựa trên ảnh nên có thể chưa đúng 100%. Bà con xem để tham khảo, nếu thấy bệnh lây nhanh chết nhiều thì phải gọi báo ngay cho Trưởng bản hoặc Cán bộ thú y xã nhé!
</div>
""", unsafe_allow_html=True)

# ===============================
# HÀM XỬ LÝ AI (Giữ nguyên logic)
# ===============================
def analyze_real_image(api_key, image, prompt):
    if image.mode == "RGBA":
        image = image.convert("RGB")

    buf = BytesIO()
    image.save(buf, format="JPEG")
    img_b64 = base64.b64encode(buf.getvalue()).decode()

    MODEL = "gemini-2.5-flash"
    URL = f"https://generativelanguage.googleapis.com/v1/models/{MODEL}:generateContent?key={api_key}"

    payload = {
        "contents": [{
            "role": "user",
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}
            ]
        }]
    }

    try:
        res = requests.post(URL, json=payload)
        if res.status_code != 200:
            return f"❌ Lỗi: {res.status_code} - {res.text}"

        data = res.json()
        if "candidates" not in data:
            return "❌ Lỗi: Không nhận được câu trả lời từ AI."

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        return f"❌ Mạng yếu hoặc lỗi kết nối: {str(e)}"

# Hàm tạo âm thanh Text-to-Speech
def generate_audio(text, lang_code):
    try:
        tts = gTTS(text=text, lang=lang_code)
        fp = BytesIO()
        tts.write_to_fp(fp)
        return fp.getvalue()
    except ValueError:
        # Nếu ngôn ngữ không được gTTS hỗ trợ (VD H'Mông đôi khi bị lỗi thư viện), dùng giọng Việt đọc phiên âm làm giải pháp thay thế
        try:
            tts = gTTS(text=text, lang='vi') 
            fp = BytesIO()
            tts.write_to_fp(fp)
            return fp.getvalue()
        except Exception as e:
            return None
    except Exception as e:
        return None

# ===============================
# KHU VỰC THAO TÁC CỦA BÀ CON
# ===============================
# BƯỚC 1: LẤY ẢNH
st.markdown("<div class='step-header'>📸 Bước 1: Cho máy xem ảnh</div>", unsafe_allow_html=True)
with st.container(border=True):
    tab1, tab2 = st.tabs(["📷 Chụp ảnh mới", "🖼️ Chọn ảnh trong máy"])
    
    photo, upload = None, None
    with tab1:
        photo = st.camera_input("Bấm vào đây để chụp:")
    with tab2:
        upload = st.file_uploader("Bấm để chọn ảnh:", type=["png", "jpg", "jpeg"])

    image = None
    if photo:
        image = Image.open(photo)
    elif upload:
        image = Image.open(upload)
        
    if image:
        st.success("✅ Đã nhận được ảnh!")
        with st.expander("👁️ Bấm để xem lại ảnh bà con vừa chọn"):
            st.image(image, use_container_width=True)

# BƯỚC 2: MÔ TẢ & CHỌN NGÔN NGỮ
st.markdown("<div class='step-header'>📝 Bước 2: Kể thêm & Chọn tiếng</div>", unsafe_allow_html=True)
with st.container(border=True):
    extra_info = st.text_area("Cây/con vật bị sao? (Bỏ ăn mấy ngày, héo từ gốc...)", 
                              placeholder="Ví dụ: Gà rù gục đầu 2 ngày nay...",
                              height=80)
    
    st.markdown("**Bà con muốn máy dịch và đọc tiếng gì? (Tiếng Việt luôn có sẵn)**")
    col_lang1, col_lang2 = st.columns(2)
    with col_lang1:
        use_hmong = st.checkbox("🏔️ Tiếng H’Mông", value=True)
    with col_lang2:
        use_thai = st.checkbox("🇹🇭 Tiếng Thái", value=True)

# BƯỚC 3: NÚT BẤM KẾT QUẢ
st.markdown("<div class='step-header'>🚀 Bước 3: Xem kết quả & Nghe âm thanh</div>", unsafe_allow_html=True)

submit_btn = st.button("🔍 TÌM BỆNH & CÁCH CHỮA NGAY")

# ===============================
# XỬ LÝ & HIỂN THỊ KẾT QUẢ
# ===============================
if submit_btn:
    if not image:
        st.error("❌ Bà con nhớ chụp hoặc chọn ảnh ở Bước 1 nhé!")
    elif not api_key:
        st.error("❌ Cán bộ chưa nhập API Key ở thanh bên trái (Menu)!")
    else:
        st.markdown("---")
        with st.spinner("⏳ Máy đang suy nghĩ và chuẩn bị giọng đọc, bà con chờ một chút nhé..."):
            
            langs = ["Việt"]
            if use_hmong: langs.append("H’Mông")
            if use_thai: langs.append("Thái")
            lang_str = " – ".join(langs)
            
            extra_prompt = f"\n- Lời kể của bà con: {extra_info}" if extra_info else ""

            # Bổ sung các Thẻ [VI], [HMN], [TH] để Tách Text phát âm thanh
            prompt_text = fr"""
Bạn là một kỹ sư nông nghiệp và bác sĩ thú y giàu kinh nghiệm, đặc biệt am hiểu thực tế làm nông ở vùng cao.
Hãy quan sát kỹ bức ảnh và chẩn đoán bệnh, đưa ra lời khuyên theo phong cách DỄ HIỂU, GẦN GŨI VỚI BÀ CON NÔNG DÂN bằng ({lang_str}).{extra_prompt}

==============================
⚠️ QUY TẮC AN TOÀN CHẨN ĐOÁN
==============================
- Nếu ảnh KHÔNG RÕ RÀNG hoặc KHÔNG PHẢI cây trồng/vật nuôi: Hãy nói thật là "Ảnh mờ quá, AI không nhìn rõ, bà con chụp lại nhé". TUYỆT ĐỐI KHÔNG đoán bừa.
- Nếu bệnh có nhiều nguyên nhân: Hãy liệt kê các khả năng.
- Luôn có câu chốt khuyên báo cho cán bộ thú y/khuyến nông xã.

==========================
3️⃣ LƯU Ý TRÌNH BÀY (BẮT BUỘC)
==========================
- Sử dụng từ ngữ mộc mạc, ngắn gọn. Tuyệt đối không dùng thuật ngữ học thuật.
- BẮT BUỘC phải chia rõ nội dung theo cấu trúc các thẻ sau để hệ thống cắt lớp âm thanh:
[VI] 
(Chỉ viết Tiếng Việt ở đây)
[HMN] 
(Chỉ viết Tiếng H'Mông ở đây - nếu có yêu cầu)
[TH] 
(Chỉ viết Tiếng Thái ở đây - nếu có yêu cầu)
"""
            result = analyze_real_image(api_key, image, prompt_text)
            
            if result.startswith("❌"):
                st.error(result)
            else:
                st.balloons()
                st.success("📝 MÁY ĐÃ TÌM RA BỆNH! BÀ CON ĐỌC VÀ NGHE BÊN DƯỚI NHÉ:")
                
                # Tách văn bản để đọc âm thanh dựa vào các thẻ [VI], [HMN], [TH]
                vi_match = re.search(r'\[VI\](.*?)(?=\[HMN\]|\[TH\]|$)', result, re.DOTALL)
                hmn_match = re.search(r'\[HMN\](.*?)(?=\[TH\]|$)', result, re.DOTALL)
                th_match = re.search(r'\[TH\](.*?)$', result, re.DOTALL)
                
                vi_text = vi_match.group(1).strip() if vi_match else result
                hmn_text = hmn_match.group(1).strip() if hmn_match else ""
                th_text = th_match.group(1).strip() if th_match else ""

                # Giao diện hiển thị văn bản (Loại bỏ các thẻ [VI], [HMN] cho đẹp mắt)
                display_text = result.replace("[VI]", "🇻🇳 **Tiếng Việt:**\n").replace("[HMN]", "\n---\n🏔️ **Tiếng H'Mông:**\n").replace("[TH]", "\n---\n🇹🇭 **Tiếng Thái:**\n")
                
                with st.container(border=True):
                    st.markdown(display_text)
                
                # KHU VỰC PHÁT ÂM THANH
                st.markdown("<div class='step-header' style='background-color:#e3f2fd; color:#1565c0; border-left-color:#1976d2;'>🔊 Nghe máy đọc kết quả</div>", unsafe_allow_html=True)
                
                # Đọc Tiếng H'Mông
                if use_hmong and hmn_text:
                    st.write("🏔️ **Phát âm Tiếng H'Mông:**")
                    # Dùng mã 'hmn' hoặc fallback
                    audio_hmn = generate_audio(hmn_text, 'hmn')
                    if audio_hmn:
                        st.audio(audio_hmn, format="audio/mp3")
                    else:
                        st.warning("⚠️ Giọng đọc H'Mông hiện đang bảo trì, bà con đọc chữ tạm nhé!")
                
                # Đọc Tiếng Thái
                if use_thai and th_text:
                    st.write("🇹🇭 **Phát âm Tiếng Thái:**")
                    audio_th = generate_audio(th_text, 'th')
                    if audio_th:
                        st.audio(audio_th, format="audio/mp3")
                    else:
                        st.warning("⚠️ Không tải được giọng đọc tiếng Thái lúc này.")

                # Lưu vào lịch sử
                timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
                st.session_state.history.insert(0, {"time": timestamp, "result": display_text, "info": extra_info})
                
                # Nút tải về 
                st.markdown("<div class='download-btn'>", unsafe_allow_html=True)
                st.download_button(
                    label="📥 Lưu kết quả này vào điện thoại",
                    data=display_text,
                    file_name=f"Don_Thuoc_AI_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain"
                )
                st.markdown("</div>", unsafe_allow_html=True)

# ===============================
# LỊCH SỬ KHÁM BỆNH
# ===============================
if st.session_state.history:
    st.markdown("---")
    st.markdown("<div class='step-header' style='background-color:#fff3e0; color:#e65100; border-left-color:#ff9800;'>🕒 Các lần hỏi trước</div>", unsafe_allow_html=True)
    for i, item in enumerate(st.session_state.history[:3]):
        with st.expander(f"📌 Bệnh án lúc: {item['time']}"):
            if item['info']:
                st.caption(f"**Bà con đã kể:** {item['info']}")
            st.markdown(item['result'])
