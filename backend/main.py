from fastapi import FastAPI, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from gradio_client import Client, handle_file
import shutil
import os
import time

# FastAPI 앱 생성 (백엔드 서버 인스턴스)
app = FastAPI()

# -----------------------------------------------------------------------------
# 1. 서버 설정 (Configuration)
# -----------------------------------------------------------------------------
# 환경 변수에서 URL을 읽어오며, 없을 경우 기본값(localhost)을 사용합니다.
# 학교 서버 배포 등을 고려하여 주소를 동적으로 관리합니다.
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

print(f"🔧 서버 시작 설정: BASE_URL={BASE_URL}, FRONTEND_URL={FRONTEND_URL}")

# -----------------------------------------------------------------------------
# 2. CORS (Cross-Origin Resource Sharing) 보안 설정
# -----------------------------------------------------------------------------
# 프론트엔드(Next.js)에서 백엔드 API를 호출할 수 있도록 허용할 출처 목록입니다.
origins = [
    "http://localhost:3000",
    FRONTEND_URL, 
    "*" # 개발 편의를 위해 모든 출처 허용 (배포 시 주의 필요)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # 허용할 출처 목록
    allow_credentials=True,      # 쿠키/인증 정보 허용 여부
    allow_methods=["*"],         # 허용할 HTTP 메서드 (GET, POST 등)
    allow_headers=["*"],         # 허용할 HTTP 헤더
)

# -----------------------------------------------------------------------------
# 3. 정적 파일 호스팅 (Static Files)
# -----------------------------------------------------------------------------
# 의류 이미지(static)와 AI 결과 이미지(results)를 웹에서 접근 가능하게 만듭니다.

# 의류 이미지가 저장된 폴더 연결
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 피팅 결과 이미지가 저장될 폴더 연결
RESULT_DIR = "results"
os.makedirs(RESULT_DIR, exist_ok=True)
app.mount("/results", StaticFiles(directory=RESULT_DIR), name="results")

from urllib.parse import quote

# -----------------------------------------------------------------------------
# 4. 상품 데이터베이스 (Mock Database)
# -----------------------------------------------------------------------------
# 실제 DB 대신 리스트를 사용하여 상품 정보를 관리합니다.
# 'file_name'은 static 폴더 내의 실제 이미지 파일명을 가리킵니다.
RAW_PRODUCTS = [
    {"id": "hoodie_basic", "name": "베이직 오버핏 후드 (그레이)", "price": 89000, "file_name": "hoodie.png", "category": "Top"},
    {"id": "jacket_minimal", "name": "미니멀 울 자켓 (블랙)", "price": 189000, "file_name": "jacket.png", "category": "Outer"},
    {"id": "shirt_check", "name": "클래식 체크 셔츠 (블루)", "price": 65000, "file_name": "shirt.png", "category": "Top"},
    {"id": "mtm_navy", "name": "데일리 시그니처 맨투맨 (네이비)", "price": 59000, "file_name": "맨투맨1.jpg", "category": "Top"},
    {"id": "mtm_graphic", "name": "어반 그래픽 맨투맨", "price": 62000, "file_name": "맨투맨2.jpg", "category": "Top"},
    {"id": "shirt_stripe", "name": "오피스 스트라이프 셔츠", "price": 49000, "file_name": "셔츠1.jpg", "category": "Top"},
    {"id": "shirt_denim", "name": "빈티지 워싱 데님 셔츠", "price": 72000, "file_name": "셔츠2.jpg", "category": "Top"},
    {"id": "shirt_oxford", "name": "프리미엄 옥스포드 셔츠", "price": 55000, "file_name": "셔츠3.jpg", "category": "Top"},
    {"id": "sweater_knit", "name": "케이블 니트 스웨터 (아이보리)", "price": 85000, "file_name": "스웨터1.jpg", "category": "Top"},
    {"id": "jacket_daily", "name": "모던 데일리 블레이저", "price": 159000, "file_name": "자켓1.jpg", "category": "Outer"},
    {"id": "puffer_warm", "name": "윈터 헤비 숏패딩", "price": 239000, "file_name": "패딩1.jpg", "category": "Outer"},
]

@app.get("/api/products")
async def get_products():
    """
    상품 목록 API
    프론트엔드에 상품 정보와 이미지 전체 URL을 반환합니다.
    """
    products_with_urls = []
    for p in RAW_PRODUCTS:
        # 한글 파일명 등 특수문자가 포함된 URL을 안전하게 변환 (quote 사용)
        encoded_filename = quote(p['file_name'])
        products_with_urls.append({
            "id": p["id"],
            "name": p["name"],
            "price": p["price"],
            "image": f"{BASE_URL}/static/{encoded_filename}", # 웹 접근 가능한 전체 URL 생성
            "category": p["category"]
        })
    return products_with_urls

# -----------------------------------------------------------------------------
# 5. 가상 피팅 API (Virtual Try-On Core Logic)
# -----------------------------------------------------------------------------
@app.post("/api/try-on")
async def try_on(
    product_id: str = Form(...),          # 입어볼 상품의 ID
    person_image: UploadFile = File(...), # 사용자가 업로드한 전신 사진
    seed: int = Form(42),                 # 생성 결과 고정을 위한 시드값
    steps: int = Form(30)                 # AI 생성 단계 수 (높을수록 품질 증가, 속도 저하)
):
    print(f"👕 피팅 요청 수신: 상품ID={product_id}, 시드={seed}")
    
    # [1단계] 사용자 이미지 임시 저장
    # AI 모델에 파일을 전달하기 위해 잠시 서버 디스크에 저장합니다.
    try:
        temp_person_path = f"temp_{int(time.time())}_{person_image.filename}"
        with open(temp_person_path, "wb") as buffer:
            shutil.copyfileobj(person_image.file, buffer)
            
        # [2단계] 입힐 옷 이미지 찾기
        # 요청된 product_id에 해당하는 상품 정보를 데이터베이스에서 찾습니다.
        target_product = next((p for p in RAW_PRODUCTS if p["id"] == product_id), None)
        
        if not target_product:
            return {"error": "존재하지 않는 상품 ID입니다."}
            
        cloth_filename = target_product["file_name"]
        cloth_path = os.path.join("static", cloth_filename)
        
        # 파일 존재 여부 확인 (안전장치)
        if not os.path.exists(cloth_path):
             print(f"❌ 서버 오류: 옷 이미지 파일을 찾을 수 없음 - {cloth_path}")
             return {"error": f"관리자에게 문의하세요 (이미지 누락): {cloth_filename}"}

        # [3단계] AI 모델 호출 (Gradio Client)
        # HuggingFace의 yisol/IDM-VTON 모델을 사용하여 피팅을 수행합니다.
        # os.getenv 대신 직접 토큰을 문자열로 넣습니다.
        hf_token = os.getenv("HF_TOKEN")
        print(f"🚀 AI 모델에 요청 전송 중... (토큰 사용 여부: {'O' if hf_token else 'X'})")
        
        # hf_token이 있으면 인증된 클라이언트로, 없으면 공용(익명)으로 연결됩니다.
        client = Client("yisol/IDM-VTON", token=hf_token)
        
        result = client.predict(
            # [입력 1] 사용자 정보 (배경 이미지, 마스크 등)
            dict={"background": handle_file(temp_person_path), "layers": [], "composite": None},
            
            # [입력 2] 입힐 옷 이미지
            garm_img=handle_file(cloth_path),
            
            # [프롬프트] 옷에 대한 텍스트 설명
            garment_des="A cool fashion item",
            
            # [옵션] 자동 마스킹 및 크롭 설정
            is_checked=True,        # True: 자동으로 옷 영역을 감지하여 입힘
            is_checked_crop=False,  # False: 이미지 전체를 사용 (크롭 안함)
            
            # [파라미터] 생성 품질 설정
            denoise_steps=steps,
            seed=seed,
            
            # 호출할 API 경로명
            api_name="/tryon"
        )
        
        # [4단계] 결과 처리
        print("✅ AI 피팅 완료")
        # 결과는 파일 경로 리스트 또는 단일 경로로 반환됨
        final_path = result[0] if isinstance(result, (list, tuple)) else result
        
        # 결과를 웹 서빙 폴더(results)로 이동
        output_filename = f"result_{int(time.time())}.webp"
        output_path = os.path.join(RESULT_DIR, output_filename)
        shutil.move(final_path, output_path)
        
        # [5단계] 뒷정리 (임시 파일 삭제)
        if os.path.exists(temp_person_path):
            os.remove(temp_person_path)
        
        # 클라이언트에게 결과 URL 반환
        return {
            "success": True, 
            "result_url": f"{BASE_URL}/results/{output_filename}"
        }

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    # 0.0.0.0으로 호스팅하여 외부 접근(또는 같은 네트워크 접근)을 허용합니다.
    uvicorn.run(app, host="0.0.0.0", port=8000)
