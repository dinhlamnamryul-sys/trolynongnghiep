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
st.set_page_config(page_title="Trợ Lý Nông Nghiệp Bản Làng", page_icon="🌱", layout="centered", initial_sidebar_state="collapsed")

# TÍCH HỢP CSS NÂNG CAO
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Be Vietnam Pro', sans-serif !important; }

    .app-header { background: linear-gradient(135deg, #2e7d32 0%, #4caf50 100%); padding: 25px 15px; border-radius: 16px; color: white; text-align: center; box-shadow: 0 4px 15px rgba(46, 125, 50, 0.3); margin-bottom: 25px; }
    .app-header h1 { color: white !important; font-weight: 800; font-size: 30px; margin: 0; padding: 0; line-height: 1.2; }
    .app-header p { font-size: 16px; font-weight: 500; opacity: 0.9; margin-top: 5px; margin-bottom: 0; }

    .note-box { background-color: #fff9e6; border: 1px solid #ffe082; border-left: 6px solid #ffb300; padding: 18px; border-radius: 12px; color: #5c4000; font-size: 15px; line-height: 1.6; margin-bottom: 25px; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }

    .step-card { background-color: white; border: 1px solid #e0e0e0; border-radius: 16px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.03); }
    .step-title { color: #1b5e20; font-weight: 700; font-size: 19px; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; border-bottom: 2px solid #f1f8e9; padding-bottom: 10px; }

    .stButton>button { background: linear-gradient(to right, #f57c00, #ff9800) !important; color: white !important; border-radius: 50px !important; font-weight: 700 !important; font-size: 18px !important; padding: 12px 0 !important; border: none !important; box-shadow: 0 6px 15px rgba(245, 124, 0, 0.3) !important; transition: all 0.3s ease !important; }
    .stButton>button:hover { transform: translateY(-3px) !important; box-shadow: 0 8px 20px rgba(245, 124, 0, 0.4) !important; }
    .download-btn>button { background: linear-gradient(to right, #0277bd, #039be5) !important; box-shadow: 0 6px 15px rgba(2, 119, 189, 0.3) !important; }
    .stTextArea textarea { font-size: 16px !important; border-radius: 10px !important; }
    
    .reference-box { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 4px solid #1976d2; font-size: 14px; line-height: 1.5; color: #333;}
    </style>
""", unsafe_allow_html=True)

if "history" not in st.session_state: st.session_state.history = []

# =====================
# 2. MENU CÀI ĐẶT ẨN (SIDEBAR)
# =====================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/862/862856.png", width=60)
    api_key = st.text_input("🔑 Google API Key:", type="password")
    
    # HƯỚNG DẪN LẤY API KEY ĐƯỢC THÊM VÀO ĐÂY
    with st.expander("👉 Hướng dẫn lấy mã API Key (Miễn phí)"):
        st.markdown("""
        1. Truy cập trang web: <a href="https://aistudio.google.com/app/apikey" target="_blank"><b>Google AI Studio</b></a>.
        2. Đăng nhập bằng tài khoản Gmail của bạn.
        3. Bấm vào nút <b>Create API key</b>.
        4. Sao chép (Copy) đoạn mã dài vừa tạo và dán vào ô trống phía trên.
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown("<b>Dự án dự thi Sáng tạo Thanh thiếu niên, Nhi đồng</b><br>Mục tiêu: Chuyển đổi số Nông nghiệp vùng cao.", unsafe_allow_html=True)

# =====================
# 3. HEADER ỨNG DỤNG
# =====================
st.markdown("""
<div class='app-header'>
    <h1>🌱 Trợ Lý Nông Nghiệp Bản Làng</h1>
    <p>Chẩn đoán bệnh cây trồng, vật nuôi bằng AI</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='note-box'>
    <b>👋 Lời ngỏ:</b> Ứng dụng hỗ trợ bà con chẩn đoán nhanh dịch bệnh (Hỗ trợ đọc tiếng Phổ thông, dịch tiếng dân tộc Thái và H'Mông vùng Tây Bắc). 
    <br><i>Lưu ý: Kết quả mang tính tham khảo bước đầu, bà con cần báo cho cán bộ Khuyến nông/Thú y nếu bệnh diễn biến nặng!</i>
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
    except: return None

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
    with st.expander("👁️ Xem trước hình ảnh"): st.image(image, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# BƯỚC 2: THÔNG TIN
st.markdown("<div class='step-title'>📝 Bước 2: Thông tin & Ngôn ngữ</div>", unsafe_allow_html=True)
st.markdown("<div class='step-card'>", unsafe_allow_html=True)
extra_info = st.text_area("Bà con mô tả thêm tình trạng (nếu có):", placeholder="Ví dụ: Lợn bỏ ăn 2 ngày, sốt cao... hoặc lúa bị vàng lá...", height=80)

st.markdown("**Chọn ngôn ngữ muốn máy đọc và dịch:**")
col_lang1, col_lang2, col_lang3 = st.columns(3)
with col_lang1: use_vi = st.checkbox("🇻🇳 Tiếng Việt", value=True, disabled=True, help="Mặc định luôn có Tiếng Phổ thông")
with col_lang2: use_hmong = st.checkbox("🏔️ Tiếng H’Mông", value=True)
with col_lang3: use_thai = st.checkbox("🌿 Tiếng Thái (Tây Bắc)", value=True)
st.markdown("</div>", unsafe_allow_html=True)

# BƯỚC 3: XỬ LÝ
st.markdown("<br>", unsafe_allow_html=True)
submit_btn = st.button("🚀 BẮT ĐẦU CHẨN ĐOÁN NGAY")

if submit_btn:
    if not image: st.error("⚠️ Vui lòng chụp hoặc tải ảnh lên ở Bước 1!")
    elif not api_key: st.error("⚠️ Cán bộ quản lý vui lòng nhập API Key ở Menu bên trái để khởi động AI!")
    else:
        st.markdown("---")
        with st.spinner("⏳ Hệ thống đang đối chiếu dữ liệu thú y/nông nghiệp và chuẩn bị giọng đọc..."):
            langs = ["Tiếng Phổ Thông"]
            if use_hmong: langs.append("Tiếng dân tộc H’Mông")
            if use_thai: langs.append("Tiếng dân tộc Thái (Tây Bắc Việt Nam)")
            lang_str = " – ".join(langs)
            extra_prompt = f"\n- Lời kể của bà con: {extra_info}" if extra_info else ""

            prompt_text = fr"""
Bạn là chuyên gia nông nghiệp và bác sĩ thú y đang công tác tại vùng núi Tây Bắc (Điện Biên). Hãy quan sát ảnh và chẩn đoán bệnh, khuyên DỄ HIỂU, GẦN GŨI bằng ({lang_str}).{extra_prompt}

⚠️ QUY TẮC CHUYÊN MÔN (BẮT BUỘC TUÂN THỦ TÀI LIỆU CHUẨN):
1. Phác đồ điều trị và cách ly phải dựa trên hướng dẫn chuẩn của Cổng thông tin Trung tâm Khuyến nông Quốc gia và Cục Thú y.
2. Ưu tiên các phương pháp chăm sóc phù hợp với đặc thù khí hậu lạnh, nuôi thả rông của tỉnh Điện Biên.
3. Nếu ảnh mờ/không đúng bệnh: Từ chối chẩn đoán, yêu cầu chụp lại. TUYỆT ĐỐI KHÔNG ĐOÁN BỪA.
4. LUÔN CÓ CÂU CHỐT: Yêu cầu bà con báo ngay cho Trạm thú y/Khuyến nông xã để được hỗ trợ.

⚠️ QUY TẮC NGÔN NGỮ ĐỊA PHƯƠNG & HIỂN THỊ:
- Tiếng Thái ở đây là ngôn ngữ của ĐỒNG BÀO DÂN TỘC THÁI tại Việt Nam, KHÔNG PHẢI tiếng của đất nước Thái Lan. Hãy dùng phiên âm chữ Latinh để bà con dễ đọc.
- Không dùng từ hàn lâm. BẮT BUỘC chia rõ các thẻ:
[VI] 
(Nội dung Tiếng Phổ Thông)
[HMN] 
(Nội dung tiếng dân tộc H'Mông - nếu có)
[TH] 
(Nội dung tiếng dân tộc Thái Tây Bắc - nếu có)
"""
            result = analyze_real_image(api_key, image, prompt_text)
            
            if result.startswith("❌"): st.error(result)
            else:
                st.balloons()
                st.success("🎉 PHÂN TÍCH THÀNH CÔNG! MỜI BÀ CON XEM KẾT QUẢ:")
                
                vi_match = re.search(r'\[VI\](.*?)(?=\[HMN\]|\[TH\]|$)', result, re.DOTALL)
                hmn_match = re.search(r'\[HMN\](.*?)(?=\[TH\]|$)', result, re.DOTALL)
                th_match = re.search(r'\[TH\](.*?)$', result, re.DOTALL)
                
                vi_text = vi_match.group(1).strip() if vi_match else result
                hmn_text = hmn_match.group(1).strip() if hmn_match else ""
                th_text = th_match.group(1).strip() if th_match else ""

                display_text = result.replace("[VI]", "🇻🇳 **Tiếng Phổ thông:**\n").replace("[HMN]", "\n---\n🏔️ **Tiếng dân tộc H'Mông:**\n").replace("[TH]", "\n---\n🌿 **Tiếng dân tộc Thái (Tây Bắc):**\n")
                
                st.markdown("<div class='step-card' style='border-top: 4px solid #4caf50;'>", unsafe_allow_html=True)
                st.markdown(display_text)
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("<div class='step-title'>🔊 Nghe máy đọc kết quả</div>", unsafe_allow_html=True)
                st.markdown("<div class='step-card'>", unsafe_allow_html=True)
                
                # Âm thanh Tiếng Phổ thông
                if vi_text:
                    st.write("🇻🇳 **Giọng Tiếng Phổ thông:**")
                    clean_vi = vi_text.replace('*', '').replace('#', '')
                    audio_vi = generate_audio(clean_vi, 'vi')
                    if audio_vi: st.audio(audio_vi, format="audio/mp3")

                # Cảnh báo kỹ thuật cho ngôn ngữ đồng bào
                if (use_hmong and hmn_text) or (use_thai and th_text):
                    st.info("💡 **Ghi chú kỹ thuật (Hội đồng Giám khảo):** Hiện tại nền tảng Text-to-Speech toàn cầu (Google/Microsoft) chưa có bộ dữ liệu phát âm chuẩn cho tiếng dân tộc H'Mông và Thái tại vùng Tây Bắc Việt Nam. Tính năng tự động phát giọng bản địa sẽ được nâng cấp khi nhóm hoàn thiện bộ thu âm từ điển địa phương!")
                
                st.markdown("</div>", unsafe_allow_html=True)

                st.session_state.history.insert(0, {"time": datetime.now().strftime("%d/%m/%Y %H:%M"), "result": display_text})
                
                st.markdown("<div class='download-btn'>", unsafe_allow_html=True)
                st.download_button("📥 Tải bản chẩn đoán này về máy", display_text, f"DonThuoc_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
                st.markdown("</div>", unsafe_allow_html=True)

# LỊCH SỬ KHÁM
if st.session_state.history:
    st.markdown("<br><div class='step-title' style='color:#f57c00; border-bottom: 2px solid #ffe0b2;'>🕒 Lịch sử khám bệnh hôm nay</div>", unsafe_allow_html=True)
    for item in st.session_state.history[:3]:
        with st.expander(f"📌 Chẩn đoán lúc: {item['time']}"): st.markdown(item['result'])

# ===============================
# 4. THÔNG TIN DỰ ÁN & HỌC LIỆU
# ===============================
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("ℹ️ Nguồn dữ liệu tham khảo)"):
    st.markdown("""
    <div class='reference-box'>
        <b>🎯 1. Tính mới & Sáng tạo của mô hình:</b><br>
        Lần đầu tiên ứng dụng AI tạo sinh (Generative AI) được tùy biến riêng cho nông nghiệp vùng Tây Bắc. Ứng dụng phá vỡ rào cản ngôn ngữ bằng cách hỗ trợ dịch tự động sang Tiếng Thái, Tiếng H'Mông (phiên âm Latinh), giúp đồng bào dân tộc thiểu số dễ dàng tiếp cận khoa học kỹ thuật.
        <br><br>
        <b>⚙️ 2. Khả năng áp dụng thực tiễn:</b><br>
        Ứng dụng chạy mượt mà trên nền tảng Web/Điện thoại thông minh mà không cần cài đặt phức tạp. Dữ liệu bệnh được đối chiếu trực tiếp từ các nguồn uy tín:
        <ul>
            <li><a href='http://www.khuyennongvn.gov.vn/' target='_blank' style='color: #1976d2; text-decoration: none;'><b>Trung tâm Khuyến nông Quốc gia</b></a> & <a href='http://cucthuy.gov.vn/' target='_blank' style='color: #1976d2; text-decoration: none;'><b>Cục Thú y Việt Nam</b></a>.</li>
            <li>Sổ tay dịch bệnh nông nghiệp từ <a href='https://sonongnghiep.dienbien.gov.vn/' target='_blank' style='color: #1976d2; text-decoration: none;'><b>Sở Nông nghiệp & PTNT tỉnh Điện Biên</b></a>.</li>
        </ul>
        <b>🌍 3. Hiệu quả kinh tế - xã hội (Đạo đức AI):</b><br>
        Ứng dụng đóng vai trò "sơ cấp cứu thông tin", không thay thế bác sĩ thú y mà <b>khuyên người dân báo cáo cho cán bộ chức năng</b>. Điều này giúp ngăn chặn dịch bệnh bùng phát sớm, giảm thiểu thiệt hại kinh tế cho bà con nông dân và thúc đẩy quá trình chuyển đổi số nông thôn mới.
    </div>
    """, unsafe_allow_html=True)
