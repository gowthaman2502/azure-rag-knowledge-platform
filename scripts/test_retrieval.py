
from rag_knowledge_assistant.config import validate_config

from rag_knowledge_assistant.vector_store import AzureAISearchStore


def main():
    validate_config()

    vector_store = AzureAISearchStore()

    queries = [
        "What is the expense submission deadline?",
        "What is the Enterprise pricing?",
        "What is the password expiration policy?",
        "What is the NDA confidentiality period?",
        "What is the leave policy?",
    ]

    for query in queries:
        print("\n" + "=" * 80)
        print(f"QUERY: {query}")
        print("=" * 80)

        results = vector_store.similarity_search(query, k=5)

        for rank, document in enumerate(results, start=1):
            print(f"\n--- Rank {rank} ---")
            print(f"Document: {document.metadata.get('document_name')}")
            print(f"Department: {document.metadata.get('department')}")
            print(f"Page: {document.metadata.get('page')}")
            print(f"Content:\n{document.page_content[:500]}")


if __name__ == "__main__":
    main()