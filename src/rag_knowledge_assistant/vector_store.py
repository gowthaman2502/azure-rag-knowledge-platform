from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import AzureSearch


from rag_knowledge_assistant.config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    AZURE_SEARCH_ENDPOINT,
    AZURE_SEARCH_ADMIN_KEY,
    AZURE_SEARCH_INDEX_NAME,
)


class AzureAISearchStore:

    def __init__(self):
        self.embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        )

        self.vector_store = AzureSearch(
            azure_search_endpoint=AZURE_SEARCH_ENDPOINT,
            azure_search_key=AZURE_SEARCH_ADMIN_KEY,
            index_name=AZURE_SEARCH_INDEX_NAME,
            embedding_function=self.embeddings.embed_query,
        )

    def add_documents(self, documents):
        if not documents:
            print("No documents to index.")
            return

        print(f"Indexing {len(documents)} chunks...")

        self.vector_store.add_documents(documents)

        print("Indexing completed.")

    def similarity_search(self, query, k=5):
        return self.vector_store.similarity_search(
            query,
            k=k,
        )