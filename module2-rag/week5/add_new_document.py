"""Add a brand-new document to the index, WITHOUT rebuilding anything else.

Run it:  python add_new_document.py
Prereq:  python build_secure_index.py (this week), Qdrant running locally
"""
from rag.qdrant_store import QdrantStore
from rag.reindex import add_document


def main():
    store = QdrantStore.connect()

    before = store.client.count(collection_name=store.collection).count
    print(f"Chunks in the index before: {before}")

    n_added = add_document(store, "data/articles/heatwave-council-response.md")

    after = store.client.count(collection_name=store.collection).count
    print(f"Added {n_added} new chunk(s) for heatwave-council-response.md.")
    print(f"Chunks in the index after: {after}")
    print("Every other document's chunks - and their embeddings - were never touched.")


if __name__ == "__main__":
    main()
