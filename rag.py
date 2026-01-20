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
        # We use a PromptTemplate where we pass everything as variables to the chain
        
        template = """
        Human: You are DevMate, a helpful developer onboarding assistant.
        
        User Profile:
        - Role: {role}
        - Experience: {exp}
        
        Previous Conversation:
        {history}
        
        Use the following pieces of context to answer the question at the end.
        
        Context: {context}
        
        Question: {question}
        
        Assistant:"""
        
        PROMPT = PromptTemplate(
            template=template,
            input_variables=["context", "question", "role", "exp", "history"]
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
        # We need to pass the other variables in the validation dict too
        result = chain.invoke(
            {"query": question, "role": role, "exp": exp, "history": history}
        )
        
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

def generate_quiz():
    """
    Generates a 3-question quiz based on the knowledge base.
    """
    try:
        # Initialize components
        embeddings = get_embeddings()
        llm = get_llm()
        
        if not embeddings or not llm:
            return None
            
        vectorstore = FAISS.load_local(FAISS_INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5}) # Get broad context
        
        # We need to retrieve some random/broad context to base the quiz on.
        # Since we can't search for "everything", we'll search for key project terms.
        # A simple hack: search for "overview features setup"
        docs = retriever.invoke("project overview features setup")
        context_text = "\n".join([doc.page_content for doc in docs])
        
        prompt_template = f"""
        Human: based on the following context, generate a quiz with 3 multiple-choice questions.
        Return the result correctly formatted in JSON with the keys: "question", "options" (list of 4 strings), and "answer" (the correct string).
        Do not output any markdown code blocks or text, just the raw JSON list.
        
        Context:
        {context_text}
        
        Assistant:"""
        
        # Direct generation
        response = llm.invoke(prompt_template)
        
        # Parse JSON
        import json
        import re
        
        content = response.content.strip()
        # Clean potential markdown
        content = re.sub(r'```json', '', content)
        content = re.sub(r'```', '', content)
        
        quiz_data = json.loads(content)
        return quiz_data
        
    except Exception as e:
        print(f"Quiz Generation Error: {e}")
        return []

def explain_code(code_snippet):
    """
    Explains a code snippet line-by-line using the LLM.
    """
    try:
        llm = get_llm()
        if not llm:
            return "Error: LLM not initialized."
            
        prompt = f"""
        Human: You are an expert senior developer. Please explain the following code snippet to a junior developer.
        Break it down line-by-line or by logical blocks. Explain WHY it is done this way, not just WHAT it does.
        
        Code Snippet:
        ```
        {code_snippet}
        ```
        
        Assistant:"""
        
        response = llm.invoke(prompt)
        return response.content
        
    except Exception as e:
        return f"Error explaining code: {str(e)}"
