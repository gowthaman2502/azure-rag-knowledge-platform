from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery


from rag_knowledge_assistant.config import (
    AZURE_SEARCH_ENDPOINT,
    AZURE_SEARCH_ADMIN_KEY,
)


class HybridSearch:

    def __init__(self, index_name):
        self.client = SearchClient(
            endpoint=AZURE_SEARCH_ENDPOINT,
            index_name=index_name,
            credential=AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY),
        )

    def search(self, query, query_vector, k=5):
        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=k,
            fields="content_vector",
        )

        results = self.client.search(
            search_text=query,
            vector_queries=[vector_query],
            select=[
                "id",
                "content",
                "document_name",
                "document_path",
                "document_type",
                "department",
                "chunk_id",
                "page",
            ],
            top=k,
        )

        return list(results)