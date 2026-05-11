import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from openai import OpenAI

# -----------------------------
# Step 1: Load data
# -----------------------------
def load_documents(file_path):
    with open(file_path, "r") as f:
        docs = f.readlines()
    return [doc.strip() for doc in docs if doc.strip()]

documents = load_documents("faqs.txt")

# -----------------------------
# Step 2: Create embeddings
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")
doc_embeddings = model.encode(documents)

# -----------------------------
# Step 3: Store in FAISS
# -----------------------------
dimension = doc_embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(doc_embeddings))

# -----------------------------
# Step 4: Query function
# -----------------------------
def retrieve(query, k=2):
    query_embedding = model.encode([query])
    distances, indices = index.search(np.array(query_embedding), k)
    
    results = [documents[i] for i in indices[0]]
    return results

# -----------------------------
# Step 5: Generate answer
# -----------------------------
client = OpenAI(api_key="YOUR_API_KEY")

def generate_answer(query):
    context = retrieve(query)
    
    prompt = f"""
    Answer the question using the context below.
    
    Context:
    {context}
    
    Question:
    {query}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    while True:
        query = input("\nAsk something: ")
        answer = generate_answer(query)
        print("\nAnswer:", answer)