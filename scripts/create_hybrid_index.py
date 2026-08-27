
from rag_knowledge_assistant.config import (
    AZURE_SEARCH_HYBRID_INDEX_NAME,
    validate_config,
)

from rag_knowledge_assistant.search_index import SearchIndexManager


def main():
    validate_config()

    manager = SearchIndexManager()
    manager.create_index(AZURE_SEARCH_HYBRID_INDEX_NAME)


if __name__ == "__main__":
    main()