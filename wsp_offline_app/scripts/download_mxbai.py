from sentence_transformers import SentenceTransformer
import sys

print("Downloading mixedbread-ai/mxbai-embed-large-v1 (~669MB)...")
sys.stdout.flush()
model = SentenceTransformer("mixedbread-ai/mxbai-embed-large-v1", local_files_only=False)
v = model.encode(["test query"], normalize_embeddings=True)
print(f"Done. Vector dims: {v.shape[1]}")
