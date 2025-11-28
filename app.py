import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 設定頁面 ---
st.set_page_config(page_title="Gemini 建築透視生成器", layout="wide")

# --- 側邊欄：API Key 設定 ---
with st.sidebar:
    st.header("🔑 系統設定")
    # 優先從 Secrets 讀取，如果沒有則顯示輸入框
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("已從系統讀取 API Key ✅")
    else:
        api_key = st.text_input("請輸入 Google API Key", type="password")
        st.markdown("[按這裡免費申請 API Key](https://aistudio.google.com/app/apikey)")
    
    if api_key:
        genai.configure(api_key=api_key)

# --- 核心邏輯：Gemini Prompt ---
def get_gemini_response(user_input, image_input=None):
    model = genai.GenerativeModel('gemini-1.5-pro') 
    
    system_instruction = """
    你是一位世界頂尖的建築視覺化專家。請將使用者的建築設計條件，轉化為一段「高品質、照片級真實」的英文圖像生成提示詞 (Prompt)。
    輸出格式範例："A photorealistic eye-level shot of a [Scale] story building, [Style], located in [Location], [Weather], featuring [Entourage]. 8k resolution, architectural photography."
    """
    
    prompt_parts = [system_instruction, user_input]
    if image_input:
        prompt_parts.append(image_input)
        
    response = model.generate_content(prompt_parts)
    return response.text

# --- 主介面 ---
st.title("🏗️ Gemini 建築透視圖生成介面")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. 設定參數")
    uploaded_file = st.file_uploader("上傳草圖 或 基地照片 (選填)", type=["jpg", "png", "jpeg"])
    image = None
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="已上傳參考圖", use_column_width=True)

    style = st.selectbox("建築風格", ["現代極簡", "清水模", "Zaha Hadid 流線", "日式禪風", "賽博龐克"])
    floors = st.slider("樓層數", 1, 50, 5)
    location = st.text_input("基地位置/氛圍", "台北市繁忙街頭")
    weather = st.radio("天氣", ["晴朗午後", "雨天倒影", "黃昏"])
    
    user_prompt = f"風格: {style}, 樓層: {floors}, 位置: {location}, 天氣: {weather}"

with col2:
    st.subheader("2. 生成結果")
    if st.button("🚀 生成 Prompt", type="primary"):
        if not api_key:
            st.warning("⚠️ 請先設定 API Key")
        else:
            with st.spinner('AI 正在思考...'):
                try:
                    result = get_gemini_response(user_prompt, image)
                    st.success("生成成功！請複製下方指令：")
                    st.code(result, language="bash")
                except Exception as e:
                    st.error(f"錯誤：{e}")
