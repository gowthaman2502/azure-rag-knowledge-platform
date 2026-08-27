import json
from pathlib import Path


EVALUATION_DIR = Path(__file__).parent

REFUSAL_PHRASE = (
    "I don't have enough information in the provided knowledge base"
)


def load_results(filename):
    with open(EVALUATION_DIR / filename, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize(text):
    if text is None:
        return ""

    return " ".join(str(text).lower().split())


def hit_at_k(result, k):
    expected_document = result.get("expected_document")

    if not expected_document:
        return None

    return int(
        any(
            document.get("document") == expected_document
            for document in result["retrieved_documents"][:k]
        )
    )


def retrieval_metrics(results):
    metrics = {}

    for k in [1, 3, 5]:
        valid_results = [
            result for result in results
            if result.get("expected_document")
        ]

        hits = [
            hit_at_k(result, k)
            for result in valid_results
        ]

        metrics[f"hit_at_{k}"] = (
            sum(hits) / len(hits)
            if hits
            else 0
        )

    return metrics


def answer_correct(result):
    generated = normalize(result["generated_answer"])

    if result["type"] == "unanswerable":
        return int(REFUSAL_PHRASE.lower() in generated)

    facts = result.get("expected_facts", [])

    if not facts:
        return 0

    matched = sum(
        normalize(fact) in generated
        for fact in facts
    )

    return int(matched == len(facts))


def fact_coverage(result):
    generated = normalize(result["generated_answer"])
    facts = result.get("expected_facts", [])

    if not facts:
        return 1 if result["type"] == "unanswerable" else 0

    matched = sum(
        normalize(fact) in generated
        for fact in facts
    )

    return matched / len(facts)


def grounded(result):
    if result["type"] == "unanswerable":
        return int(
            REFUSAL_PHRASE.lower()
            in normalize(result["generated_answer"])
        )

    generated = normalize(result["generated_answer"])

    context = normalize(
        " ".join(
            document.get("content", "")
            for document in result["retrieved_documents"]
        )
    )

    facts = result.get("expected_facts", [])

    if not facts:
        return 0

    supported_facts = sum(
        normalize(fact) in context
        for fact in facts
    )

    answered_facts = sum(
        normalize(fact) in generated
        for fact in facts
    )

    return int(
        supported_facts == len(facts)
        and answered_facts == len(facts)
    )


def refusal_accuracy(result):
    if result["type"] != "unanswerable":
        return 1

    return int(
        REFUSAL_PHRASE.lower()
        in normalize(result["generated_answer"])
    )


def version_accuracy(result):
    question = normalize(result["question"])
    answer = normalize(result["generated_answer"])

    if "2026" not in question:
        return 1

    return int("2026" in answer)


def answer_metrics(results):
    return {
        "answer_correctness": sum(
            answer_correct(result)
            for result in results
        ) / len(results),

        "fact_coverage": sum(
            fact_coverage(result)
            for result in results
        ) / len(results),

        "groundedness": sum(
            grounded(result)
            for result in results
        ) / len(results),

        "refusal_accuracy": sum(
            refusal_accuracy(result)
            for result in results
        ) / len(results),

        "version_accuracy": sum(
            version_accuracy(result)
            for result in results
        ) / len(results),
    }


def print_metrics(name, retrieval, answers):
    print(f"\n{name}")
    print("-" * 50)

    print(f"HIT@1              : {retrieval['hit_at_1']:.2%}")
    print(f"HIT@3              : {retrieval['hit_at_3']:.2%}")
    print(f"HIT@5              : {retrieval['hit_at_5']:.2%}")
    print(f"ANSWER CORRECTNESS : {answers['answer_correctness']:.2%}")
    print(f"FACT COVERAGE      : {answers['fact_coverage']:.2%}")
    print(f"GROUNDEDNESS       : {answers['groundedness']:.2%}")
    print(f"REFUSAL ACCURACY   : {answers['refusal_accuracy']:.2%}")
    print(f"VERSION ACCURACY   : {answers['version_accuracy']:.2%}")


def print_question_comparison(baseline, improved):
    print("\n" + "=" * 100)
    print("QUESTION-LEVEL COMPARISON")
    print("=" * 100)

    for old, new in zip(baseline, improved):
        print(f"\n{old['id']}: {old['question']}")

        print(
            f"  Retrieval Hit@1 : "
            f"{hit_at_k(old, 1)} -> {hit_at_k(new, 1)}"
        )

        print(
            f"  Answer Correct  : "
            f"{answer_correct(old)} -> {answer_correct(new)}"
        )

        print(
            f"  Fact Coverage   : "
            f"{fact_coverage(old):.2%} -> "
            f"{fact_coverage(new):.2%}"
        )

        print(
            f"  Grounded        : "
            f"{grounded(old)} -> {grounded(new)}"
        )

        print(
            f"  Refusal         : "
            f"{refusal_accuracy(old)} -> "
            f"{refusal_accuracy(new)}"
        )

        print(
            f"  Version         : "
            f"{version_accuracy(old)} -> "
            f"{version_accuracy(new)}"
        )


def print_improvement(name, baseline, improved):
    print(f"\n{name}")
    print("-" * 50)

    for metric in baseline:
        change = improved[metric] - baseline[metric]

        print(
            f"{metric.upper():<20}: "
            f"{baseline[metric]:.2%} -> "
            f"{improved[metric]:.2%} "
            f"({change:+.2%})"
        )


def main():
    baseline = load_results("baseline_results.json")
    improved = load_results("improved_results.json")

    baseline_retrieval = retrieval_metrics(baseline)
    improved_retrieval = retrieval_metrics(improved)

    baseline_answers = answer_metrics(baseline)
    improved_answers = answer_metrics(improved)

    print("\n" + "=" * 100)
    print("RAG EVALUATION")
    print("=" * 100)

    print_metrics(
        "BASELINE",
        baseline_retrieval,
        baseline_answers,
    )

    print_metrics(
        "IMPROVED",
        improved_retrieval,
        improved_answers,
    )

    print_question_comparison(
        baseline,
        improved,
    )

    print("\n" + "=" * 100)
    print("RETRIEVAL IMPROVEMENT")
    print("=" * 100)

    print_improvement(
        "Retrieval",
        baseline_retrieval,
        improved_retrieval,
    )

    print("\n" + "=" * 100)
    print("ANSWER QUALITY IMPROVEMENT")
    print("=" * 100)

    print_improvement(
        "Answer Quality",
        baseline_answers,
        improved_answers,
    )


if __name__ == "__main__":
    main()