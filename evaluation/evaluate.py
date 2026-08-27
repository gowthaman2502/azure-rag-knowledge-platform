import json
from pathlib import Path


from rag_knowledge_assistant.config import validate_config
from rag_knowledge_assistant.rag import RAGChain


def load_questions():
    path = Path(__file__).parent / "questions.json"

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    validate_config()

    questions = load_questions()
    rag = RAGChain()

    results = []

    for item in questions:
        question = item["question"]

        print("\n" + "=" * 80)
        print(f"{item['id']}: {question}")
        print("=" * 80)

        result = rag.ask(question)

        print("\nANSWER:")
        print(result["answer"])

        print("\nRETRIEVED DOCUMENTS:")

        retrieved_documents = []

        for rank, document in enumerate(result["documents"], start=1):
            document_name = document.metadata.get("document_name")
            page = document.metadata.get("page")

            print(f"{rank}. {document_name} | Page: {page}")

            retrieved_documents.append({
                "rank": rank,
                "document": document_name,
                "page": page,
                "content": document.page_content
            })

        results.append({
            "id": item["id"],
            "question": question,
            "expected_answer": item["expected_answer"],
            "expected_document": item["expected_document"],
            "type": item["type"],
            "difficulty": item["difficulty"],
            "expected_facts": item.get("expected_facts", []),
            "generated_answer": result["answer"],
            "retrieved_documents": retrieved_documents
        })

    # output_path = Path(__file__).parent / "baseline_results.json"
    output_path = Path(__file__).parent / "improved_results.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print(f"Evaluation completed.")
    print(f"Results saved to: {output_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()