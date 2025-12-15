# app/rag/index_docs.py

import os
import json

from app.rag.embeddings import get_embedding
from app.memory.db import SessionLocal
from app.memory.models import Document

DOCUMENTS_PATH = "data/docs"


def index_documents():
    """
    Индексируем все текстовые файлы в папке data/docs/
    и сохраняем их эмбеддинги в БД.
    """
    files = [f for f in os.listdir(DOCUMENTS_PATH) if f.endswith(".txt")]
    if not files:
        print("В папке data/docs нет .txt файлов.")
        return

    with SessionLocal() as session:
        for filename in files:
            filepath = os.path.join(DOCUMENTS_PATH, filename)
            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read()

            embedding = get_embedding(content)

            doc = Document(
                title=filename,
                content=content,
                embedding=json.dumps(embedding),  # Сохраняем как JSON-строку
            )
            session.add(doc)

        session.commit()
        print(f"Индексация завершена. Загружено {len(files)} документов.")


if __name__ == "__main__":
    index_documents()
