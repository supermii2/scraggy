from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import faiss
import json
import numpy as np
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

EMBED_MODEL = "text-embedding-3-small"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Build absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAISS_PATH = os.path.join(BASE_DIR, "./faiss/embeddings.faiss")
META_PATH  = os.path.join(BASE_DIR, "./faiss/metadata.json")

# Load FAISS + metadata
index = faiss.read_index(FAISS_PATH)
with open(META_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class Query(BaseModel):
    text: str

@app.post("/search")
def search(query: Query):
    # Compute embedding
    emb = client.embeddings.create(
        model=EMBED_MODEL,
        input=query.text
    ).data[0].embedding

    q_emb = np.array(emb, dtype="float32").reshape(1, -1)

    # Run FAISS
    D, I = index.search(q_emb, 5)

    results = []
    for dist, idx in zip(D[0], I[0]):
        if idx == -1:
            continue
        entry = metadata[str(idx)]
        results.append({
            "id": entry["id"],
            "text": entry["text"],
            "name": entry["name"],
            "distance": float(dist)
        })

    return {"results": results}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("backend:app", host="0.0.0.0", port=port, reload=True)
