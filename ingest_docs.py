import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from bedrock_client import get_embeddings
import shutil

DATA_DIR = "data"
FAISS_INDEX_DIR = "faiss_index"

def ingest_docs():
    """
    Loads documents from 'data/' directory, splits them, and stores embeddings in FAISS.
    """
    print(f"Loading documents from {DATA_DIR}...")
    
    documents = []
    
    # Load PDFs
    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if file.endswith(".pdf"):
                    loader = PyPDFLoader(file_path)
                    documents.extend(loader.load())
                elif file.endswith(".txt"):
                    loader = TextLoader(file_path, encoding='utf-8')
                    documents.extend(loader.load())
                elif file.endswith(".md"):
                    loader = TextLoader(file_path, encoding='utf-8')
                    documents.extend(loader.load())
                elif file.endswith(".py"):
                    loader = TextLoader(file_path, encoding='utf-8')
                    documents.extend(loader.load())
                elif file.endswith((".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".json", ".java", ".cpp", ".c", ".h", ".go", ".rs", ".php", ".rb")):
                     loader = TextLoader(file_path, encoding='utf-8')
                     documents.extend(loader.load())
            except Exception as e:
                print(f"Error loading {file}: {e}")

    if not documents:
        print("No documents found to ingest.")
        return

    print(f"Loaded {len(documents)} documents.")

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    
    print("Splitting documents...")
    split_docs = text_splitter.split_documents(documents)
    print(f"Created {len(split_docs)} chunks.")

    if not split_docs:
        print("No chunks created. Documents might be empty.")
        return

    # Get embeddings
    embeddings = get_embeddings()
    if not embeddings:
        print("Failed to initialize embeddings. Check AWS credentials.")
        return

    # Create vector store
    print("Creating FAISS index...")
    try:
        vectorstore = FAISS.from_documents(split_docs, embeddings)
        
        # Save index
        vectorstore.save_local(FAISS_INDEX_DIR)
        print(f"FAISS index saved to {FAISS_INDEX_DIR}")
        
    except Exception as e:
        print(f"Error creating FAISS index: {e}")

if __name__ == "__main__":
    ingest_docs()
