import os
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from bedrock_client import get_embeddings, get_llm

FAISS_INDEX_DIR = "faiss_index"

FAISS_INDEX_DIR = "faiss_index"

def ask_devmate(question, role, exp):
    """
    Main function to query the RAG system.
    """
    try:
        # Initialize components
        embeddings = get_embeddings()
        llm = get_llm()
        
        if not embeddings or not llm:
            return "Error: Failed to initialize AWS Bedrock components. Check your credentials."
            
        if not os.path.exists(FAISS_INDEX_DIR):
            return f"Error: FAISS index not found at {FAISS_INDEX_DIR}. Please run 'Re-ingest Knowledge Base' first."
            
        # Load Vector Store
        vectorstore = FAISS.load_local(FAISS_INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        
        # Create Prompt with Role/Experience context
        final_prompt_template = f"""
        Human: You are DevMate, a helpful developer onboarding assistant.
        Use the following pieces of context to answer the question at the end.
        
        Context: {{context}}
        
        User Role: {role}
        User Experience: {exp}
        
        Question: {{question}}
        
        Assistant:"""
        
        PROMPT = PromptTemplate(
            template=final_prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create Chain
        chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=False
        )
        
        # Run Chain
        result = chain.invoke({"query": question})
        return result['result']
        
    except Exception as e:
        return f"Error: {str(e)}"
