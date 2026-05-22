import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO
import json
from datetime import datetime

# =====================
# CẤU HÌNH TRANG & CSS
# =====================
st.set_page_config(page_title="Trợ Lý Nông Nghiệp Bản Làng", page_icon="🌱", layout="wide")

# CSS Tùy chỉnh để làm đẹp giao diện
st.markdown("""
    <style>
    .main-title { color: #2e7d32; text-align: center; font-weight: bold; }
    .sub-title { text-align: center; color: #555; font-style: italic; margin-bottom: 20px; }
    .warning-box { background-color: #fff3cd; color: #856404; padding: 15px; border-left: 5px solid #ffeeba; border-radius: 5px; margin-bottom: 20px; font-size: 0.95em;}
    .stButton>button { background-color: #2e7d32; color: white; border-radius: 8px; font-weight: bold; width: 100%; transition: 0.3s; }
    .stButton>button:hover { background-color: #1b5e20; border-color: #1b5e20; }
    </style>
""", unsafe_allow_html=True)

# Khởi tạo Session State để lưu lịch sử
if "history" not in st.session_state:
    st.session_state.history = []

# =====================
# SIDEBAR: CẤU HÌNH API
# =====================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3004/3004122.png", width=80)
    st.header("⚙️ Cấu hình hệ thống")
    api_key = st.text_input("🔑 Nhập Google API Key:", type="password", help="Bắt buộc để sử dụng AI")
    
    with st.expander("👉 Hướng dẫn lấy API Key"):
        st.markdown("""
        1. Vào **[Google AI Studio](https://aistudio.google.com/app/apikey)**
        2. Đăng nhập Gmail.
        3. Nhấn **Create API key**.
        4. Copy và dán vào ô bên trên.
        """)
        
    st.markdown("---")
    st.caption("Bản quyền © 2026. Ứng dụng hỗ trợ đồng bào vùng cao.")

# =====================
# GIAO DIỆN CHÍNH
# =====================
st.markdown("<h1 class='main-title'>🌱 Trợ Lý Nông Nghiệp Bản Làng</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Hỗ trợ chẩn đoán bệnh cây trồng, vật nuôi (Việt – H’Mông)</p>", unsafe_allow_html=True)

st.markdown("""
<div class='warning-box'>
    <b>⚠️ Lưu ý an toàn:</b> Kết quả chẩn đoán của AI chỉ mang tính chất tham khảo bước đầu. Bà con nên kết hợp với kinh nghiệm thực tế hoặc báo ngay cho cán bộ khuyến nông/thú y xã nếu bệnh lây lan nhanh.
</div>
""", unsafe_allow_html=True)

# ===============================
# HÀM GỌI GEMINI (GIỮ NGUYÊN LOGIC CỦA BẠN)
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
            return f"❌ Lỗi API {res.status_code}: {res.text}"

        data = res.json()
        if "candidates" not in data:
            return "❌ API trả về rỗng."

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        return f"❌ Lỗi kết nối: {str(e)}"

# ===============================
# KHU VỰC NHẬP DỮ LIỆU
# ===============================
col_input, col_settings = st.columns([1.5, 1], gap="large")

with col_input:
    st.subheader("📸 Cung cấp hình ảnh")
    # Sử dụng Tabs để giao diện gọn gàng hơn
    tab1, tab2 = st.tabs(["📷 Chụp từ Camera", "📤 Tải ảnh có sẵn"])
    
    photo, upload = None, None
    with tab1:
        photo = st.camera_input("Chụp ảnh cây/con vật bị bệnh:")
    with tab2:
        upload = st.file_uploader("Chọn ảnh từ điện thoại/máy tính:", type=["png", "jpg", "jpeg"])

    image = None
    if photo:
        image = Image.open(photo)
    elif upload:
        image = Image.open(upload)
        
    if image:
        st.success("✅ Đã nhận ảnh thành công!")

with col_settings:
    st.subheader("📝 Thông tin bổ sung")
    extra_info = st.text_area("Mô tả thêm triệu chứng (Không bắt buộc):", 
                              placeholder="Ví dụ: Lợn bỏ ăn 2 ngày, bị tiêu chảy... hoặc Cây héo lá từ gốc lên...",
                              height=100)
    
    st.subheader("⚙️ Tùy chọn chẩn đoán")
    st.markdown("**Ngôn ngữ hiển thị:**")
    use_hmong = st.checkbox("✅ Dịch kèm Tiếng H’Mông", value=True)
    
    submit_btn = st.button("🔍 BẮT ĐẦU CHẨN ĐOÁN", type="primary", use_container_width=True)

st.markdown("---")

# ===============================
# XỬ LÝ & HIỂN THỊ KẾT QUẢ
# ===============================
if submit_btn:
    if not image:
        st.error("❌ Vui lòng chụp hoặc tải ảnh lên trước khi chẩn đoán!")
    elif not api_key:
        st.error("❌ Bạn chưa nhập Google API Key ở thanh công cụ bên trái (Sidebar)!")
    else:
        # Layout kết quả
        res_col1, res_col2 = st.columns([1, 2], gap="large")
        
        with res_col1:
            st.image(image, caption="Ảnh bà con cung cấp", use_container_width=True)
            
        with res_col2:
            with st.spinner("⏳ Kỹ sư AI đang phân tích dữ liệu..."):
                # Thiết lập danh sách ngôn ngữ động
                langs = ["Việt"]
                if use_hmong: langs.append("H’Mông")
                lang_str = " – ".join(langs)
                
                prompt_structure = "Tiếng Việt"
                if use_hmong: prompt_structure += " và Tiếng H’Mông"
                
                extra_prompt = f"\n- Thông tin bổ sung từ bà con: {extra_info}" if extra_info else ""

                # PROMPT ĐƯỢC GIỮ NGUYÊN VÀ BỔ SUNG THÊM THÔNG TIN MÔ TẢ
                prompt_text = fr"""
Bạn là một kỹ sư nông nghiệp và bác sĩ thú y giàu kinh nghiệm, đặc biệt am hiểu thực tế làm nông ở vùng cao.
Hãy quan sát kỹ bức ảnh và **chẩn đoán bệnh**, đưa ra lời khuyên theo phong cách DỄ HIỂU, GẦN GŨI VỚI BÀ CON NÔNG DÂN bằng ({lang_str}).{extra_prompt}

==============================
⚠️ QUY TẮC AN TOÀN CHẨN ĐOÁN
==============================
- Nếu ảnh KHÔNG RÕ RÀNG hoặc KHÔNG PHẢI cây trồng/vật nuôi: Hãy nói thật là "Ảnh mờ quá hoặc không đúng chủ đề, AI không nhìn rõ, bà con chụp lại nhé". TUYỆT ĐỐI KHÔNG đoán bừa.
- Nếu bệnh có nhiều nguyên nhân giống nhau: Hãy liệt kê các khả năng (Ví dụ: "Lá vàng này có thể do thiếu phân hoặc do úng nước...").
- Luôn có câu chốt: "Khuyên bà con nên báo cho cán bộ thú y/khuyến nông xã để được hỗ trợ thêm".

=====================
1️⃣ CHẨN ĐOÁN BỆNH
=====================
- Nhìn vào ảnh, đây là con vật/cây gì? Triệu chứng hiện tại là gì?
- Dự đoán bệnh (Trình bày bằng: {prompt_structure}).

==========================
2️⃣ CÁCH XỬ LÝ (Tham khảo)
==========================
- Cách cách ly, chăm sóc để không lây lan.
- Gợi ý cách xử lý an toàn, thuốc phổ thông hoặc kinh nghiệm dân gian (Trình bày bằng {prompt_structure}).

==========================
3️⃣ LƯU Ý TRÌNH BÀY
==========================
- Sử dụng từ ngữ mộc mạc, ngắn gọn. 
- Phân đoạn rõ ràng giữa Tiếng Việt và Tiếng H'Mông để bà con dễ đọc.
- Tuyệt đối không dùng các thuật ngữ khoa học hàn lâm phức tạp.
"""
                result = analyze_real_image(api_key, image, prompt_text)
                
                if result.startswith("❌"):
                    st.error(result)
                else:
                    st.toast('🎉 Phân tích hoàn tất!', icon='✅')
                    st.success("📝 Dưới đây là kết quả phân tích từ Trợ lý AI:")
                    
                    # Hiển thị kết quả trong khung đẹp mắt
                    with st.container(border=True):
                        st.markdown(result)
                    
                    # Lưu vào lịch sử
                    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
                    st.session_state.history.insert(0, {"time": timestamp, "result": result, "info": extra_info})
                    
                    # TÍNH NĂNG MỚI: Nút tải kết quả (Download)
                    st.download_button(
                        label="📥 Tải kết quả này về máy (File Text)",
                        data=result,
                        file_name=f"Chan_doan_Nong_Nghiep_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                        mime="text/plain"
                    )

# ===============================
# TÍNH NĂNG MỚI: LỊCH SỬ CHẨN ĐOÁN
# ===============================
if st.session_state.history:
    st.markdown("---")
    st.subheader("🕒 Lịch sử chẩn đoán gần đây")
    for i, item in enumerate(st.session_state.history[:3]): # Chỉ hiện 3 cái gần nhất cho gọn
        with st.expander(f"Kết quả lúc: {item['time']}"):
            if item['info']:
                st.caption(f"**Mô tả của bà con:** {item['info']}")
            st.markdown(item['result'])
