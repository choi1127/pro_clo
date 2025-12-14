from fastapi import FastAPI, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from gradio_client import Client, handle_file
import shutil
import os
import time

app = FastAPI()

# Configuration
# Default to localhost for local dev, but allow override via env var
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

print(f"🔧 Server Config: BASE_URL={BASE_URL}, FRONTEND_URL={FRONTEND_URL}")

# CORS
origins = [
    "http://localhost:3000",
    FRONTEND_URL, 
    # Add your school server IP/Domain here later if needed, e.g. "http://111.222.33.44:3000"
    "*" # For development simplicity, allowing all. In production, be more specific.
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# mount static files for serving product images
# Ensure the directory exists
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Result Directory
RESULT_DIR = "results"
os.makedirs(RESULT_DIR, exist_ok=True)
app.mount("/results", StaticFiles(directory=RESULT_DIR), name="results")

# Mock Products
# Use BASE_URL to generate full image paths
PRODUCTS = [
    {"id": "jacket", "name": "Minimal Wool Jacket (Black)", "price": 189000, "image": f"{BASE_URL}/static/jacket.png", "category": "Outer"},
    {"id": "hoodie", "name": "Oversized Hoodie (Gray)", "price": 89000, "image": f"{BASE_URL}/static/hoodie.png", "category": "Top"},
    {"id": "shirt", "name": "Checkered Flannel Shirt (Blue)", "price": 65000, "image": f"{BASE_URL}/static/shirt.png", "category": "Top"},
]

@app.get("/api/products")
async def get_products():
    return PRODUCTS

@app.post("/api/try-on")
async def try_on(
    product_id: str = Form(...),
    person_image: UploadFile = File(...),
    seed: int = Form(42),
    steps: int = Form(30)
):
    print(f"👕 Request received: {product_id}, Seed: {seed}")
    
    # 1. Save uploaded person image
    try:
        temp_person_path = f"temp_{int(time.time())}_{person_image.filename}"
        with open(temp_person_path, "wb") as buffer:
            shutil.copyfileobj(person_image.file, buffer)
            
        # 2. Identify Product Image
        # In a real app, this would be a database lookup.
        # Here we map ID to local file.
        cloth_map = {
            "jacket": "static/jacket.png",
            "hoodie": "static/hoodie.png",
            "shirt": "static/shirt.png"
        }
        
        cloth_path = cloth_map.get(product_id)
        if not cloth_path or not os.path.exists(cloth_path):
             return {"error": "Product image not found"}

        # 3. Call Gradio Client
        print("🚀 Calling AI Client...")
        client = Client("yisol/IDM-VTON")
        result = client.predict(
            dict={"background": handle_file(temp_person_path), "layers": [], "composite": None},
            garm_img=handle_file(cloth_path),
            garment_des="A cool fashion item",
            is_checked=True,
            is_checked_crop=False,
            denoise_steps=steps,
            seed=seed,
            api_name="/tryon"
        )
        
        # 4. Handle Result
        print("✅ Prediction complete")
        final_path = result[0] if isinstance(result, (list, tuple)) else result
        
        # Move to result dir for serving
        output_filename = f"result_{int(time.time())}.webp"
        output_path = os.path.join(RESULT_DIR, output_filename)
        shutil.move(final_path, output_path)
        
        # Cleanup temp
        os.remove(temp_person_path)
        
        return {
            "success": True, 
            "result_url": f"{BASE_URL}/results/{output_filename}"
        }

    except Exception as e:
        print(f"❌ Error: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    # Use standard 0.0.0.0 to allow external access (important for server)
    uvicorn.run(app, host="0.0.0.0", port=8000)
