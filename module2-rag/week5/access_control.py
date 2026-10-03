"""Prove access control works: the same query, asked as three different
roles, sees three different sets of sources - and an embargoed source is
never visible to a public query, no matter how relevant it looks.

Run it:  python access_control.py
Prereq:  python build_secure_index.py (this week), Qdrant running locally
"""
from rag.embed import embed_query
from rag.qdrant_store import QdrantStore
from rag.access import visibility_filter


def main():
    store = QdrantStore.connect()

    query = "did any council member have a financial conflict of interest with the arena contractor"
    query_vector = embed_query(query)

    for role in ["public", "reporter", "editor"]:
        print(f'\nQuery (as role="{role}"): "{query}"')
        for score, payload in store.search_with_filter(query_vector, visibility_filter(role)):
            meta = payload["metadata"]
            print(f"  [{score:.3f}] {meta.get('source')} (visibility={meta.get('visibility')})")


if __name__ == "__main__":
    main()
