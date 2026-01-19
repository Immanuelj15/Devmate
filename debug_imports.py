try:
    import langchain_core
    print(f"langchain_core version: {langchain_core.__version__}")
    import langchain_core.memory
    print("langchain_core.memory imported successfully")
except ImportError as e:
    print(f"ImportError: {e}")

try:
    from langchain.chains import RetrievalQA
    print("RetrievalQA imported successfully")
except ImportError as e:
    print(f"RetrievalQA ImportError: {e}")
