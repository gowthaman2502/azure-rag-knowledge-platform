
from rag_knowledge_assistant.config import validate_config

from rag_knowledge_assistant.ingestion import KnowledgeBaseIngestion

from rag_knowledge_assistant.vector_store import AzureAISearchStore

def main():
    validate_config()

    ingestion = KnowledgeBaseIngestion()
    chunks = ingestion.run()

    # print("\nSample chunks:\n")

    # for index, chunk in enumerate(chunks[:5], start=1):
    #     print("=" * 80)
    #     print(f"Chunk {index}")
    #     print(f"Document: {chunk.metadata.get('document_name')}")
    #     print(f"Department: {chunk.metadata.get('department')}")
    #     print(f"Page: {chunk.metadata.get('page')}")
    #     print("-" * 80)
    #     print(chunk.page_content[:500])

    print(f"\nPreparing to index {len(chunks)} chunks...")

    vector_store = AzureAISearchStore()
    vector_store.add_documents(chunks)

    print("\nBaseline ingestion completed successfully.")


if __name__ == "__main__":
    main()