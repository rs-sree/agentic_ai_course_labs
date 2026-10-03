"""Update an existing document: remove its OLD chunks, add its NEW ones -
without touching any other document in the archive.

Run it:  python update_existing_document.py
Prereq:  python build_secure_index.py + python add_new_document.py (this week),
         and data/articles/heatwave-warning.md already overwritten with the
         escalated version (see the take's off-camera edit note).
"""
from rag.qdrant_store import QdrantStore
from rag.reindex import update_document


def main():
    store = QdrantStore.connect()

    before = store.client.count(collection_name=store.collection).count
    n_updated = update_document(store, "data/articles/heatwave-warning.md", "heatwave-warning.md")
    after = store.client.count(collection_name=store.collection).count

    print(f"Chunks before: {before}")
    print(f"Removed heatwave-warning.md's old chunk(s), added {n_updated} new one(s).")
    print(f"Chunks after: {after}")

    # prove the OLD content is really gone, not just outranked
    hits, _ = store.client.scroll(collection_name=store.collection, limit=100)
    hw_texts = [h.payload["text"] for h in hits if h.payload["metadata"].get("source") == "heatwave-warning.md"]
    print(f"\nheatwave-warning.md now has {len(hw_texts)} chunk(s) in the index.")
    print("Contains the escalated '42 degrees' wording:", any("42 degrees" in t for t in hw_texts))
    print("Still contains the OLD '39 degrees' wording:", any("39 degrees" in t for t in hw_texts))


if __name__ == "__main__":
    main()
