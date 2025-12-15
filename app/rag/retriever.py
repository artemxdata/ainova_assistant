# app/rag/retriever.py

import json
import numpy as np
from scipy.spatial.distance import cosine

from app.memory.db import SessionLocal
from app.memory.models import Document
from app.rag.embeddings import get_embedding


def retrieve_documents(query: str, top_k: int = 3):
    """
    Ищем top_k документов, наиболее похожих на запрос (по косинусному сходству).
    """
    query_emb = np.array(get_embedding(query))

    with SessionLocal() as session:
        docs = session.query(Document).all()

        if not docs:
            return []

        scored = []
        for doc in docs:
            doc_emb_list = json.loads(doc.embedding)
            doc_emb = np.array(doc_emb_list)
            sim = 1 - cosine(query_emb, doc_emb)
            scored.append((doc, sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in scored[:top_k]]
