
from rag_knowledge_assistant.ingestion import KnowledgeBaseIngestion


def main():
    ingestion = KnowledgeBaseIngestion()
    chunks = ingestion.run()

    print(f"\nTotal chunks: {len(chunks)}")

    for i, chunk in enumerate(chunks[:10]):
        print("\n" + "=" * 70)
        print(f"Chunk {i}")
        print("=" * 70)
        print("Metadata:")
        print(chunk.metadata)
        print("\nContent:")
        print(chunk.page_content[:300])


if __name__ == "__main__":
    main()