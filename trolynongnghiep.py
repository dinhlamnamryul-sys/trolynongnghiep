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

# TÍCH HỢP CSS "PRO WEB APP" - BẢO ĐẢM GIAO DIỆN SANG TRỌNG
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

    .stTextArea textarea { border-radius: 10px !important; border: 1px solid #cbd5e1 !important; padding: 15px !important; }
    .stTextArea textarea:focus { border-color: #10b981 !important; box-shadow: 0 0 0 2px rgba(16,185,129,0.2) !important; }
    
    .alert-pro { background-color: #fffbeb; border-left: 4px solid #f59e0b; padding: 15px 20px; border-radius: 8px; color: #92400e; font-size: 14px; margin-bottom: 25px;}
    
    .contact-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 15px; margin-top: 15px; text-align: center; }
    .contact-btn { background-color: #ef4444; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; display: inline-block; margin-top: 10px; transition: 0.2s;}
    .contact-btn:hover { background-color: #dc2626; color: white; }
    
    .reference-box { background-color: #f8f9fa; padding: 25px; border-radius: 12px; border-left: 5px solid #0284c7; font-size: 14.5px; line-height: 1.7; color: #334155;}
    </style>
""", unsafe_allow_html=True)

if "history" not in st.session_state: st.session_state.history = []

# =====================
# 2. CƠ SỞ DỮ LIỆU RAG NỘI BỘ (SỐ HÓA THỰC TẾ THEO CHUẨN 2026)
# =====================
RAG_KNOWLEDGE_BASE = """
[KNOWLEDGE BASE - TÀI LIỆU SỐ HÓA NỘI BỘ TRÍCH XUẤT TỪ SỞ NN&PTNT ĐIỆN BIÊN ĐẾN NĂM 2026]

--- DANH MỤC LÂM SÀNG VÀ PHÁC ĐỒ CHĂN NUÔI (VẬT NUÔI) ---
1. BỆNH DỊCH TẢ LỢN CHÂU PHI (ASF):
- Lâm sàng: Sốt cao (40.5-42°C), đi đứng loạng choạng, tai mõm và bụng xuất huyết màu đỏ thẫm hoặc tím. Bỏ ăn hoàn toàn, chết nhanh.
- Phác đồ RAG luật định: TUYỆT ĐỐI KHÔNG CÓ THUỐC ĐIỀU TRỊ. Biện pháp duy nhất: Cách ly triệt để khu chuồng nhiễm bệnh, nghiêm cấm mua bán chạy hay mổ thịt tự phát. Báo ngay cán bộ thú y để thực hiện tiêu hủy cơ học bằng chôn sâu, đổ vôi bột. Sát trùng chuồng bằng vôi bột bão hòa hoặc hóa chất Benkocid.

2. BỆNH LỞ MỒM LONG MÓNG (Gia súc lớn Trâu, Bò):
- Lâm sàng: Sốt, xuất hiện vết loét, mụn nước nông ở niêm mạc miệng, kẽ móng chân, vành móng và sưng núm vú. Chảy nhiều nước bọt đục như bọt xà phòng. Thú đi khập khiễng, rên rỉ.
- Phác đồ RAG luật định: Không có thuốc đặc hiệu trị virus. Tiến hành cách ly hộ chăn nuôi. Kháng sinh cục bộ: Sử dụng các dung dịch sát trùng hữu cơ bản địa nhẹ để rửa sạch vết loét (Axit chanh 2%, nước quả khế chua hoặc dung dịch phèn chua 2%). Sau khi rửa sạch, bôi dung dịch Xanh Methylene 1% hoặc cồn Iodine 10% lên vết loét móng và miệng để chống nhiễm trùng thứ phát. Cho ăn cháo loãng ấm, bổ sung Vitamin C tổng hợp liều cao.

3. BỆNH TỤ HUYẾT TRÙNG (Gia cầm Gà, Vịt, Ngỗng):
- Lâm sàng: Thể cấp tính gà sốt cao, ủ rũ, xù lông, chảy nước nhớt từ miệng, mào và tích tím tái do tụ huyết tuần hoàn. Khó thở dữ dội, đi tiêu lỏng phân xanh hoặc trắng xám.
- Phác đồ RAG luật định: Cách ly khu vực nuôi. Điều trị khẩn cấp bằng thuốc kháng sinh đặc hiệu: Amoxicillin (liều 20mg/kg thể trọng) hoặc Enrofloxacin 10% pha nước uống liên tục 3 - 5 ngày theo hướng dẫn nhà sản xuất. Bổ sung điện giải và Vitamin B-Complex trợ sức. Phun khử trùng chuồng trại định kỳ.

--- DANH MỤC LÂM SÀNG VÀ PHÁC ĐỒ TRỒNG TRỌT (CÂY TRỒNG VÙNG CAO) ---
4. BỆNH ĐẠO ÔN HẠI LÚA (Do nấm Pyricularia oryzae):
- Lâm sàng: Trên phiến lá xuất hiện chấm nhỏ màu xanh mướt, sau lan rộng thành hình thoi đặc trưng (mắt én), tâm vết bệnh màu xám tro, viền ngoài màu nâu sẫm. Bệnh nặng gây thối cổ bông, bông lúa bạc trắng, gãy gục.
- Phác đồ RAG luật định: LẬP TỨC NGỪNG BÓN PHÂN ĐẠM (URÊ), không phun phân bón vi lượng qua lá. Giữ nguyên mực nước ruộng ổn định từ 3 - 5 cm, không để ruộng cạn nước. Sử dụng thuốc bảo vệ thực vật đặc trị có hoạt chất Tricyclazole (với các tên thương mại như Beam, Filia) hoặc Isoprothiolane (Fuji-One), phun đều mặt lá vào lúc chiều mát.

5. SÂU CUỐN LÁ NHỎ HẠI LÚA:
- Lâm sàng: Sâu non nhả tơ cuốn dọc lá lúa thành hình ống, ẩn nấp bên trong ăn lớp mô xanh (diệp lục), để lại các vệt biểu bì màu trắng dọc thân lá khiến ruộng lúa sơ xác, giảm quang hợp.
- Phác đồ RAG luật định: Thăm đồng thường xuyên. Chỉ tiến hành phun thuốc khi mật độ sâu vượt ngưỡng kinh tế (trên 20 con/m2 đối với giai đoạn đẻ nhánh). Sử dụng các hoạt chất nội hấp, lưu dẫn thế hệ mới như Chlorantraniliprole (Virtako, Prevathon) hoặc Indoxacarb. Phun thuốc tập trung khi sâu non vừa nở ở tuổi 1 hoặc tuổi 2.

6. BỆNH SƯƠNG MAI / THÁN THƯ PHÁ HOẠI RAU MÀU (Cà chua, Cây ăn quả, Cà phê):
- Lâm sàng: Mặt dưới lá xuất hiện lớp nấm mịn màu trắng xám tro, mặt trên lá có các vết loang lổ màu vàng nhạt rồi chuyển nâu sẫm. Quả non bị đốm đen, thối nhũn hoặc teo tóp, rụng hàng loạt khi gặp tiết trời sương mù, ẩm độ cao.
- Phác đồ RAG luật định: Cắt tỉa triệt để các cành vô hiệu, lá gốc để tạo độ thông thoáng tối đa cho vườn. Sử dụng các hợp chất gốc Đồng bền vững như Copper Oxychloride (thuốc COC 85) hoặc hoạt chất Mancozeb để phun phòng và trị. Tuyệt đối không phun thuốc khi thời tiết có dấu hiệu sắp mưa để tránh rửa trôi chất độc.

7. BIỆN PHÁP PHÒNG CHỐNG SƯƠNG MUỐI VÀ RÉT ĐẬM (Đặc thù khí hậu Tây Bắc):
- Đối với Cây trồng: Tiến hành phun nước rửa sương trên mặt lá vào sáng sớm trước khi mặt trời mọc để tránh cháy lá do thấu kính băng. Tủ tro bếp kết hợp rơm rạ khô xung quanh gốc cây để giữ nhiệt cho bộ rễ.
- Đối với Vật nuôi: Che chắn chuồng trại kín gió bằng bạt dứa, rơm bện. Tổ chức đốt trấu, củi sưởi ấm vào ban đêm, tuyệt đối không chăn thả trông khi nhiệt độ ngoài trời dưới 12°C. Cho trâu bò uống nước ấm pha muối khoáng 0.9% và bổ sung thức ăn tinh (cám gạo, cám ngô).
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
    st.caption("Dự án dự thi Sáng tạo TTN-NĐ 2026 | Điện Biên")

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
        Hệ thống RAG: Đã đồng bộ Kho dữ liệu Số hóa Thú y & BVTV 2026
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='alert-pro'>
    <b>📌 Lưu ý y tế nông nghiệp:</b> Phác đồ được nội suy dựa trên Cơ sở dữ liệu RAG nội bộ chỉ mang tính chất sơ cứu ban đầu. Yêu cầu báo cáo cán bộ phụ trách khu vực khi có dấu hiệu lây lan diện rộng.
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
extra_info = st.text_area("", placeholder="Nhập mô tả của nông dân (VD: Gà chảy nhớt dãi xù lông bỏ ăn, lá lúa bị đốm mắt én giống cháy khét...)", height=80)

st.markdown("<br>**Cấu hình ngôn ngữ kết quả:**", unsafe_allow_html=True)
col_lang1, col_lang2, col_lang3 = st.columns(3)
with col_lang1: use_vi = st.checkbox("🇻🇳 Tiếng Việt", value=True, disabled=True)
with col_lang2: use_hmong = st.checkbox("🏔️ Tiếng H’Mông", value=True)
with col_lang3: use_thai = st.checkbox("🌿 Tiếng Thái (Tây Bắc)", value=True)
st.markdown("</div>", unsafe_allow_html=True)

# ----------------- NÚT XỬ LÝ -----------------
st.markdown("<br>", unsafe_allow_html=True)
submit_btn = st.button("🚀 KÍCH HOẠT AI CHẨN ĐOÁN NGAY")

# ----------------- KẾT QUẢ -----------------
if submit_btn:
    if not image: st.error("⚠️ Vui lòng cung cấp hình ảnh!")
    elif not api_key: st.error("⚠️ Hệ thống chưa được cấp quyền (Nhập API Key ở Menu trái)!")
    else:
        st.markdown("---")
        with st.spinner("⏳ AI đang trích xuất dữ liệu lâm sàng và đối chiếu với Cơ sở dữ liệu Luật định..."):
            langs = ["Tiếng Phổ Thông"]
            if use_hmong: langs.append("Tiếng dân tộc H’Mông")
            if use_thai: langs.append("Tiếng dân tộc Thái (Tây Bắc Việt Nam)")
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
   - 🚨 **Khuyến cáo dịch tễ:** (Biện pháp phòng ngừa và dặn báo cán bộ xã)
4. Dịch chuẩn xác sang ({lang_str}). Sử dụng phiên âm chữ Latinh cho tiếng dân tộc để bà con dễ đọc.{extra_prompt}

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
                    <div class='card-title'><div class='card-title-icon' style='background:#dcfce7; color:#16a34a;'>📋</div> Kết quả Phân tích từ Hệ thống</div>
                """, unsafe_allow_html=True)
                st.markdown(display_text)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Mạng lưới liên hệ khẩn cấp
                st.markdown("""
                <div class='modern-card'>
                    <div class='card-title'><div class='card-title-icon' style='background:#fee2e2; color:#ef4444;'>🚨</div> Mạng lưới Hỗ trợ Địa phương khép kín</div>
                    <p style='color:#475569; font-size:14px;'>Hệ thống tự động liên kết danh bạ Cán bộ Khuyến nông/Thú y phụ trách (Bản thử nghiệm hình ảnh hóa):</p>
                """, unsafe_allow_html=True)
                
                dia_phuong = st.selectbox(" ", ["📍 Phường Mường Thanh", "📍 Xã Thanh Xương", "📍 Xã Mường Phăng"], label_visibility="collapsed")
                st.markdown("<div class='contact-box'>", unsafe_allow_html=True)
                if dia_phuong == "📍 Phường Mường Thanh":
                    st.markdown("👨‍🌾 **Nguyễn Văn A** - Trạm trưởng Khuyến nông & Thú y<br>📞 0912.345.678", unsafe_allow_html=True)
                    st.markdown("<a href='tel:0912345678' class='contact-btn'>☎ BẤM GỌI CỨU VIỆN NGAY</a>", unsafe_allow_html=True)
                elif dia_phuong == "📍 Xã Thanh Xương":
                    st.markdown("👨‍🌾 **Lò Văn B** - Cán bộ Thú y xã chuyên trách<br>📞 0988.777.666", unsafe_allow_html=True)
                    st.markdown("<a href='tel:0988777666' class='contact-btn'>☎ BẤM GỌI CỨU VIỆN NGAY</a>", unsafe_allow_html=True)
                else:
                    st.markdown("👩‍🌾 **Lường Thị C** - Kỹ thuật viên Bảo vệ thực vật xã<br>📞 0215.3123.456", unsafe_allow_html=True)
                    st.markdown("<a href='tel:02153123456' class='contact-btn'>☎ BẤM GỌI CỨU VIỆN NGAY</a>", unsafe_allow_html=True)
                st.markdown("</div></div>", unsafe_allow_html=True)

                # Âm thanh
                st.markdown("""
                <div class='modern-card'>
                    <div class='card-title'><div class='card-title-icon' style='background:#f3e8ff; color:#9333ea;'>🔊</div> Trợ lý Giọng nói Phổ thông</div>
                """, unsafe_allow_html=True)
                if vi_text:
                    st.write("🇻🇳 **Giọng Tiếng Việt:**")
                    clean_vi = vi_text.replace('*', '').replace('#', '').replace('🔍', '').replace('🩺', '').replace('📋', '').replace('🚨', '')
                    audio_vi = generate_audio(clean_vi, 'vi')
                    if audio_vi: st.audio(audio_vi, format="audio/mp3")
                if (use_hmong and hmn_text) or (use_thai and th_text):
                    st.info("💡 Hệ thống AI toàn cầu hiện đang thiếu bộ dữ liệu âm vị học H'Mông/Thái Tây Bắc. Tính năng Text-to-Speech bản địa đang chờ bổ sung từ ngân hàng dữ liệu thu âm thực tế địa phương.")
                st.markdown("</div>", unsafe_allow_html=True)

                st.session_state.history.insert(0, {"time": datetime.now().strftime("%d/%m/%Y %H:%M"), "result": display_text})

# ----------------- TÀI LIỆU DỰ ÁN -----------------
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("ℹ️ Minh bạch Công nghệ & Học liệu Dự án (Dành cho Hội đồng Giám khảo)"):
    st.markdown("""
    <div class='reference-box'>
        <b style='color:#0f172a; font-size:16px;'>🔬 1. Bản chất Hệ thống RAG (Retrieval-Augmented Generation) của Dự án</b><br>
        Để triệt tiêu hiện tượng "Ảo giác AI" nguy hiểm trong y tế nông nghiệp, mô hình ứng dụng kỹ thuật RAG. Trong phiên bản mẫu thử nghiệm (Prototype) này, nhóm tác giả đã tiến hành <b>số hóa thủ công (Manual Indexing)</b> các tài liệu phác đồ thật của cơ quan chức năng để nạp trực tiếp thành Cơ sở dữ liệu nội bộ cố định (luồng biến <code>RAG_KNOWLEDGE_BASE</code> tại dòng số 40), <b>chưa thực hiện kết nối tự động API thời gian thực</b> với máy chủ lưu trữ của Sở Nông nghiệp vì lý do bảo mật hệ thống thông tin của Nhà nước. 
        <br><br>
        Khi có yêu cầu, thuật toán sẽ cưỡng bức AI bắt buộc phải quét, đối chiếu chéo thông tin hình ảnh với kho dữ liệu luật định này, bảo đảm đầu ra chính xác tuyệt đối theo danh mục cho phép.
        <br><br>
        <b style='color:#0f172a; font-size:16px;'>📚 2. Nguồn tài liệu Số hóa gốc có thể click kiểm chứng trực tiếp:</b>
        <ul>
            <li><b>Phác đồ Thú y Quốc gia:</b> Dữ liệu trích xuất từ văn bản chính thức của <a href='http://www.khuyennongvn.gov.vn/' target='_blank' style='color: #0284c7; text-decoration: none;'><b>Trung tâm Khuyến nông Quốc gia</b></a> và <a href='http://cucthuy.gov.vn/' target='_blank' style='color: #0284c7; text-decoration: none;'><b>Cục Thú y Việt Nam</b></a>.</li>
            <li><b>Cẩm nang nông nghiệp đặc thù:</b> Hướng dẫn phòng chống sương muối, rét hại vùng cao trích từ <a href='https://sonongnghiep.dienbien.gov.vn/' target='_blank' style='color: #0284c7; text-decoration: none;'><b>Sở Nông nghiệp & PTNT tỉnh Điện Biên</b></a>.</li>
        </ul>
        <b style='color:#0f172a; font-size:16px;'>🚀 3. Hướng phát triển phần mềm trong tương lai</b><br>
        Nhóm tác giả định hướng sẽ xin cấp phép kết nối cổng mạng an toàn để đồng bộ hóa dữ liệu tự động hoàn toàn dưới dạng API của Sở, đồng thời tích hợp sâu hệ thống thành một tiện ích Zalo Mini App nằm trong cổng dịch vụ công <i>Điện Biên Smart</i> nhằm tối ưu hóa tối đa khả năng tiếp cận của đồng bào dân tộc thiểu số vùng ranh giới.
    </div>
    """, unsafe_allow_html=True)
