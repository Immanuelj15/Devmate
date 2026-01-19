import os
import boto3
from langchain_aws import ChatBedrockConverse
from langchain_aws import BedrockEmbeddings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_bedrock_client():
    """
    Returns a configured Bedrock client for usage with LangChain or direct Boto3 calls.
    Ensures credentials are loaded.
    """
    try:
        # Check for credentials
        if not os.getenv("AWS_ACCESS_KEY_ID") or not os.getenv("AWS_SECRET_ACCESS_KEY"):
            raise ValueError("AWS credentials not found in environment variables.")
            
        return boto3.client(
            service_name='bedrock-runtime',
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
    except Exception as e:
        print(f"Error initializing Bedrock client: {e}")
        return None

def get_llm():
    """
    Returns the LangChain ChatBedrockConverse model for text generation.
    Uses 'amazon.nova-lite-v1:0' by default.
    Using Converse API is required for Nova models.
    """
    model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")
    
    client = get_bedrock_client()
    if not client:
        return None

    # ChatBedrockConverse handles the 'messages' payload format required by Nova
    return ChatBedrockConverse(
        client=client,
        model=model_id,
        temperature=0.7,
        top_p=0.9,
        max_tokens=1000
    )

def get_embeddings():
    """
    Returns the BedrockEmbeddings model for vectorization.
    Uses 'amazon.titan-embed-text-v1'.
    """
    client = get_bedrock_client()
    if not client:
        return None
        
    return BedrockEmbeddings(
        client=client,
        model_id="amazon.titan-embed-text-v1"
    )
