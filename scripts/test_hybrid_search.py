from langchain_openai import AzureOpenAIEmbeddings


from rag_knowledge_assistant.config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    AZURE_SEARCH_ENDPOINT,
    AZURE_SEARCH_ADMIN_KEY,
    AZURE_SEARCH_HYBRID_INDEX_NAME,
)

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery


def main():
    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    )

    client = SearchClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        index_name=AZURE_SEARCH_HYBRID_INDEX_NAME,
        credential=AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY),
    )

    questions = [
        "What is the Enterprise price?",
        "What is the expense submission deadline?",
        "What is the password expiration policy?",
        "What is the NDA confidentiality period?",
    ]

    for question in questions:
        print("\n" + "=" * 80)
        print(f"QUERY: {question}")
        print("=" * 80)

        query_vector = embeddings.embed_query(question)

        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=20,
            fields="content_vector",
        )

        results = client.search(
            search_text=question,
            vector_queries=[vector_query],
            query_type="semantic",
            semantic_configuration_name="default-semantic-config",
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
            top=5,
        )

        for rank, result in enumerate(results, start=1):
            print(f"\n--- Rank {rank} ---")
            print(f"Document: {result.get('document_name')}")
            print(f"Page: {result.get('page')}")
            print(f"Chunk: {result.get('chunk_id')}")
            print(f"Search Score: {result.get('@search.score')}")
            print(f"Reranker Score: {result.get('@search.rerankerScore')}")
            print(f"Content:\n{result.get('content', '')[:600]}")


if __name__ == "__main__":
    main()