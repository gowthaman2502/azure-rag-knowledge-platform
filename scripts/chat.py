
from rag_knowledge_assistant.config import validate_config
from rag_knowledge_assistant.rag import RAGChain


def main():
    validate_config()

    rag = RAGChain()

    questions = [
        "What is the expense submission deadline?",
        "What is the Enterprise price?",
        "What is the password expiration policy?",
        "What is the NDA confidentiality period?",
        "What is the leave policy?",
        "What is the price of a Ferrari?",
    ]

    for question in questions:
        question = "What is the Enterprise price?"
        print("\n" + "=" * 80)
        print(f"QUESTION: {question}")
        print("=" * 80)

        # result = rag.ask(question)
        result = rag.ask(
            question,
            filters={"document_name": "Pricing2026.pdf"}
        )
        print("\nANSWER:")
        print(result["answer"])

        print("\nRETRIEVED SOURCES:")

        for rank, document in enumerate(result["documents"], start=1):
            print(
                f"{rank}. "
                f"{document.metadata.get('document_name')} "
                f"(Page {document.metadata.get('page')})"
            )
        break


if __name__ == "__main__":
    main()