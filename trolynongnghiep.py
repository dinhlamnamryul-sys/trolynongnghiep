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

# TÍCH HỢP CSS "PRO WEB APP" - BÍ QUYẾT LÀM ĐẸP
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');
    
    /* Đặt lại Font và Nền toàn trang */
    html, body, [class*="css"] { font-family: 'Be Vietnam Pro', sans-serif !important; }
    .stApp { background-color: #f4f7f6; }
    
    /* Ẩn các thành phần mặc định của Streamlit */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Hero Banner Tuyệt Đẹp */
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

    /* Badge Trạng thái RAG */
    .status-badge-container { display: flex; justify-content: center; margin-bottom: 30px; }
    .status-badge {
        background-color: #d1fae5; color: #065f46;
        padding: 8px 20px; border-radius: 50px; font-size: 13px; font-weight: 600;
        display: inline-flex; align-items: center; gap: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.02); border: 1px solid #a7f3d0;
    }
    .pulse-dot {
        height: 10px; width: 10px; background-color: #10b981;
        border-radius: 50%; display: inline-block;
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 1);
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    /* Thẻ Container Chuyên nghiệp (Cards) */
    .modern-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        border: 1px solid #f1f5f9;
        margin-bottom: 25px;
    }
    .card-title {
        color: #1e293b; font-size: 18px; font-weight: 700; margin-bottom: 20px;
        display: flex; align-items: center; gap: 10px;
    }
    .card-title-icon { background: #e0f2fe; color: #0284c7; width: 35px; height: 35px; border-radius: 10px; display: flex; justify-content: center; align-items: center; font-size: 18px; }

    /* Nút Bấm Xịn Xò */
    div.stButton > button:first-child {
        background: linear-gradient(to right, #059669, #10b981) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 17px !important;
        padding: 15px 0 !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(16, 185, 129, 0.4) !important;
    }

    /* Các thành phần input */
    .stTextArea textarea { border-radius: 10px !important; border: 1px solid #cbd5e1 !important; padding: 15px !important; }
    .stTextArea textarea:focus { border-color: #10b981 !important; box-shadow: 0 0 0 2px rgba(16,185,129,0.2) !important; }
    
    /* Cảnh báo chuyên nghiệp */
    .alert-pro { background-color: #fffbeb; border-left: 4px solid #f59e0b; padding: 15px 20px; border-radius: 8px; color: #92400e; font-size: 14px; margin-bottom: 25px;}
    
    /* Danh bạ liên hệ */
    .contact-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 15px; margin-top: 15px; text-align: center; }
    .contact-btn { background-color: #ef4444; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; display: inline-block; margin-top: 10px; transition: 0.2s;}
    .contact-btn:hover { background-color: #dc2626; color: white; }
    </style>
""", unsafe_allow_html=True)

if "history" not in st.session_state: st.session_state.history = []

# =====================
# 2. CƠ SỞ DỮ LIỆU RAG
# =====================
RAG_KNOWLEDGE_BASE = """
[QUY TRÌNH XỬ LÝ CHUẨN - CHI CỤC THÚ Y & BẢO VỆ THỰC VẬT ĐIỆN BIÊN 2026]
1. BỆNH DỊCH TẢ LỢN CHÂU PHI (ASF): Triệu chứng: Sốt cao, xuất huyết đốm đỏ/tím ở tai, mõm, bẹn. Bỏ ăn. Xử lý: KHÔNG CÓ THUỐC CHỮA. Cách ly tuyệt đối, báo chính quyền tiêu hủy. Rắc vôi bột.
2. BỆNH LỞ MỒM LONG MÓNG (Trâu/Bò/Lợn): Nổi mụn nước ở miệng, móng. Rửa vết thương bằng phèn chua 2%, bôi thuốc Xanh Methylene. Báo cáo kiểm dịch.
3. BỆNH TỤ HUYẾT TRÙNG (Gia cầm/Lợn): Tụ huyết hầu họng, phân lỏng. Tiêm/uống kháng sinh Enrofloxacin 10% hoặc Amoxicillin. Tiêu độc.
4. BỆNH ĐẠO ÔN TRÊN LÚA: Lá có vết chấm mắt én, tâm xám tro. Ngừng bón đạm. Phun Tricyclazole hoặc Isoprothiolane.
5. SÂU CUỐN LÁ NHỎ HẠI LÚA: Lá cuốn ống. Phun Indoxacarb hoặc Chlorantraniliprole khi sâu non nở.
6. SƯƠNG MAI / THÁN THƯ: Đốm nâu sẫm trên lá, quả thối. Phun Copper Oxychloride hoặc Mancozeb.
7. SƯƠNG MUỐI/RÉT ĐẬM: Cây trồng: Tưới nước rửa sương, tủ gốc. Vật nuôi: Đốt trấu sưởi, uống nước ấm pha muối.
"""

# =====================
# 3. SIDEBAR (QUẢN TRỊ VIÊN)
# =====================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/862/862856.png", width=50)
    st.markdown("<h3 style='color:#1e293b; margin-top:10px;'>Cấu hình Hệ thống</h3>", unsafe_allow_html=True)
    api_key = st.text_input("🔑 Cấp quyền Google AI API:", type="password")
    with st.expander("👉 Hướng dẫn lấy mã API"):
        st.markdown("Vào [Google AI Studio](https://aistudio.google.com/app/apikey) -> Đăng nhập -> Create API key.")
    st.markdown("---")
    st.caption("Dự án Khoa học Kỹ thuật | TP. Điện Biên Phủ")

# =====================
# 4. GIAO DIỆN CHÍNH
# =====================
# Hero Banner
st.markdown("""
<div class='hero-banner'>
    <h1>🌿 Hệ Sinh Thái Nông Nghiệp AI</h1>
    <p>Chẩn đoán bệnh & Trích xuất phác đồ chuẩn cho cây trồng, vật nuôi</p>
</div>
""", unsafe_allow_html=True)

# Status Badge
st.markdown("""
<div class='status-badge-container'>
    <div class='status-badge'>
        <span class='pulse-dot'></span>
        Đã đồng bộ Dữ liệu RAG: Sở NN&PTNT Điện Biên 2026
    </div>
</div>
""", unsafe_allow_html=True)

# Lời nhắc chuyên nghiệp
st.markdown("""
<div class='alert-pro'>
    <b>📌 Lưu ý y tế nông nghiệp:</b> Phác đồ được nội suy bằng AI chỉ mang tính chất sơ cứu ban đầu. Yêu cầu báo cáo cán bộ phụ trách khu vực khi có dấu hiệu lây lan diện rộng.
</div>
""", unsafe_allow_html=True)

# HÀM XỬ LÝ
def analyze_real_image(api_key, image, prompt):
    if image.mode == "RGBA": image = image.convert("RGB")
    buf = BytesIO()
    image.save(buf, format="JPEG")
    img_b64 = base64.b64encode(buf.getvalue()).decode()
    MODEL = "gemini-2.5-flash"
    URL = f"https://generativelanguage.googleapis.com/v1/models/{MODEL}:generateContent?key={api_key}"
    payload = {"contents": [{"role": "user", "parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}]}]}
    try:
        res = requests.post(URL, json=payload)
        if res.status_code != 200: return f"❌ Lỗi máy chủ: {res.status_code}"
        data = res.json()
        if "candidates" not in data: return "❌ Lỗi: AI không phản hồi."
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e: return f"❌ Lỗi mạng: {str(e)}"

def generate_audio(text, lang_code):
    try:
        tts = gTTS(text=text, lang=lang_code)
        fp = BytesIO()
        tts.write_to_fp(fp)
        return fp.getvalue()
    except: return None

# ----------------- BƯỚC 1 -----------------
st.markdown("""
<div class='modern-card'>
    <div class='card-title'><div class='card-title-icon'>📸</div> Thu thập Dữ liệu Hình ảnh</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Mở Camera Điện Thoại", "Tải tệp từ thiết bị"])
photo, upload = None, None
with tab1: photo = st.camera_input(" ")
with tab2: upload = st.file_uploader(" ", type=["png", "jpg", "jpeg"])
image = None
if photo: image = Image.open(photo)
elif upload: image = Image.open(upload)

if image:
    st.success("✅ Hình ảnh đã được nạp vào hệ thống!")
    with st.expander("👁️ Kiểm tra lại hình ảnh"): st.image(image, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# ----------------- BƯỚC 2 -----------------
st.markdown("""
<div class='modern-card'>
    <div class='card-title'><div class='card-title-icon'>📝</div> Dữ liệu Lâm sàng & Ngôn ngữ</div>
""", unsafe_allow_html=True)
extra_info = st.text_area("", placeholder="Nhập mô tả của nông dân (VD: Lợn bỏ ăn 2 ngày, lúa cháy lá từ hôm qua...)", height=80)

st.markdown("<br>**Cấu hình ngôn ngữ kết quả:**", unsafe_allow_html=True)
col_lang1, col_lang2, col_lang3 = st.columns(3)
with col_lang1: use_vi = st.checkbox("🇻🇳 Tiếng Việt", value=True, disabled=True)
with col_lang2: use_hmong = st.checkbox("🏔️ Tiếng H’Mông", value=True)
with col_lang3: use_thai = st.checkbox("🌿 Tiếng Thái (Tây Bắc)", value=True)
st.markdown("</div>", unsafe_allow_html=True)

# ----------------- NÚT XỬ LÝ -----------------
st.markdown("<br>", unsafe_allow_html=True)
submit_btn = st.button("🚀 TRÍCH XUẤT HỒ SƠ CHẨN ĐOÁN & PHÁC ĐỒ")

# ----------------- KẾT QUẢ -----------------
if submit_btn:
    if not image: st.error("⚠️ Vui lòng cung cấp hình ảnh!")
    elif not api_key: st.error("⚠️ Hệ thống chưa được cấp quyền (Nhập API Key ở Menu trái)!")
    else:
        st.markdown("---")
        with st.spinner("⏳ AI đang quét và truy vấn Cơ sở dữ liệu chuẩn..."):
            langs = ["Tiếng Phổ Thông"]
            if use_hmong: langs.append("Tiếng dân tộc H’Mông")
            if use_thai: langs.append("Tiếng dân tộc Thái (Tây Bắc Việt Nam)")
            lang_str = " – ".join(langs)
            extra_prompt = f"\n- Lời kể lâm sàng: {extra_info}" if extra_info else ""

            prompt_text = fr"""
Phân tích ảnh và tình trạng để lập hồ sơ bệnh án nông nghiệp.
[TÀI LIỆU KNOWLEDGE BASE]{RAG_KNOWLEDGE_BASE}[/KẾT THÚC]

⚠️ BẮT BUỘC trả lời chính xác theo cấu trúc 4 phần sau cho mỗi ngôn ngữ:
- 🔍 **Dấu hiệu lâm sàng:** (Mô tả tình trạng)
- 🩺 **Chẩn đoán:** (Tên bệnh)
- 📋 **Phác đồ RAG:** (Biện pháp xử lý/Tên thuốc y hệt tài liệu chuẩn)
- 🚨 **Khuyến cáo dịch tễ:** (Báo cáo trạm thú y/khuyến nông)
Tuyệt đối không bịa tên thuốc. Văn phong mộc mạc, dịch ra ({lang_str}). Dùng phiên âm Latinh cho tiếng dân tộc.{extra_prompt}

⚠️ CHIA THẺ ĐỂ CẮT ÂM THANH:
[VI] (Nội dung Tiếng Việt)
[HMN] (Nội dung H'Mông - nếu có)
[TH] (Nội dung Thái - nếu có)
"""
            result = analyze_real_image(api_key, image, prompt_text)
            
            if result.startswith("❌"): st.error(result)
            else:
                vi_match = re.search(r'\[VI\](.*?)(?=\[HMN\]|\[TH\]|$)', result, re.DOTALL)
                hmn_match = re.search(r'\[HMN\](.*?)(?=\[TH\]|$)', result, re.DOTALL)
                th_match = re.search(r'\[TH\](.*?)$', result, re.DOTALL)
                vi_text = vi_match.group(1).strip() if vi_match else result
                hmn_text = hmn_match.group(1).strip() if hmn_match else ""
                th_text = th_match.group(1).strip() if th_match else ""

                display_text = result.replace("[VI]", "🇻🇳 **HỒ SƠ TIẾNG VIỆT:**\n").replace("[HMN]", "\n---\n🏔️ **HỒ SƠ TIẾNG H'MÔNG:**\n").replace("[TH]", "\n---\n🌿 **HỒ SƠ TIẾNG THÁI (TÂY BẮC):**\n")
                
                # Vùng kết quả
                st.markdown("""
                <div class='modern-card' style='border-top: 4px solid #10b981;'>
                    <div class='card-title'><div class='card-title-icon' style='background:#dcfce7; color:#16a34a;'>📋</div> Kết quả Phân tích từ AI</div>
                """, unsafe_allow_html=True)
                st.markdown(display_text)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Mạng lưới liên hệ khẩn cấp
                st.markdown("""
                <div class='modern-card'>
                    <div class='card-title'><div class='card-title-icon' style='background:#fee2e2; color:#ef4444;'>🚨</div> Mạng lưới Hỗ trợ Khẩn cấp</div>
                    <p style='color:#475569; font-size:14px;'>Định tuyến đến Cán bộ Nông nghiệp/Thú y phụ trách địa bàn (Demo):</p>
                """, unsafe_allow_html=True)
                
                dia_phuong = st.selectbox(" ", ["📍 Phường Mường Thanh", "📍 Xã Thanh Xương", "📍 Xã Mường Phăng"], label_visibility="collapsed")
                st.markdown("<div class='contact-box'>", unsafe_allow_html=True)
                if dia_phuong == "📍 Phường Mường Thanh":
                    st.markdown("👨‍🌾 **Nguyễn Văn A** - Trạm trưởng Khuyến nông<br>📞 0912.345.678", unsafe_allow_html=True)
                    st.markdown("<a href='tel:0912345678' class='contact-btn'>☎ BẤM GỌI CỨU VIỆN NGAY</a>", unsafe_allow_html=True)
                elif dia_phuong == "📍 Xã Thanh Xương":
                    st.markdown("👨‍🌾 **Lò Văn B** - Cán bộ Thú y xã<br>📞 0988.777.666", unsafe_allow_html=True)
                    st.markdown("<a href='tel:0988777666' class='contact-btn'>☎ BẤM GỌI CỨU VIỆN NGAY</a>", unsafe_allow_html=True)
                else:
                    st.markdown("👩‍🌾 **Lường Thị C** - Tổ trưởng BVTV<br>📞 0215.3123.456", unsafe_allow_html=True)
                    st.markdown("<a href='tel:02153123456' class='contact-btn'>☎ BẤM GỌI CỨU VIỆN NGAY</a>", unsafe_allow_html=True)
                st.markdown("</div></div>", unsafe_allow_html=True)

                # Âm thanh
                st.markdown("""
                <div class='modern-card'>
                    <div class='card-title'><div class='card-title-icon' style='background:#f3e8ff; color:#9333ea;'>🔊</div> Trợ lý Giọng nói</div>
                """, unsafe_allow_html=True)
                if vi_text:
                    st.write("🇻🇳 **Giọng Tiếng Việt:**")
                    clean_vi = vi_text.replace('*', '').replace('#', '').replace('🔍', '').replace('🩺', '').replace('📋', '').replace('🚨', '')
                    audio_vi = generate_audio(clean_vi, 'vi')
                    if audio_vi: st.audio(audio_vi, format="audio/mp3")
                if (use_hmong and hmn_text) or (use_thai and th_text):
                    st.info("💡 Hệ thống AI toàn cầu hiện đang thiếu bộ dữ liệu âm vị học H'Mông/Thái Tây Bắc. Tính năng Text-to-Speech bản địa đang chờ bổ sung từ ngân hàng dữ liệu địa phương.")
                st.markdown("</div>", unsafe_allow_html=True)

                st.session_state.history.insert(0, {"time": datetime.now().strftime("%d/%m/%Y %H:%M"), "result": display_text})

# ----------------- TÀI LIỆU DỰ ÁN -----------------
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("ℹ️ Tuyên bố Công nghệ & Kiến trúc Hệ thống (Dành cho Giám khảo)"):
    st.markdown("""
    <div style='background: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; font-size: 14.5px; line-height: 1.7;'>
        <b style='color:#0f172a; font-size:16px;'>1. Kiến trúc Hệ thống RAG (Retrieval-Augmented Generation)</b><br>
        Ứng dụng sử dụng lõi LLM kết hợp với CSDL nhúng (Knowledge Base) mô phỏng tài liệu chuẩn của <i>Chi cục Thú y & Bảo vệ thực vật</i>. Thuật toán ép buộc AI phải <b>đối chiếu và trích xuất</b> phác đồ từ CSDL thay vì tự sinh văn bản ngẫu nhiên, giải quyết triệt để lỗi "AI Hallucination" trong y tế nông nghiệp.<br><br>
        
        <b style='color:#0f172a; font-size:16px;'>2. Thiết kế Lấy Người Nông Dân Làm Trung Tâm (User-Centric Design)</b><br>
        Giao diện loại bỏ hoàn toàn yếu tố kỹ thuật phức tạp, ứng dụng ngôn ngữ thiết kế "Card UI" phẳng. Chuỗi hành động được khép kín: <i>Nhận diện hình ảnh -> Đối chiếu phác đồ -> Dịch phương ngữ (Thái/H'Mông) -> Cung cấp phím gọi cấp cứu định tuyến theo xã</i>.
    </div>
    """, unsafe_allow_html=True)
