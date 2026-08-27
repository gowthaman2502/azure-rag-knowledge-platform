from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
)



from rag_knowledge_assistant.config import AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_ADMIN_KEY


class SearchIndexManager:

    def __init__(self):
        self.client = SearchIndexClient(
            endpoint=AZURE_SEARCH_ENDPOINT,
            credential=AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY),
        )

    def create_index(self, index_name):
        try:
            self.client.get_index(index_name)
            print(f"Index '{index_name}' already exists. Deleting it...")
            self.client.delete_index(index_name)
        except Exception:
            pass

        fields = [
            SimpleField(
                name="id",
                type=SearchFieldDataType.String,
                key=True,
            ),
            SearchableField(
                name="content",
                type=SearchFieldDataType.String,
            ),
            SearchField(
                name="content_vector",
                type=SearchFieldDataType.Collection(
                    SearchFieldDataType.Single
                ),
                searchable=True,
                vector_search_dimensions=1536,
                vector_search_profile_name="default-vector-profile",
            ),
            SearchableField(
                name="document_name",
                type=SearchFieldDataType.String,
                filterable=True,
            ),
            SimpleField(
                name="document_path",
                type=SearchFieldDataType.String,
                filterable=True,
            ),
            SimpleField(
                name="document_type",
                type=SearchFieldDataType.String,
                filterable=True,
            ),
            SimpleField(
                name="department",
                type=SearchFieldDataType.String,
                filterable=True,
            ),
            SimpleField(
                name="chunk_id",
                type=SearchFieldDataType.Int32,
                filterable=True,
            ),
            SimpleField(
                name="page",
                type=SearchFieldDataType.Int32,
                filterable=True,
            ),
        ]

        vector_search = VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(
                    name="default-hnsw"
                )
            ],
            profiles=[
                VectorSearchProfile(
                    name="default-vector-profile",
                    algorithm_configuration_name="default-hnsw",
                )
            ],
        )

        semantic_config = SemanticConfiguration(
            name="default-semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                title_field=SemanticField(field_name="document_name"),
                content_fields=[
                    SemanticField(field_name="content")
                ],
            ),
        )

        semantic_search = SemanticSearch(
            configurations=[semantic_config]
        )

        index = SearchIndex(
            name=index_name,
            fields=fields,
            vector_search=vector_search,
            semantic_search=semantic_search,
        )

        self.client.create_or_update_index(index)

        print(f"Index '{index_name}' created successfully.")