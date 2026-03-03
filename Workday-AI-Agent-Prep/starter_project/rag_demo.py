"""
Day 1 — RAG demo: load a policy doc, embed, retrieve, and answer questions.
Run from starter_project/: python rag_demo.py
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_anthropic import ChatAnthropic
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

DATA_DIR = Path(__file__).resolve().parent / "data"
PERSIST_DIR = Path(__file__).resolve().parent / "chroma_db"


def load_and_chunk_docs(chunk_size: int = 500, overlap: int = 50):
    """Load sample HR policy and split into chunks."""
    path = DATA_DIR / "sample_hr_policy.txt"
    loader = TextLoader(str(path), encoding="utf-8")
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=len,
    )
    return splitter.split_documents(docs)


def build_retriever(top_k: int = 3):
    """Build or reuse Chroma vector store and return retriever.
    Uses local HuggingFace embeddings (no API key needed for embeddings).
    If you had a previous chroma_db from another embedder, delete the chroma_db folder to rebuild.
    """
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    if PERSIST_DIR.exists() and any(PERSIST_DIR.iterdir()):
        vectorstore = Chroma(
            persist_directory=str(PERSIST_DIR),
            embedding_function=embeddings,
        )
    else:
        chunks = load_and_chunk_docs()
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=str(PERSIST_DIR),
        )
    return vectorstore.as_retriever(search_kwargs={"k": top_k})


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Set ANTHROPIC_API_KEY in .env to run this demo.")
        return

    retriever = build_retriever(top_k=3)
    llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer using only the following context. If the answer is not in the context, say so.\n\nContext:\n{context}"),
        ("human", "{question}"),
    ])

    def format_docs(docs):
        return "\n\n".join(d.doc_page_content for d in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    print("RAG demo — HR policy Q&A (Ctrl+C to exit)\n")
    while True:
        try:
            q = input("Question: ").strip()
            if not q:
                continue
            out = chain.invoke(q)
            print(f"Answer: {out}\n")
        except KeyboardInterrupt:
            print("\nBye.")
            break


if __name__ == "__main__":
    main()
