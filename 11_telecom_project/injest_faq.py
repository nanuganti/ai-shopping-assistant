"""
injest faq.csv to chrome local storage for testing
"""
from langchain_core import documents
import pandas as pd
import chromadb 

# load the csv file
faq_df = pd.read_csv("./data/faq.csv")

# initialize chromadb client save to local storage
client = chromadb.PersistentClient(path="./chromadb_storage")

# add the faq data to the chromadb collection id,question,answer,category
collection = client.get_or_create_collection("faq_collection")
for index, row in faq_df.iterrows():
    collection.add(
        documents=[row["answer"]],
        metadatas=[{"question": row["question"], "category": row["category"]}],
        ids=[str(index)],
    )

## store the collection in local storage
batch_size = 100
for i in range(0, len(faq_df), batch_size):
    batch = faq_df.iloc[i:i + batch_size]
    collection.add(
        documents=batch["answer"].tolist(),
        metadatas=[{"question": q, "category": c} for q, c in zip(batch["question"], batch["category"])],
        ids=[str(idx) for idx in batch.index.tolist()],
    )

print(f"Successfully ingested {len(documents)} rows into ChromaDB!")