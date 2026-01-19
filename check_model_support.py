try:
    from langchain_aws import ChatBedrockConverse
    print("ChatBedrockConverse is available!")
except ImportError:
    print("ChatBedrockConverse NOT found.")
    
try:
    from langchain_aws import ChatBedrock
    print("ChatBedrock is available.")
except ImportError:
    print("ChatBedrock NOT found.")
