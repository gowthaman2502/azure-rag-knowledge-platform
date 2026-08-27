from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery


from rag_knowledge_assistant.config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_CHAT_DEPLOYMENT,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    AZURE_SEARCH_ENDPOINT,
    AZURE_SEARCH_ADMIN_KEY,
    AZURE_SEARCH_HYBRID_INDEX_NAME,
)


class RAGChain:

    def __init__(self):
        self.embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        )

        self.search_client = SearchClient(
            endpoint=AZURE_SEARCH_ENDPOINT,
            index_name=AZURE_SEARCH_HYBRID_INDEX_NAME,
            credential=AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY),
        )

        self.llm = AzureChatOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_deployment=AZURE_OPENAI_CHAT_DEPLOYMENT,
            temperature=0,
        )

        self.rewrite_prompt = ChatPromptTemplate.from_template(
            """Rewrite the user's latest question into a standalone search query.

Use the conversation history only to resolve references such as:
- "this"
- "that"
- "what about"
- "how about"
- "it"
- "the previous one"

Rules:
- Preserve the user's intent.
- Preserve important years, versions, product names, policy names, and entities.
- Do not answer the question.
- Do not add information that is not present in the conversation.
- If the question is already standalone, return it unchanged.
- Return only the rewritten search query.

Conversation history:
{history}

Latest question:
{question}

Search query:"""
        )

        self.prompt = ChatPromptTemplate.from_template(
            """You are an enterprise knowledge assistant.

Answer the user's question using ONLY the information provided in the context.

Rules:
- Do not use outside knowledge.
- Do not invent, assume, estimate, or guess information.
- Do not perform calculations to fill in missing information.
- Use the most relevant and current information available in the context.
- If different years, versions, or effective dates appear, use the information relevant to the user's question.
- When multiple documents contain similar or overlapping information, prefer the document most directly relevant to the user's question.
- When the question asks about a specific policy, procedure, or document topic, answer from the most directly relevant source even if another retrieved source contains related information.
- Do not merge rules from different policies or documents unless the user explicitly asks for a comparison or combined answer.
- If two sources contain conflicting information, do not silently combine them. Prefer the source most directly relevant to the question and mention the distinction when necessary.
- If the question refers to a term that does not appear in the context, do not assume it means a similar term.
- Answer only what is supported by the context.
- If the context does not explicitly support the answer, say:
"I don't have enough information in the provided knowledge base to answer this question."
- Keep the answer concise.

Context:
{context}

Question:
{question}

Answer:"""
        )

    def _rewrite_query(self, question, conversation_history):
        if not conversation_history:
            return question

        history = "\n".join(
            f"{item['role'].capitalize()}: {item['content']}"
            for item in conversation_history[-6:]
        )

        messages = self.rewrite_prompt.format_messages(
            history=history,
            question=question,
        )

        response = self.llm.invoke(messages)
        return response.content.strip()

    def _build_filter(self, filters):
        if not filters:
            return None

        allowed_fields = {
            "document_name",
            "document_path",
            "document_type",
            "department",
            "chunk_id",
            "page",
        }

        expressions = []

        for field, value in filters.items():
            if field not in allowed_fields:
                raise ValueError(
                    f"Unsupported filter field: {field}"
                )

            if isinstance(value, str):
                escaped_value = value.replace("'", "''")
                expressions.append(
                    f"{field} eq '{escaped_value}'"
                )

            elif isinstance(value, int):
                expressions.append(
                    f"{field} eq {value}"
                )

            else:
                raise ValueError(
                    f"Unsupported filter value for {field}: "
                    f"{type(value).__name__}"
                )

        return " and ".join(expressions)

    def ask(
        self,
        question,
        conversation_history=None,
        k=5,
        filters=None,
    ):
        conversation_history = conversation_history or []

        search_query = self._rewrite_query(
            question,
            conversation_history,
        )

        query_vector = self.embeddings.embed_query(search_query)

        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=20,
            fields="content_vector",
        )

        filter_expression = self._build_filter(filters)

        results = self.search_client.search(
            search_text=search_query,
            vector_queries=[vector_query],
            query_type="semantic",
            semantic_configuration_name="default-semantic-config",
            filter=filter_expression,
            select=[
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

        documents = []

        for result in results:
            documents.append(
                Document(
                    page_content=result.get("content", ""),
                    metadata={
                        "document_name": result.get("document_name"),
                        "document_path": result.get("document_path"),
                        "document_type": result.get("document_type"),
                        "department": result.get("department"),
                        "chunk_id": result.get("chunk_id"),
                        "page": result.get("page"),
                    },
                )
            )

        context_parts = []

        for i, document in enumerate(documents, start=1):
            source = document.metadata.get(
                "document_name",
                "Unknown",
            )
            page = document.metadata.get("page")
            chunk = document.metadata.get("chunk_id")

            citation = source

            if page:
                citation += f", Page {page}"

            if chunk is not None:
                citation += f", Chunk {chunk}"

            context_parts.append(
                f"[Source {i}: {citation}]\n"
                f"{document.page_content}"
            )

        context = "\n\n".join(context_parts)

        messages = self.prompt.format_messages(
            context=context,
            question=question,
        )

        response = self.llm.invoke(messages)
        answer = response.content

        return {
            "answer": answer,
            "documents": documents,
            "search_query": search_query,
        }