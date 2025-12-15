# app/rag/retriever.py

import json
from typing import List

import numpy as np

from app.memory.db import SessionLocal
from app.memory.models import Document
from app.rag.embeddings import get_embedding


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """
    Косинусное сходство без SciPy.
    """
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0.0:
        return 0.0
    return float(np.dot(a, b) / denom)


def retrieve_documents(query: str, top_k: int = 3) -> List[Document]:
    """
    Ищем top_k документов, наиболее похожих на запрос (по косинусному сходству).
    """
    query_emb = np.array(get_embedding(query), dtype=np.float32)

    with SessionLocal() as session:
        docs = session.query(Document).all()
        if not docs:
            return []

        scored = []
        for doc in docs:
            try:
                doc_emb_list = json.loads(doc.embedding)
                doc_emb = np.array(doc_emb_list, dtype=np.float32)
                sim = cosine_sim(query_emb, doc_emb)
                scored.append((doc, sim))
            except Exception:
                # Если какой-то документ битый — просто пропускаем, не валим запрос.
                continue

        scored.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in scored[:top_k]]
