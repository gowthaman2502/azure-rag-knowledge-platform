from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient


from rag_knowledge_assistant.config import (
    AZURE_SEARCH_ENDPOINT,
    AZURE_SEARCH_ADMIN_KEY,
    AZURE_SEARCH_HYBRID_INDEX_NAME,
)


def main():
    client = SearchIndexClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        credential=AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY),
    )

    index = client.get_index(AZURE_SEARCH_HYBRID_INDEX_NAME)

    print(f"Index: {index.name}")
    print("\nFields:")

    for field in index.fields:
        print(
            f"- {field.name} | "
            f"type={field.type} | "
            f"searchable={field.searchable} | "
            f"filterable={field.filterable} | "
            f"facetable={field.facetable}"
        )


if __name__ == "__main__":
    main()