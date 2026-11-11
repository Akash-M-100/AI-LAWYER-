"""Build or resume the persistent Chroma legal knowledge base."""
import argparse
import hashlib
import json
import lzma
import re
from pathlib import Path

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "chroma_db"
COLLECTION_NAME = "kuku_legal_knowledge"
MANIFEST_PATH = DB_PATH / "build_manifest.json"
BATCH_SIZE = 128

# Legal sections are usually short. Judgments and training examples benefit from
# larger chunks so a provision, issue, and holding stay together in retrieval.
SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=1600,
    chunk_overlap=180,
    add_start_index=True,
    separators=["\n\n", "\n", ". ", "; ", " ", ""],
)

SKIP_JSON_FILES = {"queries_to_annotate.json", "id-act-meta.json", "id-section-meta.json"}


def source_files():
    """Select JSON files directly in the project root, excluding metadata files."""
    return sorted(
        path for path in BASE_DIR.glob("*.json")
        if path.is_file() and path.name.lower() not in SKIP_JSON_FILES
    )


def json_value_documents(value, source, record_id="root"):
    """Yield text records from key-to-text legal JSON files."""
    if isinstance(value, dict):
        for key, child in value.items():
            yield from json_value_documents(child, source, str(key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from json_value_documents(child, source, f"{record_id}_{index}")
    elif isinstance(value, str):
        text = value.strip()
        if text:
            if record_id != "root":
                text = f"{record_id}\n{text}"
            yield Document(
                page_content=text,
                metadata={"source": source, "record_id": record_id},
            )


def format_record(value):
    """Preserve JSON field labels to make court cases/examples searchable."""
    if isinstance(value, dict):
        fields = []
        for key, item in value.items():
            if str(key).lower() in {"id", "custom_id", "record_id"}:
                continue
            if isinstance(item, (str, int, float)):
                text = str(item).strip()
            else:
                text = json.dumps(item, ensure_ascii=False)
            if text:
                fields.append(f"{key}: {text}")
        return "\n".join(fields)
    if isinstance(value, str):
        return value.strip()
    return json.dumps(value, ensure_ascii=False)


def fingerprint(path):
    stat = path.stat()
    return f"{stat.st_size}:{stat.st_mtime_ns}"


def stable_id(document):
    source = document.metadata["source"]
    record_id = document.metadata["record_id"]
    start = document.metadata.get("start_index", 0)
    raw = f"{source}\0{record_id}\0{start}\0{document.page_content}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Clear the collection and rebuild it from every selected source file.",
    )
    args = parser.parse_args()

    DB_PATH.mkdir(parents=True, exist_ok=True)
    if MANIFEST_PATH.exists():
        try:
            manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            manifest = {}
    else:
        manifest = {}

    client = chromadb.PersistentClient(path=str(DB_PATH))
    if args.rebuild:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
        manifest = {}
        MANIFEST_PATH.write_text("{}", encoding="utf-8")
    vectorstore = Chroma(client=client, collection_name=COLLECTION_NAME)
    pending = []
    total_added = 0

    def flush():
        nonlocal total_added
        if not pending:
            return
        ids = [stable_id(document) for document in pending]
        vectorstore.add_documents(documents=pending, ids=ids)
        total_added += len(pending)
        pending.clear()

    files = source_files()
    if not files:
        raise RuntimeError("No legal JSON or training JSONL.XZ files were found.")

    for file_number, path in enumerate(files, start=1):
        relative_path = path.relative_to(BASE_DIR).as_posix()
        signature = fingerprint(path)
        if not args.rebuild and manifest.get(relative_path) == signature:
            print(f"[{file_number}/{len(files)}] Skipping unchanged {relative_path}")
            continue

        print(f"[{file_number}/{len(files)}] Indexing {relative_path}", flush=True)
        before = total_added

        def queue_record(document):
            chunks = SPLITTER.split_documents([document])
            for chunk in chunks:
                pending.append(chunk)
                if len(pending) >= BATCH_SIZE:
                    flush()

        if path.name.lower().endswith(".jsonl.xz"):
            with lzma.open(path, "rt", encoding="utf-8") as stream:
                for line_number, line in enumerate(stream, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    text = format_record(record)
                    if text:
                        queue_record(Document(
                            page_content=text,
                            metadata={"source": relative_path, "record_id": f"line_{line_number}"},
                        ))
        else:
            try:
                value = json.loads(path.read_text(encoding="utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                print(f"  Skipped unreadable JSON: {exc}")
                continue
            for document in json_value_documents(value, relative_path):
                queue_record(document)

        flush()
        manifest[relative_path] = signature
        MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(f"  Added {total_added - before} chunks")

    print(f"Knowledge base ready: {vectorstore._collection.count()} total chunks; {total_added} added this run.")


if __name__ == "__main__":
    main()
