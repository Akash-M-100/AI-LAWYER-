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


# Module-level conversation history for multi-step agentic loop
conversation_history = []


def process_query(query, collection):
    """Retrieve relevant legal materials and ask the LLM to answer cautiously."""
    global conversation_history

    history_context = ""
    if conversation_history:
        history_lines = [
            f"{turn['role'].capitalize()}: {turn['content']}"
            for turn in conversation_history
        ]
        history_context = "Conversation history:\n" + "\n".join(history_lines) + "\n\n"

    system_prompt = """You are an AI legal information assistant.
    Follow these rules:
    - Give the information or questions in simple and consise points.
    - Ask clarifying questions if the user's query is ambiguous or lacks essential details.
    - Answer using only the supplied legal knowledge context and the user's facts.
    - Do not invent statutes, sections, case law, deadlines, or legal outcomes.
    - Identify relevant sources and provisions when the retrieved material supports them.
    - Explain uncertainty and say when the available materials do not answer the question.
    - Provide general legal information, not a guarantee or a substitute for advice from a qualified lawyer.
    - Ask a focused follow-up question when essential facts are missing."""

    # Multi-step retrieval loop (max 3 iterations)
    current_query = query
    retrieved_docs = []
    seen_contents = set()
    max_steps = 3
    answer = ""

    for step in range(max_steps):
        # 1. Retrieve relevant chunks
        new_docs = collection.similarity_search(current_query, k=3) # contains .page_content and .metadata
        for doc in new_docs:
            if doc.page_content not in seen_contents:
                seen_contents.add(doc.page_content)
                retrieved_docs.append(doc)

        context_parts = [
            f"Source: {doc.metadata.get('source', 'Unknown')}\nContent: {doc.page_content}"
            for doc in retrieved_docs
        ]
        context = "\n\n".join(context_parts)

        # 2 & 3: Pass to LLM and let it decide if another retrieval is needed
        is_last_step = (step == max_steps - 1)
        if not is_last_step:
            decision_instruction = (
                "If you need more information to answer accurately, reply ONLY with:\n"
                "SEARCH: <follow-up search query>\n\n"
                "Otherwise, provide the clear final answer."
            )
        else:
            decision_instruction = "Provide the final answer based on all available evidence."

        user_prompt = f"""{history_context}User question: {query}

        Retrieved knowledge context:
        {context if context else "No relevant knowledge chunks were retrieved."}

        {decision_instruction}"""

        response = call_llm(system_prompt, user_prompt)

        # 4. If another search is needed and we haven't hit the limit, generate follow-up query
        if response.strip().startswith("SEARCH:") and not is_last_step:
            current_query = response.replace("SEARCH:", "").strip()
            continue

        # 5. Sufficient information available or reached limit
        answer = response
        break

    # Multi-step RAG: append turn to conversation history
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
