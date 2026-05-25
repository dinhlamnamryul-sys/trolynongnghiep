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
st.set_page_config(page_title="Trợ Lý Nông Nghiệp Tây Bắc", page_icon="🌿", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Be Vietnam Pro', sans-serif !important; }
    .stApp { background-color: #f4f7f6; }
    
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Cấu hình chuẩn trên Máy tính (Desktop) */
    .hero-banner {
        background: linear-gradient(135deg, #047857 0%, #10b981 100%);
        border-radius: 20px;
        padding: 30px 20px;
        text-align: center;
        color: white;
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.2);
        margin-bottom: 20px;
        margin-top: -40px;
    }
    .hero-banner h1 { color: white !important; font-weight: 800; font-size: 30px; margin-bottom: 5px; }
    .hero-banner p { font-size: 15px; font-weight: 500; opacity: 0.9; margin: 0; }

    .status-badge-container { display: flex; justify-content: center; margin-bottom: 20px; }
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

    .modern-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        border: 1px solid #f1f5f9;
        margin-bottom: 20px;
    }
    .card-title {
        color: #1e293b; font-size: 16px; font-weight: 700; margin-bottom: 15px;
        display: flex; align-items: center; gap: 10px;
    }
    .card-title-icon { background: #e0f2fe; color: #0284c7; width: 30px; height: 30px; border-radius: 8px; display: flex; justify-content: center; align-items: center; font-size: 16px; }

    div.stButton > button:first-child {
        background: linear-gradient(to right, #059669, #10b981) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 12px 0 !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(16, 185, 129, 0.4) !important;
    }

    .stTextArea textarea { border-radius: 10px !important; border: 1px solid #cbd5e1 !important; padding: 12px !important; }
    .stTextArea textarea:focus { border-color: #10b981 !important; box-shadow: 0 0 0 2px rgba(16,185,129,0.2) !important; }
    
    .alert-pro { background-color: #fffbeb; border-left: 4px solid #f59e0b; padding: 12px 15px; border-radius: 8px; color: #92400e; font-size: 13px; margin-bottom: 20px;}
    
    .link-box { background-color: #f8fafc; padding: 10px 12px; border-radius: 8px; color: #0f172a; font-weight: 600; display: flex; align-items: center; gap: 10px; margin-bottom: 8px; transition: 0.2s; border: 1px solid #e2e8f0; font-size: 13px;}
    .link-box:hover { background-color: #f1f5f9; transform: translateX(5px); border-color: #cbd5e1; }
    
    .reference-box { background-color: #f8f9fa; padding: 15px; border-radius: 12px; border-left: 5px solid #0284c7; font-size: 13.5px; line-height: 1.6; color: #334155;}

    /* ==================================================
       💥 CẤU HÌNH ĐẶC BIỆT TỐI ƯU TRÊN ĐIỆN THOẠI (RESPONSIVE)
       ================================================== */
    @media (max-width: 768px) {
        .hero-banner { padding: 15px 10px; margin-top: -20px; margin-bottom: 15px; }
        .hero-banner h1 { font-size: 20px; }
        .hero-banner p { font-size: 12px; }
        .status-badge { padding: 6px 14px; font-size: 11px; }
        .modern-card { padding: 12px; margin-bottom: 12px; border-radius: 12px; }
        .card-title { font-size: 14px; margin-bottom: 10px; }
        .card-title-icon { width: 26px; height: 26px; font-size: 14px; }
        div.stButton > button:first-child { font-size: 14px; padding: 10px 0; border-radius: 10px; }
        .alert-pro { padding: 10px; font-size: 11px; margin-bottom: 15px; }
        .link-box { padding: 8px 10px; font-size: 12px; }
    }
    </style>
""", unsafe_allow_html=True)

if "history" not in st.session_state: st.session_state.history = []

# =====================
# 2. CƠ SỞ DỮ LIỆU RAG NỘI BỘ (SỐ HÓA THỰC TẾ THEO CHUẨN)
# =====================
RAG_KNOWLEDGE_BASE = """
[KNOWLEDGE BASE - TÀI LIỆU SỐ HÓA NỘI BỘ TRÍCH XUẤT TỪ SỞ NN&PTNT ĐIỆN BIÊN]

--- DANH MỤC LÂM SÀNG VÀ PHÁC ĐỒ CHĂN NUÔI ---
1. BỆNH DỊCH TẢ LỢN CHÂU PHI (ASF):
- Lâm sàng: Sốt cao (40.5-42°C), đi đứng loạng choạng, tai mõm và bụng xuất huyết màu đỏ thẫm hoặc tím. Bỏ ăn hoàn toàn, chết nhanh.
- Phác đồ RAG luật định: TUYỆT ĐỐI KHÔNG CÓ THUỐC ĐIỀU TRỊ. Biện pháp duy nhất: Cách ly triệt để khu chuồng nhiễm bệnh, nghiêm cấm mua bán chạy. Báo ngay cán bộ thú y để thực hiện tiêu hủy cơ học bằng chôn sâu, đổ vôi bột. 

2. BỆNH LỞ MỒM LONG MÓNG (Trâu, Bò):
- Lâm sàng: Sốt, xuất hiện vết loét, mụn nước nông ở niêm mạc miệng, kẽ móng chân. Chảy nhiều nước bọt đục. Thú đi khập khiễng.
- Phác đồ RAG luật định: Không có thuốc đặc hiệu trị virus. Sử dụng dung dịch sát trùng hữu cơ bản địa nhẹ rửa sạch vết loét (Axit chanh 2%, nước khế chua hoặc dung dịch phèn chua 2%). Sau đó bôi dung dịch Xanh Methylene 1% hoặc cồn Iodine 10%. Bổ sung Vitamin C.

3. BỆNH TỤ HUYẾT TRÙNG (Gà, Vịt):
- Lâm sàng: Ủ rũ, xù lông, mào và tích tím tái do tụ huyết tuần hoàn. Khó thở dữ dội, đi tiêu lỏng phân xanh hoặc trắng xám.
- Phác đồ RAG luật định: Cách ly. Điều trị khẩn cấp bằng kháng sinh đặc hiệu: Amoxicillin (20mg/kg thể trọng) hoặc Enrofloxacin 10% pha nước uống liên tục 3-5 ngày. Bổ sung điện giải. Phun khử trùng.

--- DANH MỤC LÂM SÀNG VÀ PHÁC ĐỒ TRỒNG TRỌT ---
4. BỆNH ĐẠO ÔN HẠI LÚA:
- Lâm sàng: Phiến lá xuất hiện vết bệnh hình thoi (mắt én), tâm màu xám tro, viền ngoài màu nâu sẫm. Bệnh nặng gây thối cổ bông.
- Phác đồ RAG luật định: LẬP TỨC NGỪNG BÓN PHÂN ĐẠM (URÊ). Giữ nguyên mực nước ruộng 3-5 cm. Sử dụng thuốc hoạt chất Tricyclazole (Beam, Filia) hoặc Isoprothiolane (Fuji-One), phun chiều mát.

5. SÂU CUỐN LÁ NHỎ HẠI LÚA:
- Lâm sàng: Sâu non nhả tơ cuốn dọc lá lúa thành hình ống, ăn lớp mô xanh để lại vệt biểu bì trắng.
- Phác đồ RAG luật định: Phun thuốc nội hấp lưu dẫn như Chlorantraniliprole (Virtako, Prevathon) hoặc Indoxacarb khi sâu non vừa nở.

6. BỆNH SƯƠNG MAI / THÁN THƯ (Rau màu, Cây ăn quả):
- Lâm sàng: Mặt dưới lá xuất hiện lớp nấm trắng xám, mặt trên lá đốm nâu sẫm. Quả non thối nhũn hoặc teo tóp rụng.
- Phác đồ RAG luật định: Tỉa cành thông thoáng. Phun hợp chất gốc Đồng (Copper Oxychloride) hoặc Mancozeb. Không phun khi trời sắp mưa.

7. PHÒNG CHỐNG SƯƠNG MUỐI VÀ RÉT ĐẬM:
- Cây trồng: Phun nước rửa sương sáng sớm, tủ tro bếp, rơm rạ quanh gốc.
- Vật nuôi: Che chắn chuồng trại, đốt trấu sưởi ấm, cho trâu bò uống nước ấm pha muối khoáng 0.9%. Không thả rông khi dưới 12°C.
"""

# =====================
# 3. SIDEBAR (QUẢN TRỊ VIÊN)
# =====================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/862/862856.png", width=40)
    st.markdown("<h4 style='color:#1e293b; margin-top:5px;'>Cấu hình Hệ thống</h4>", unsafe_allow_html=True)
    api_key = st.text_input("🔑 Cấp quyền Google AI API:", type="password")
    with st.expander("👉 Hướng dẫn lấy mã API"):
        st.markdown("Vào [Google AI Studio](https://aistudio.google.com/app/apikey) -> Đăng nhập -> Create API key.")
    st.markdown("---")

# =====================
# 4. HEADER & GIAO DIỆN CHÍNH
# =====================
st.markdown("""
<div class='hero-banner'>
    <h1>🌿 Hệ Sinh Thái Nông Nghiệp AI</h1>
    <p>Chẩn đoán bệnh & Trích xuất phác đồ chuẩn cho cây trồng, vật nuôi</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='status-badge-container'>
    <div class='status-badge'>
        <span class='pulse-dot'></span>
        Hệ thống RAG: Đã đồng bộ Kho dữ liệu Số hóa Thú y & BVTV
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='alert-pro'>
    <b>📌 Lưu ý y tế nông nghiệp:</b> Phác đồ được nội suy dựa trên Cơ sở dữ liệu RAG nội bộ chỉ mang tính chất sơ cứu ban đầu. Yêu cầu báo cáo cán bộ chuyên môn khi có dấu hiệu lây lan.
</div>
""", unsafe_allow_html=True)

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

# TẠO 2 CỘT GIAO DIỆN CHÍNH
col_left, col_right = st.columns([1, 1.2], gap="medium")

with col_left:
    # ----------------- BƯỚC 1 -----------------
    tab1, tab2 = st.tabs(["📸 Mở Camera Điện Thoại", "📁 Tải tệp từ thiết bị"])
    photo, upload = None, None
    with tab1: photo = st.camera_input(" ")
    with tab2: upload = st.file_uploader(" ", type=["png", "jpg", "jpeg"])
    image = None
    if photo: image = Image.open(photo)
    elif upload: image = Image.open(upload)

    if image:
        st.success("✅ Hình ảnh đã được nạp thành công!")
    
    st.markdown("<br>", unsafe_allow_html=True)

    # ----------------- BƯỚC 2 -----------------
    st.markdown("""
    <div class='modern-card'>
        <div class='card-title'><div class='card-title-icon'>📝</div> Dữ liệu Lâm sàng & Ngôn ngữ</div>
    """, unsafe_allow_html=True)
    extra_info = st.text_area("", placeholder="Nhập mô tả của nông dân (VD: Gà chảy nhớt dãi xù lông bỏ ăn, lá lúa bị đốm mắt én giống cháy khét...)", height=70)

    st.markdown("<br>**Ngôn ngữ kết quả:**", unsafe_allow_html=True)
    col_lang1, col_lang2 = st.columns(2)
    with col_lang1: use_vi = st.checkbox("🇻🇳 Tiếng Việt", value=True, disabled=True)
    with col_lang2: use_hmong = st.checkbox("🏔️ Tiếng H’Mông", value=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ----------------- NÚT XỬ LÝ -----------------
    submit_btn = st.button("🚀 KÍCH HOẠT AI CHẨN ĐOÁN NGAY")
    
    # Học liệu Dự án đặt gọn gàng ở cuối cột nhập liệu
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("Học liệu Dự án"):
        st.markdown("""
        <div class='reference-box'>
            <b style='color:#0f172a; font-size:14px;'>🔬 1. Bản chất Hệ thống RAG</b><br>
            Mô hình ứng dụng kỹ thuật RAG số hóa thủ công (Manual Indexing) tài liệu phác đồ thật của cơ quan chức năng để nạp trực tiếp thành Cơ sở dữ liệu nội bộ, bảo đảm đầu ra chính xác tuyệt đối.
            <br><br>
            <b style='color:#0f172a; font-size:14px;'>📚 2. Nguồn tài liệu gốc:</b>
            <ul>
                <li><b>Phác đồ Thú y:</b> Trích xuất từ <a href='http://www.khuyennongvn.gov.vn/' target='_blank' style='color: #0284c7; text-decoration: none;'><b>Khuyến nông Quốc gia</b></a> & <a href='http://cucthuy.gov.vn/' target='_blank' style='color: #0284c7; text-decoration: none;'><b>Cục Thú y</b></a>.</li>
                <li><b>Thời tiết vùng cao:</b> Hướng dẫn của <a href='https://sonongnghiep.dienbien.gov.vn/' target='_blank' style='color: #0284c7; text-decoration: none;'><b>Sở NN&PTNT Điện Biên</b></a>.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


with col_right:
    # ----------------- KẾT QUẢ CHẨN ĐOÁN VÀ ẢNH SONG SONG -----------------
    if submit_btn:
        if not image: st.error("⚠️ Vui lòng chụp hoặc tải ảnh lên ở cột bên trái!")
        elif not api_key: st.error("⚠️ Hệ thống chưa được cấp quyền (Nhập API Key ở Menu trái)!")
        else:
            with st.spinner("⏳ AI đang trích xuất dữ liệu lâm sàng và đối chiếu dữ liệu..."):
                langs = ["Tiếng Phổ Thông"]
                if use_hmong: langs.append("Tiếng dân tộc H’Mông")
                lang_str = " – ".join(langs)
                extra_prompt = f"\n- Lời kể lâm sàng của bà con: {extra_info}" if extra_info else ""

                prompt_text = fr"""
Bạn là AI chẩn đoán nông nghiệp uy tín chuyên trách vùng Tây Bắc. Hãy lập hồ sơ bệnh án chuẩn xác.
[TÀI LIỆU LUẬT ĐỊNH RAG]{RAG_KNOWLEDGE_BASE}[/KẾT THÚC TÀI LIỆU]

⚠️ QUY TẮC RAG CỰC KỲ NGHIÊM NGẶT:
1. Bạn BẮT BUỘC phải trích xuất câu trả lời đối chiếu trực tiếp từ [TÀI LIỆU LUẬT ĐỊNH RAG] ở trên. 
2. CHỈ ĐƯỢC đề xuất các loại tên hoạt chất thuốc, biện pháp xử lý có ghi rõ trong tài liệu kiểm chứng. Không tự bịa thuốc ngoài danh mục. Nếu triệu chứng không nằm trong tài liệu, thông báo: "Hệ thống RAG chưa ghi nhận phác đồ cho ca bệnh này, đề nghị báo cán bộ hỗ trợ trực tiếp".
3. Lời khuyên phải rõ ràng, ngắn gọn theo cấu trúc 4 phần sau cho mỗi ngôn ngữ:
   - 🔍 **Dấu hiệu lâm sàng:** (Mô tả chi tiết triệu chứng thấy trên ảnh)
   - 🩺 **Chẩn đoán sơ bộ:** (Tên bệnh hoặc loại sâu bệnh phá hoại)
   - 📋 **Phác đồ điều trị chuẩn:** (Các bước cách ly, tên thuốc, kỹ thuật phun/bôi trích xuất từ tài liệu)
   - 🚨 **Khuyến cáo dịch tễ:** (Biện pháp phòng ngừa và dặn báo cán bộ)
4. Dịch chuẩn xác sang ({lang_str}). Sử dụng phiên âm chữ Latinh cho tiếng dân tộc để bà con dễ đọc.{extra_prompt}

⚠️ CHIA THẺ ĐỂ CẮT ÂM THANH:
[VI] (Nội dung Tiếng Việt)
[HMN] (Nội dung H'Mông - nếu có)
"""
                result = analyze_real_image(api_key, image, prompt_text)
                
                if result.startswith("❌"): st.error(result)
                else:
                    vi_match = re.search(r'\[VI\](.*?)(?=\[HMN\]|$)', result, re.DOTALL)
                    hmn_match = re.search(r'\[HMN\](.*?)$', result, re.DOTALL)
                    vi_text = vi_match.group(1).strip() if vi_match else result
                    hmn_text = hmn_match.group(1).strip() if hmn_match else ""

                    display_text = result.replace("[VI]", "🇻🇳 **HỒ SƠ TIẾNG VIỆT:**\n").replace("[HMN]", "\n---\n🏔️ **HỒ SƠ TIẾNG H'MÔNG:**\n")
                    
                    # HỘP CHỨA KẾT QUẢ ĐỒNG BỘ: ẢNH 1 BÊN - CHẨN ĐOÁN 1 BÊN
                    st.markdown("""
                    <div class='modern-card' style='border-top: 4px solid #10b981;'>
                        <div class='card-title'><div class='card-title-icon' style='background:#dcfce7; color:#16a34a;'>📋</div> Kết quả Phân tích & Phác đồ Đối chiếu</div>
                    """, unsafe_allow_html=True)
                    
                    # Chia nhỏ cột nội bộ để ảnh nằm cạnh chữ chẩn đoán
                    img_col, txt_col = st.columns([1, 1.8], gap="small")
                    with img_col:
                        st.image(image, use_container_width=True, caption="Ảnh vật nuôi/cây trồng đã nạp")
                    with txt_col:
                        st.markdown(display_text)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Âm thanh hỗ trợ
                    st.markdown("""
                    <div class='modern-card'>
                        <div class='card-title'><div class='card-title-icon' style='background:#f3e8ff; color:#9333ea;'>🔊</div> Trợ lý Giọng nói Phổ thông</div>
                    """, unsafe_allow_html=True)
                    if vi_text:
                        st.write("🇻🇳 **Giọng Tiếng Việt:**")
                        clean_vi = vi_text.replace('*', '').replace('#', '').replace('🔍', '').replace('🩺', '').replace('📋', '').replace('🚨', '')
                        audio_vi = generate_audio(clean_vi, 'vi')
                        if audio_vi: st.audio(audio_vi, format="audio/mp3")
                    if (use_hmong and hmn_text):
                        st.info("💡 Tính năng Text-to-Speech tiếng H'Mông bản địa đang chờ bổ sung từ ngân hàng dữ liệu thu âm thực tế địa phương.")
                    st.markdown("</div>", unsafe_allow_html=True)

                    st.session_state.history.insert(0, {"time": datetime.now().strftime("%d/%m/%Y %H:%M"), "result": display_text})
    
    else:
        st.info("👈 **Mời bà con nhập dữ liệu** (Tải ảnh, điền mô tả) ở cột bên trái rồi bấm nút **Kích hoạt AI** để xem kết quả chẩn đoán hiển thị tại đây.")

    # Luôn hiển thị cổng thông tin khẩn cấp ở cột bên phải
    st.markdown("""
    <div class='modern-card'>
    <div class='card-title'><div class='card-title-icon' style='background:#fee2e2; color:#ef4444;'>🚨</div> Cổng Thông Tin Hỗ Trợ Khẩn Cấp</div>
    <p style='color:#475569; font-size:12px; margin-bottom:12px;'>Bà con truy cập các kênh chính thống để tìm kiếm sự hỗ trợ trực tiếp từ cơ quan chức năng khi dịch bệnh lây lan:</p>

    <a href='https://sonongnghiep.dienbien.gov.vn/' target='_blank' style='text-decoration: none;'>
    <div class='link-box' style='border-left: 4px solid #0ea5e9;'>🌐 Sở Nông nghiệp & PTNT tỉnh Điện Biên</div>
    </a>

    <a href='http://cucthuy.gov.vn/' target='_blank' style='text-decoration: none;'>
    <div class='link-box' style='border-left: 4px solid #f59e0b;'>🏥 Cục Thú y Việt Nam</div>
    </a>

    <a href='http://www.khuyennongvn.gov.vn/' target='_blank' style='text-decoration: none;'>
    <div class='link-box' style='border-left: 4px solid #10b981;'>🌾 Trung tâm Khuyến nông Quốc gia</div>
    </a>
    </div>
    """, unsafe_allow_html=True)
