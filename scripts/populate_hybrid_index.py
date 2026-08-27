
from rag_knowledge_assistant.config import validate_config

from rag_knowledge_assistant.ingestion import KnowledgeBaseIngestion

from rag_knowledge_assistant.hybrid_store import HybridSearchStore


def main():
    validate_config()

    ingestion = KnowledgeBaseIngestion()
    chunks = ingestion.run()

    store = HybridSearchStore()
    store.add_documents(chunks)


if __name__ == "__main__":
    main()