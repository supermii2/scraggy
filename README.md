# Scraggy (Reworded Dex Entry Solver)

This is a hastily put together reworded entry solver that uses a RAG pipeline.

Note: it does not have most dex entries for Pokemon with different forms. \
This is a limitation of PokeAPI where the dex entries are pulled from. \
Can be fixed by having a manual database of dex entries but that's for another time.

## How to Run

### FAISS (Embedding Generation)

1. Create a ``.env`` file, and set your ``OPENAI_API_KEY`` field appropriately.
2. Run ``pip install -r requirements.txt`
3. Run ``python generate_embeddings.py``
4. The embeddings files created are ``embeddings.faiss`` and ``metadata.json``

### Backend
1. Create a ``.env`` file, and set your ``OPENAI_API_KEY`` field appropriately. 
2. Run ``pip install -r requirements.txt`
3. Move the generated embeddings and metadata files into the `faiss` folder.
4. Run `python backend.py` to run the server.

### Frontend
1. Run ``npm -i``
2. Run ``npm start`` to run the server.