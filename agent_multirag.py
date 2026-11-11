import sys
from pathlib import Path

import chromadb
from langchain_chroma import Chroma

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
from llm_client import call_llm

DB_PATH = BASE_DIR / "chroma_db"
COLLECTION_NAME = "kuku_legal_knowledge"


def load_knowledge_base():
    """Open the persistent collection built by build_knowledge_base.py."""
    client = chromadb.PersistentClient(path=str(DB_PATH))
    try:
        collection = client.get_collection(COLLECTION_NAME)
    except Exception as exc:
        raise RuntimeError(
            "The legal knowledge base is not built yet. Run "
            "'python build_knowledge_base.py' first."
        ) from exc

    if collection.count() == 0:
        raise RuntimeError(
            "The legal knowledge base is empty. Run 'python build_knowledge_base.py' first."
        )

    return Chroma(client=client, collection_name=COLLECTION_NAME)


# Module-level conversation history, matching agent.py.
conversation_history = []


def generate_search_queries(query):
    """Create complementary retrieval queries for multi-query RAG."""
    system_prompt = """You create search queries for an Indian law knowledge base.
Generate exactly three short, distinct search queries that explore the user's
question from complementary angles. Preserve statute names, section numbers,
legal terms, and relevant synonyms. Return only the three queries, one per line,
with no numbering or explanation."""
    response = call_llm(system_prompt, f"User question: {query}")

    queries = []
    for line in response.splitlines():
        candidate = line.strip().lstrip("-• ")
        if candidate and len(candidate) > 2:
            queries.append(candidate)

    distinct_queries = [query]
    seen = {query.casefold()}
    for candidate in queries:
        normalized = candidate.casefold()
        if normalized not in seen:
            seen.add(normalized)
            distinct_queries.append(candidate)
        if len(distinct_queries) == 4:
            break
    return distinct_queries


def process_query(query, collection):
    """Retrieve across multiple query views, combine evidence, and answer."""
    global conversation_history

    history_context = ""
    if conversation_history:
        history_lines = [
            f"{turn['role'].capitalize()}: {turn['content']}"
            for turn in conversation_history
        ]
        history_context = "Conversation history:\n" + "\n".join(history_lines) + "\n\n"

    system_prompt = """You are an AI legal information assistant.
    For this prototype, focus on one step: helping a person prepare an
    organized intake note about an Indian consumer purchase or paid service
    problem, such as non-delivery, a defective product, or a cancelled event.
    When relevant, structure the response as: facts the user provided, a dated
    or ordered timeline, missing facts and focused questions, relevant retrieved
    legal sources, and evidence or documents to organize. Do not infer a contract
    term, deadline, refund entitlement, or legal outcome. If retrieved materials
    do not support an answer, say so clearly.

    Follow these rules:
    - Answer using only the supplied legal knowledge context and the user's facts.
    - Do not invent statutes, sections, case law, deadlines, or legal outcomes.
    - Identify relevant sources and provisions when the retrieved material supports them.
    - Explain uncertainty and say when the available materials do not answer the question.
    - Provide general legal information, not a guarantee or a substitute for advice from a qualified lawyer.
    - Ask a focused follow-up question when essential facts are missing."""

    search_queries = generate_search_queries(query)
    retrieved_docs = []
    seen_contents = set()
    for search_query in search_queries:
        for doc in collection.similarity_search(search_query, k=3):
            if doc.page_content not in seen_contents:
                seen_contents.add(doc.page_content)
                retrieved_docs.append(doc)

    context_parts = [
        f"Source: {doc.metadata.get('source', 'Unknown')}\nContent: {doc.page_content}"
        for doc in retrieved_docs
    ]
    context = "\n\n".join(context_parts)
    user_prompt = f"""{history_context}User question: {query}

        Retrieval queries used:
        {chr(10).join(f'- {item}' for item in search_queries)}

        Retrieved legal knowledge context:
        {context if context else "No relevant knowledge chunks were retrieved."}

        Answer the user's question using the retrieved evidence. Cite source paths
        and provisions where available, and state clearly if the evidence is insufficient."""

    answer = call_llm(system_prompt, user_prompt)
    conversation_history.append({"role": "user", "content": query})
    conversation_history.append({"role": "assistant", "content": answer})
    return answer


def main():
    try:
        collection = load_knowledge_base()
    except Exception as exc:
        print(f"Unable to load legal knowledge base: {exc}")
        return

    print("AI Law Chatbot")
    print("Type 'exit' to quit. Ask a question about the indexed legal materials.")
    while True:
        try:
            query = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break
        if query.lower() in {"exit", "quit"}:
            break
        if not query:
            continue
        try:
            answer = process_query(query, collection)
            print(f"\nAgent: {answer}")
        except Exception as exc:
            print(f"\nError: {exc}")


if __name__ == "__main__":
    main()
