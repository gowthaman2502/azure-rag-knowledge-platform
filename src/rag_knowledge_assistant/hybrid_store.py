from langchain_openai import AzureOpenAIEmbeddings
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient


from rag_knowledge_assistant.config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    AZURE_SEARCH_ENDPOINT,
    AZURE_SEARCH_ADMIN_KEY,
    AZURE_SEARCH_HYBRID_INDEX_NAME,
)


class HybridSearchStore:

    def __init__(self):
        self.embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        )

        self.client = SearchClient(
            endpoint=AZURE_SEARCH_ENDPOINT,
            index_name=AZURE_SEARCH_HYBRID_INDEX_NAME,
            credential=AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY),
        )

    def add_documents(self, documents):
        if not documents:
            return

        print(f"Generating embeddings for {len(documents)} chunks...")

        vectors = self.embeddings.embed_documents(
            [document.page_content for document in documents]
        )

        counters = {}
        search_documents = []

        for document, vector in zip(documents, vectors):
            metadata = document.metadata
            document_name = metadata.get("document_name", "document")

            chunk_id = counters.get(document_name, 0)
            counters[document_name] = chunk_id + 1

            search_documents.append({
                "id": self._create_id(document_name, chunk_id),
                "content": document.page_content,
                "content_vector": vector,
                "document_name": document_name,
                "document_path": metadata.get("document_path"),
                "document_type": metadata.get("document_type"),
                "department": metadata.get("department"),
                "chunk_id": chunk_id,
                "page": metadata.get("page"),
            })

        print(f"Uploading {len(search_documents)} documents...")

        result = self.client.upload_documents(
            documents=search_documents
        )

        if all(item.succeeded for item in result):
            print("Hybrid index populated successfully.")
        else:
            print("Some documents failed to upload.")

    def _create_id(self, document_name, chunk_id):
        safe_name = document_name.replace(".", "_").replace(" ", "_")
        return f"{safe_name}_{chunk_id}"