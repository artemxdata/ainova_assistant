# Ubuntu setup

## 1) Clone repo
git clone <repo_url>
cd ainova_assistant

## 2) Create env
conda create -n ainova_assistant python=3.10 -y
conda activate ainova_assistant
pip install -r requirements.txt

## 3) Env vars
cp .env.example .env
# edit .env and set keys

## 4) Run API
uvicorn app.api.server:app --host 0.0.0.0 --port 8000 --reload

## 5) Index RAG docs (if needed)
python -m app.rag.index_docs
