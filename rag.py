import os
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from bedrock_client import get_embeddings, get_llm

FAISS_INDEX_DIR = "faiss_index"

FAISS_INDEX_DIR = "faiss_index"

def ask_devmate(question, role, exp, history=""):
    """
    Main function to query the RAG system.
    Args:
        question: User's question
        role: User's role
        exp: User's experience
        history: Formatted chat history string
    """
    try:
        # Initialize components
        embeddings = get_embeddings()
        llm = get_llm()
        
        if not embeddings or not llm:
            return {"answer": "Error: Failed to initialize AWS Bedrock components. Check your credentials.", "sources": []}
            
        if not os.path.exists(FAISS_INDEX_DIR):
            return {"answer": f"Error: FAISS index not found at {FAISS_INDEX_DIR}. Please run 'Re-ingest Knowledge Base' first.", "sources": []}
            
        # Load Vector Store
        vectorstore = FAISS.load_local(FAISS_INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        
        # Create Prompt with Role/Experience + History context
        final_prompt_template = f"""
        Human: You are DevMate, a helpful developer onboarding assistant.
        
        User Profile:
        - Role: {role}
        - Experience: {exp}
        
        Previous Conversation:
        {history}
        
        Use the following pieces of context to answer the question at the end.
        
        Context: {{context}}
        
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
            return_source_documents=True
        )
        
        # Run Chain
        result = chain.invoke({"query": question})
        
        # Extract Answer and Sources
        answer = result['result']
        source_docs = result.get('source_documents', [])
        
        # Format sources
        sources = []
        for doc in source_docs:
            source_name = doc.metadata.get('source', 'Unknown')
            # Only keep the filename, not the full path
            source_name = os.path.basename(source_name)
            sources.append(source_name)
            
        # Remove duplicates
        sources = list(set(sources))
        
        return {"answer": answer, "sources": sources}
        
    except Exception as e:
        return {"answer": f"Error: {str(e)}", "sources": []}
