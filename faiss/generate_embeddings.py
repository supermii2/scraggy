import requests
import json
from openai import OpenAI
from dotenv import load_dotenv
import os
import numpy as np
import faiss
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

NUM_POKEMON = 1025
EMBED_MODEL = "text-embedding-3-small"
SIM_THRESHOLD = 0.1

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Please set your OPENAI_API_KEY environment variable.")

client = OpenAI(api_key=api_key)

def fetch_flavor_texts(pokemon_id, entries = []):
    try:
        url = f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_id}"
        data = requests.get(url).json()

        for entry in data["flavor_text_entries"]:
            if entry["language"]["name"] == "en":
                text = entry["flavor_text"]
                text = text.replace("\n", " ").replace("\f", " ").strip()
                entries.append([pokemon_id, text])
    except:
        print(f"Failed to retrieve id: {pokemon_id}")

def fetch_all_flavor_texts(entries = []):
    for n in range(1, NUM_POKEMON + 1):
        print(f"Fetching {n}...")
        fetch_flavor_texts(n, entries)

def get_embedding_for_entries(entries):
    embeddings_data = []

    for poke_id, text in entries:
        print(text)
        response = client.embeddings.create(
            model=EMBED_MODEL,
            input=text
        )
        embedding = response.data[0].embedding
        embeddings_data.append({
            "id": poke_id,
            "text": text,
            "embedding": embedding
        })
    return embeddings_data

def remove_similar_embeddings(embeddings_data, threshold=SIM_THRESHOLD):
    if not embeddings_data:
        return []

    from collections import defaultdict
    grouped = defaultdict(list)
    for i, item in enumerate(embeddings_data):
        grouped[item["id"]].append((i, item))

    keep_indices = []

    for poke_id, items in grouped.items():
        # Reverse items so newest embeddings come first
        items = items[::-1]

        emb_matrix = np.array([item["embedding"] for idx, item in items], dtype=np.float32)
        norms = np.linalg.norm(emb_matrix, axis=1, keepdims=True)
        emb_matrix_norm = emb_matrix / (norms + 1e-10)

        group_keep = []
        for i, emb in enumerate(emb_matrix_norm):
            if not group_keep:
                group_keep.append(i)
                continue
            sims = cosine_similarity(emb.reshape(1, -1), emb_matrix_norm[group_keep])[0]
            if np.all(sims < (1 - threshold)):
                group_keep.append(i)

        # Map back to original indices
        keep_indices.extend([items[i][0] for i in group_keep])

    # Optional: sort keep_indices to preserve original order
    keep_indices.sort()

    filtered = [embeddings_data[i] for i in keep_indices]
    print(f"Filtered {len(embeddings_data) - len(filtered)} near-duplicate embeddings (per Pokémon, keeping newest)")
    return filtered



def save_faiss_and_metadata(embeddings_data, faiss_file="embeddings.faiss", metadata_file="metadata.json"):
    if not embeddings_data:
        print("No embeddings to save!")
        return

    emb_matrix = np.array([item["embedding"] for item in embeddings_data]).astype("float32")
    dim = emb_matrix.shape[1]

    index = faiss.IndexFlatL2(dim)
    index.add(emb_matrix)
    faiss.write_index(index, faiss_file)
    print(f"Saved FAISS index to {faiss_file}")

    metadata = {i: {"id": embeddings_data[i]["id"], "text": embeddings_data[i]["text"]} for i in range(len(embeddings_data))}
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"Saved metadata to {metadata_file}")

if __name__ == "__main__":
    entries = []
    fetch_all_flavor_texts(entries)

    embeddings = get_embedding_for_entries(entries)
    embeddings = remove_similar_embeddings(embeddings, threshold=SIM_THRESHOLD)

    save_faiss_and_metadata(embeddings)
