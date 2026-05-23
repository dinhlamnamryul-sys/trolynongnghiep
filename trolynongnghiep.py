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
st.set_page_config(page_title="Trợ Lý Nông Nghiệp Bản Làng", page_icon="🌱", layout="centered", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Be Vietnam Pro', sans-serif !important; }

    .app-header { background: linear-gradient(135deg, #1b5e20 0%, #4caf50 100%); padding: 25px 15px; border-radius: 16px; color: white; text-align: center; box-shadow: 0 4px 15px rgba(46, 125, 50, 0.3); margin-bottom: 20px; }
    .app-header h1 { color: white !important; font-weight: 800; font-size: 32px; margin: 0; padding: 0; line-height: 1.2; }
    .app-header p { font-size: 16px; font-weight: 500; opacity: 0.9; margin-top: 5px; margin-bottom: 0; }

    .rag-status { background-color: #e8f5e9; border-left: 5px solid #2e7d32; padding: 10px 15px; border-radius: 8px; font-size: 14px; font-weight: 600; color: #1b5e20; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center;}
    .note-box { background-color: #fff9e6; border: 1px solid #ffe082; border-left: 6px solid #ffb300; padding: 18px; border-radius: 12px; color: #5c4000; font-size: 15px; line-height: 1.6; margin-bottom: 25px; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }

    .step-card { background-color: white; border: 1px solid #e0e0e0; border-radius: 16px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.03); }
    .step-title { color: #1b5e20; font-weight: 700; font-size: 19px; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; border-bottom: 2px solid #f1f8e9; padding-bottom: 10px; }

    .stButton>button { background: linear-gradient(to right, #f57c00, #ff9800) !important; color: white !important; border-radius: 50px !important; font-weight: 700 !important; font-size: 18px !important; padding: 12px 0 !important; border: none !important; box-shadow: 0 6px 15px rgba(245, 124, 0, 0.3) !important; transition: all 0.3s ease !important; }
    .stButton>button:hover { transform: translateY(-3px) !important; box-shadow: 0 8px 20px rgba(245, 124, 0, 0.4) !important; }
    .download-btn>button { background: linear-gradient(to right, #0277bd, #039be5) !important; box-shadow: 0 6px 15px rgba(2, 119, 189, 0.3) !important; }
    
    .reference-box { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 4px solid #1976d2; font-size: 14px; line-height: 1.5; color: #333;}
    </style>
""", unsafe_allow_html=True)

if "history" not in st.session_state: st.session_state.history = []

# =====================
# 2. CƠ SỞ DỮ LIỆU RAG (ĐƯỢC CẤU TRÚC LẠI THEO CHUẨN THÚ Y)
# =====================
RAG_KNOWLEDGE_BASE = """
[QUY TRÌNH XỬ LÝ DỊCH BỆNH CHUẨN - CHI CỤC THÚ Y & BVTV]
* NGUYÊN TẮC CHUNG: "Phát hiện sớm - Cách ly ngay - Xử lý dứt điểm - Báo cáo nhanh".

1. BỆNH DỊCH TẢ LỢN CHÂU PHI (ASF):
- Triệu chứng lâm sàng: Sốt cao, xuất huyết lốm đốm đỏ/tím ở tai, mõm, bẹn. Lợn ủ rũ, bỏ ăn. Tỷ lệ chết 100%.
- Phác đồ: KHÔNG CÓ THUỐC CHỮA.
- Xử lý 4 bước: (1) Cách ly tuyệt đối con ốm; (2) Không bán chạy, không mổ thịt; (3) Báo ngay trạm thú y xã để tiêu hủy chôn lấp với vôi bột; (4) Rắc vôi bột, phun sát trùng toàn bộ chuồng trại liên tục 7 ngày.

2. BỆNH LỞ MỒM LONG MÓNG (Trâu/Bò/Lợn):
- Triệu chứng lâm sàng: Sốt, nổi mụn nước ở niêm mạc miệng, vành móng, vú. Chảy dãi nhiều, đi lại khó khăn.
- Phác đồ & Xử lý: (1) Cách ly khỏi đàn khỏe; (2) Xử lý vết thương: Rửa bằng dung dịch phèn chua 2%, cồn I-ốt hoặc nước chanh, khế. Bôi thuốc Xanh Methylene; (3) Dinh dưỡng: Cho ăn thức ăn mềm (cháo loãng), bổ sung Vitamin C tăng đề kháng; (4) Báo cáo kiểm dịch.

3. BỆNH TỤ HUYẾT TRÙNG (Lợn/Gia cầm):
- Triệu chứng lâm sàng: Bệnh ghép, khó thở, tụ huyết thâm tím ở vùng hầu họng, tích nước. Phân lỏng.
- Phác đồ & Xử lý: (1) Cách ly; (2) Tiêm kháng sinh Enrofloxacin 10% hoặc Amoxicillin kết hợp thuốc trợ lực Vitamin B-Complex; (3) Tiêu độc sát trùng chuồng trại; (4) Khuyên tiêm phòng vaccine định kỳ cho toàn đàn.

4. BỆNH ĐẠO ÔN TRÊN LÚA (Bảo vệ thực vật):
- Triệu chứng lâm sàng: Lá lúa xuất hiện vết chấm nhỏ, sau lan rộng hình thoi (mắt én), tâm màu xám tro, viền nâu đậm.
- Phác đồ & Xử lý: (1) Lập tức ngừng bón phân đạm (Urê); (2) Giữ mực nước trong ruộng; (3) Phun thuốc đặc trị có hoạt chất Tricyclazole hoặc Isoprothiolane. Phun 2 lần cách nhau 5-7 ngày.
"""

# =====================
# 3. MENU CÀI ĐẶT ẨN
# =====================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/862/862856.png", width=60)
    st.markdown("### ⚙️ Cài đặt Quản trị")
    api_key = st.text_input("🔑 Google API Key:", type="password")
    
    with st.expander("👉 Hướng dẫn lấy mã API Key"):
        st.markdown("""
        1. Truy cập: <a href="https://aistudio.google.com/app/apikey" target="_blank"><b>Google AI Studio</b></a>.
        2. Đăng nhập Gmail -> <b>Create API key</b>.
        3. Copy mã dán vào ô trên.
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown("<b>Dự án dự thi Sáng tạo TTN-NĐ 2026</b><br>Đơn vị: TP. Điện Biên Phủ", unsafe_allow_html=True)

# =====================
# 4. HEADER & GIAO DIỆN CHÍNH
# =====================
st.markdown("""
<div class='app-header'>
    <h1>🌱 Trợ Lý Nông Nghiệp Bản Làng</h1>
    <p>Chẩn đoán dịch bệnh & Phác đồ xử lý chuẩn</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='rag-status'>
    <span>🟢 CSDL RAG: Đã đồng bộ Phác đồ chuẩn Thú y/BVTV 2026</span>
    <span>Bảo mật: Xác thực</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='note-box'>
    <b>👋 Lời ngỏ:</b> Ứng dụng hỗ trợ bà con chẩn đoán nhanh dịch bệnh (Phát âm Phổ thông, dịch tiếng Thái và H'Mông). 
    <br><i>Lưu ý: Phác đồ chỉ mang tính chất sơ cứu, bà con cần báo cho cán bộ chuyên môn để được can thiệp sâu!</i>
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
st.markdown("<div class='step-title'>📸 Bước 1: Cung cấp hình ảnh & Triệu chứng</div>", unsafe_allow_html=True)
st.markdown("<div class='step-card'>", unsafe_allow_html=True)
tab1, tab2 = st.tabs(["📷 Chụp ảnh trực tiếp", "🖼️ Tải ảnh từ thư viện"])
photo, upload = None, None
with tab1: photo = st.camera_input("Bấm vào đây để mở Camera:")
with tab2: upload = st.file_uploader("Bấm để chọn ảnh có sẵn:", type=["png", "jpg", "jpeg"])
image = None
if photo: image = Image.open(photo)
elif upload: image = Image.open(upload)
if image:
    st.success("✅ Ảnh đã được trích xuất dữ liệu thành công!")
    with st.expander("👁️ Xem trước hình ảnh"): st.image(image, use_container_width=True)

extra_info = st.text_area("Bà con mô tả thêm tình trạng lâm sàng (nếu có):", placeholder="Ví dụ: Bỏ ăn 2 ngày, sốt cao, đi ngoài phân lỏng...", height=80)
st.markdown("</div>", unsafe_allow_html=True)

# BƯỚC 2: NGÔN NGỮ ĐỊA PHƯƠNG
st.markdown("<div class='step-title'>📝 Bước 2: Chọn ngôn ngữ hỗ trợ</div>", unsafe_allow_html=True)
st.markdown("<div class='step-card'>", unsafe_allow_html=True)
col_lang1, col_lang2, col_lang3 = st.columns(3)
with col_lang1: use_vi = st.checkbox("🇻🇳 Tiếng Việt", value=True, disabled=True)
with col_lang2: use_hmong = st.checkbox("🏔️ Tiếng H’Mông", value=True)
with col_lang3: use_thai = st.checkbox("🌿 Tiếng Thái (Tây Bắc)", value=True)
st.markdown("</div>", unsafe_allow_html=True)

# BƯỚC 3: XỬ LÝ RAG & CHẨN ĐOÁN CHUYÊN MÔN
st.markdown("<br>", unsafe_allow_html=True)
submit_btn = st.button("🚀 PHÂN TÍCH & TRÍCH XUẤT PHÁC ĐỒ CHUẨN")

if submit_btn:
    if not image: st.error("⚠️ Vui lòng cung cấp hình ảnh ở Bước 1!")
    elif not api_key: st.error("⚠️ Lỗi hệ thống: Chưa nhập API Key ở Menu!")
    else:
        st.markdown("---")
        with st.spinner("⏳ Đang quét dấu hiệu lâm sàng và đối chiếu với CSDL Y tế/Nông nghiệp Điện Biên..."):
            langs = ["Tiếng Phổ Thông"]
            if use_hmong: langs.append("Tiếng dân tộc H’Mông")
            if use_thai: langs.append("Tiếng dân tộc Thái (Tây Bắc Việt Nam)")
            lang_str = " – ".join(langs)
            extra_prompt = f"\n- Lời kể lâm sàng của bà con: {extra_info}" if extra_info else ""

            # PROMPT CHUYÊN GIA: Ép AI trả lời theo cấu trúc y khoa chuẩn
            prompt_text = fr"""
Bạn là một kỹ sư nông nghiệp và bác sĩ thú y giàu kinh nghiệm. Hãy phân tích ảnh và triệu chứng để lập hồ sơ bệnh án.

[TÀI LIỆU KIỂM CHỨNG - KNOWLEDGE BASE]
{RAG_KNOWLEDGE_BASE}
[/KẾT THÚC TÀI LIỆU]

⚠️ QUY TẮC RAG & TRÌNH BÀY (BẮT BUỘC):
1. Bạn PHẢI đối chiếu với [TÀI LIỆU KIỂM CHỨNG] và trả lời chính xác theo cấu trúc 4 phần sau cho mỗi ngôn ngữ:
   - 🔍 **Dấu hiệu nhận biết:** (Bạn thấy gì từ ảnh và lời kể?)
   - 🩺 **Chẩn đoán sơ bộ:** (Kết luận tên bệnh/vấn đề là gì?)
   - 📋 **Phác đồ xử lý chuẩn:** (Viết rõ từng bước: Cách ly/Vệ sinh môi trường -> Can thiệp y tế/Dùng thuốc -> Chăm sóc phục hồi dựa trên tài liệu chuẩn).
   - 🚨 **Khuyến cáo dịch tễ:** (Bắt buộc dặn báo cáo cán bộ địa phương).
2. Tuyệt đối không tự bịa ra tên thuốc kháng sinh ngoài danh mục trên. Nếu không rõ bệnh, hãy yêu cầu báo ngay cán bộ.
3. Văn phong dễ hiểu, gần gũi với bà con bản làng. Dịch ra ({lang_str}). Dùng phiên âm Latinh cho tiếng dân tộc.{extra_prompt}

⚠️ BẮT BUỘC CHIA THẺ ĐỂ CẮT LỚP ÂM THANH:
[VI] 
(Nội dung Tiếng Phổ Thông theo cấu trúc 4 phần)
[HMN] 
(Nội dung Tiếng H'Mông - nếu có)
[TH] 
(Nội dung Tiếng Thái Tây Bắc - nếu có)
"""
            result = analyze_real_image(api_key, image, prompt_text)
            
            if result.startswith("❌"): st.error(result)
            else:
                st.balloons()
                st.success("🎉 HỒ SƠ BỆNH ÁN SƠ BỘ ĐÃ ĐƯỢC THIẾT LẬP:")
                
                vi_match = re.search(r'\[VI\](.*?)(?=\[HMN\]|\[TH\]|$)', result, re.DOTALL)
                hmn_match = re.search(r'\[HMN\](.*?)(?=\[TH\]|$)', result, re.DOTALL)
                th_match = re.search(r'\[TH\](.*?)$', result, re.DOTALL)
                
                vi_text = vi_match.group(1).strip() if vi_match else result
                hmn_text = hmn_match.group(1).strip() if hmn_match else ""
                th_text = th_match.group(1).strip() if th_match else ""

                display_text = result.replace("[VI]", "🇻🇳 **HỒ SƠ TIẾNG PHỔ THÔNG:**\n").replace("[HMN]", "\n---\n🏔️ **HỒ SƠ TIẾNG H'MÔNG:**\n").replace("[TH]", "\n---\n🌿 **HỒ SƠ TIẾNG THÁI (TÂY BẮC):**\n")
                
                st.markdown("<div class='step-card' style='border-top: 4px solid #4caf50;'>", unsafe_allow_html=True)
                st.markdown(display_text)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # NÚT GỌI ĐIỆN THOẠI KHẨN CẤP
                st.markdown("<div class='step-title' style='color:#c62828; border-bottom: 2px solid #ffcdd2;'>📞 Báo cáo Cán bộ Thú y/Khuyến nông Khẩn cấp</div>", unsafe_allow_html=True)
                st.markdown("<div class='step-card' style='background-color: #ffebee;'>", unsafe_allow_html=True)
                st.markdown("Chọn địa bàn để lấy số liên hệ cán bộ phụ trách (Bản Demo):")
                dia_phuong = st.selectbox("Chọn địa phương:", 
                                         ["Phường Mường Thanh", "Xã Thanh Xương", "Xã Mường Phăng"], label_visibility="collapsed")
                
                if dia_phuong == "Phường Mường Thanh":
                    st.markdown("👨‍⚕️ Cán bộ: **Nguyễn Văn A** | 📞 **0912.345.678**")
                    st.markdown("<a href='tel:0912345678'><button style='background-color:#c62828; color:white; padding:8px 15px; border-radius:8px; border:none; font-weight:bold; width:100%;'>☎ Bấm để gọi cấp cứu nông nghiệp</button></a>", unsafe_allow_html=True)
                elif dia_phuong == "Xã Thanh Xương":
                    st.markdown("👨‍⚕️ Cán bộ: **Lò Văn B** | 📞 **0988.777.666**")
                    st.markdown("<a href='tel:0988777666'><button style='background-color:#c62828; color:white; padding:8px 15px; border-radius:8px; border:none; font-weight:bold; width:100%;'>☎ Bấm để gọi cấp cứu nông nghiệp</button></a>", unsafe_allow_html=True)
                else:
                    st.markdown("👩‍⚕️ Cán bộ: **Lường Thị C** | 📞 **0215.3123.456**")
                    st.markdown("<a href='tel:02153123456'><button style='background-color:#c62828; color:white; padding:8px 15px; border-radius:8px; border:none; font-weight:bold; width:100%;'>☎ Bấm để gọi cấp cứu nông nghiệp</button></a>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("<div class='step-title'>🔊 Nghe máy đọc phác đồ</div>", unsafe_allow_html=True)
                st.markdown("<div class='step-card'>", unsafe_allow_html=True)
                
                if vi_text:
                    st.write("🇻🇳 **Giọng Tiếng Phổ thông:**")
                    clean_vi = vi_text.replace('*', '').replace('#', '').replace('🔍', '').replace('🩺', '').replace('📋', '').replace('🚨', '')
                    audio_vi = generate_audio(clean_vi, 'vi')
                    if audio_vi: st.audio(audio_vi, format="audio/mp3")

                if (use_hmong and hmn_text) or (use_thai and th_text):
                    st.info("💡 **Ghi chú kỹ thuật:** Nền tảng phát âm thanh AI hiện chưa có bộ dữ liệu giọng H'Mông/Thái (Tây Bắc). Tính năng tự động phát giọng bản địa sẽ được nâng cấp khi nhóm hoàn thiện bộ thu âm từ điển địa phương!")
                
                st.markdown("</div>", unsafe_allow_html=True)

                st.session_state.history.insert(0, {"time": datetime.now().strftime("%d/%m/%Y %H:%M"), "result": display_text})
                
                st.markdown("<div class='download-btn'>", unsafe_allow_html=True)
                st.download_button("📥 Tải Hồ sơ Bệnh án Sơ bộ (Định dạng File Text)", display_text, f"HoSoBenh_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
                st.markdown("</div>", unsafe_allow_html=True)

# LỊCH SỬ KHÁM
if st.session_state.history:
    st.markdown("<br><div class='step-title' style='color:#f57c00; border-bottom: 2px solid #ffe0b2;'>🕒 Nhật ký quét bệnh lưu trên máy</div>", unsafe_allow_html=True)
    for item in st.session_state.history[:3]:
        with st.expander(f"📌 Chẩn đoán lúc: {item['time']}"): st.markdown(item['result'])

# ===============================
# 5. THÔNG TIN DỰ ÁN & RAG INFO
# ===============================
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("ℹ️ Tuyên bố Kỹ thuật & Đạo đức AI (Dành cho Hội đồng Giám khảo)"):
    st.markdown("""
    <div class='reference-box'>
        <b>🔬 1. Công nghệ Lõi - Hệ thống RAG (Retrieval-Augmented Generation):</b><br>
        Để giải quyết triệt để vấn đề "Ảo giác AI" (Hallucination - AI tự bịa thông tin y khoa), dự án áp dụng kỹ thuật RAG và Prompt Engineering nghiêm ngặt: 
        <ul>
            <li>Hệ thống được tích hợp sẵn <b>Cơ sở dữ liệu (Knowledge Base)</b> mô phỏng các phác đồ từ <i>Cục Thú y</i>.</li>
            <li>Khi nhận dữ liệu, AI <b>bắt buộc phải xuất ra hồ sơ theo chuẩn 4 phần</b> (Dấu hiệu -> Chẩn đoán -> Phác đồ chuẩn -> Khuyến cáo). Nếu bệnh không có trong danh mục, AI từ chối bốc thuốc.</li>
        </ul>
        <b>🚀 2. Chuỗi hành động khép kín (Closed-loop Action):</b><br>
        Ứng dụng không chỉ dừng ở việc "tra cứu". Chúng em thiết kế quy trình khép kín: <i>Phát hiện bệnh -> Hướng dẫn cách ly -> <b>Cung cấp phím gọi khẩn cấp</b> cho đúng trạm thú y địa bàn</i>.
        <br><br>
        <b>🛡️ 3. Đạo đức AI (AI Ethics):</b><br>
        Ứng dụng được định vị là <b>Trợ lý sơ cấp cứu thông tin</b>, bảo vệ nông dân vùng cao khỏi các lời khuyên trôi nổi, xóa bỏ rào cản ngôn ngữ bằng tiếng địa phương, tuân thủ tuyệt đối quy định quản lý dịch tễ của Tỉnh Điện Biên.
    </div>
    """, unsafe_allow_html=True)
