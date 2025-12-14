import streamlit as st
import os
import shutil
import time
from gradio_client import Client, handle_file
from PIL import Image

# --- 1. Page Configuration & CSS ---
st.set_page_config(layout="wide", page_title="Musinsa AI Studio", page_icon="👕")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    .block-container {
        padding-top: 2rem;
    }
    
    /* Header Styles */
    h1, h2, h3 {
        font-weight: 700 !important;
        color: #000000;
    }
    
    /* Product Card Style */
    .product-card {
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        transition: 0.3s;
        height: 100%;
    }
    .product-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .product-img {
        width: 100%;
        height: 250px;
        object-fit: cover;
        border-radius: 4px;
        margin-bottom: 10px;
    }
    .product-name {
        font-size: 1.1rem;
        font-weight: bold;
        margin: 10px 0 5px 0;
    }
    .product-price {
        color: #555;
        font-size: 1rem;
        margin-bottom: 15px;
    }

    /* Detail Page Styles */
    .price-tag {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 2rem;
    }
    
    /* Button Override */
    .stButton button {
        width: 100%;
        border-radius: 0px;
        font-weight: bold;
        padding: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. State & Data ---

# Mock Products
PRODUCTS = [
    {"id": 1, "name": "24FW 오버핏 비건 레더 자켓", "price": "128,000", "img": "cloth.jpg", "category": "Outer"},
    {"id": 2, "name": "미니멀 울 블레이저 (Black)", "price": "215,000", "img": "cloth.jpg", "category": "Outer"}, # Demo: same img
    {"id": 3, "name": "캐시미어 블렌드 코트", "price": "349,000", "img": "cloth.jpg", "category": "Outer"},     # Demo: same img
]

# Session Initialization
if 'page' not in st.session_state:
    st.session_state['page'] = 'home'
if 'selected_product' not in st.session_state:
    st.session_state['selected_product'] = None
if 'result_image_path' not in st.session_state:
    st.session_state['result_image_path'] = None
if 'person_up_key' not in st.session_state:
    st.session_state['person_up_key'] = str(time.time())

# Client Cache
@st.cache_resource
def load_client():
    return Client("yisol/IDM-VTON")

# --- 3. Navigation Functions ---
def go_to_detail(product):
    st.session_state['selected_product'] = product
    st.session_state['page'] = 'detail'
    # Clear previous result when switching products
    st.session_state['result_image_path'] = None
    st.rerun()

def go_to_home():
    st.session_state['page'] = 'home'
    st.rerun()

# --- 4. Logic Functions ---
def try_on(product, person_file, seed, steps):
    if not person_file:
        st.error("❌ 사람 사진을 업로드해주세요!")
        return

    with st.spinner("🧵 AI가 옷을 피팅중입니다..."):
        try:
            temp_dir = "temp_uploads"
            os.makedirs(temp_dir, exist_ok=True)
            
            # Save person image
            p_path = os.path.join(temp_dir, f"person_{int(time.time())}.jpg")
            with open(p_path, "wb") as f:
                f.write(person_file.getbuffer())
            
            # Use Product Image
            # For demo, using local 'cloth.jpg' (or product['img'])
            # In real app, product['img'] would be a path.
            c_path = product['img'] 
            if not os.path.exists(c_path):
                # Fallback if specific file missing
                c_path = "cloth.jpg"

            # Predict
            client = load_client()
            result = client.predict(
                dict={"background": handle_file(p_path), "layers": [], "composite": None},
                garm_img=handle_file(c_path),
                garment_des="Hello!!",
                is_checked=True,
                is_checked_crop=False,
                denoise_steps=steps,
                seed=seed,
                api_name="/tryon"
            )
            
            # Save Result
            final_path = result[0] if isinstance(result, (list, tuple)) else result
            save_dir = r"D:\antigravity\pro\result"
            os.makedirs(save_dir, exist_ok=True)
            new_filename = f"on_{product['id']}_{int(time.time())}.webp"
            saved_path = os.path.join(save_dir, new_filename)
            shutil.move(final_path, saved_path)
            
            st.session_state['result_image_path'] = saved_path
            st.success("피팅 완료!")
            
        except Exception as e:
            st.error(f"오류 발생: {e}")

# --- 5. Page Rendering ---

def render_home():
    st.title("MUSINSA AI STUDIO")
    st.write("당신의 스타일을 AI로 완성하세요.")
    st.markdown("---")
    
    st.subheader("🔥 New Arrivals")
    
    cols = st.columns(3)
    for i, product in enumerate(PRODUCTS):
        with cols[i % 3]:
            # Simple Card Layout using container
            with st.container(border=True):
                # Image
                if os.path.exists(product['img']):
                     st.image(product['img'], use_container_width=True)
                else:
                     st.text("이미지 없음")
                
                st.markdown(f"**{product['name']}**")
                st.markdown(f"<p style='color:grey'>{product['price']} KRW</p>", unsafe_allow_html=True)
                
                if st.button("상세보기 & 피팅", key=f"btn_{product['id']}"):
                    go_to_detail(product)

def render_detail():
    product = st.session_state['selected_product']
    if not product:
        go_to_home()
        return

    # Navigation Bar
    col_nav, _ = st.columns([1, 5])
    with col_nav:
        if st.button("⬅ 목록으로 (Back)"):
            go_to_home()

    st.markdown("---")

    # Layout: [1, 1] as requested
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        # Display Result or Default
        if st.session_state['result_image_path']:
            st.image(st.session_state['result_image_path'], caption="✨ AI Fitting Result", use_container_width=True)
        else:
            # Show person upload preview if available
            # Note: File uploader in right col, but we can't easily display it here instantly without extra trick.
            # We'll use a placeholder or the product image as "Model" if no person uploaded.
            
            # Actually, standard UX: Left shows the Product on a Model.
            st.image(product['img'], caption="Original Product Look", use_container_width=True)


    with col_right:
        # Info
        st.markdown(f"## {product['name']}")
        st.markdown(f'<div class="price-tag">{product["price"]} KRW</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1: st.button("바로 구매하기", type="primary")
        with c2: st.button("장바구니 담기")

        st.markdown("---")
        
        # Try-On Panel
        st.markdown("### 🔹 Virtual Try-On")
        st.info(f"선택된 상품: {product['name']}")
        
        # Only Person Uploader needed
        person_file = st.file_uploader("피팅 모델 사진 (내 사진)", type=['jpg', 'png', 'webp'])
        
        with st.expander("상세 설정 (Advanced)"):
            seed_val = st.slider("Seed", 0, 1000, 42)
            steps_val = st.slider("Quality Steps", 10, 50, 30)

        if st.button("✨ 이 옷 입어보기 (Try On)", type="primary"):
            try_on(product, person_file, seed_val, steps_val)
            st.rerun()


# --- Main Router ---
if st.session_state['page'] == 'home':
    render_home()
else:
    render_detail()

