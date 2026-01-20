# 🤖 DevMate - AI Developer Onboarding Assistant

DevMate is an intelligent RAG (Retrieval-Augmented Generation) application designed to streamline the onboarding process for new developers. It uses **AWS Bedrock (Amazon Nova Lite)** to answer questions, explain code, and test knowledge based on your project's internal documentation.

## 🎯 Problem Statement

*   **The Problem**: New developers (interns/juniors) often struggle to understand complex codebases. They spend hours reading outdated documentation or waiting for senior developers to answer basic questions, which kills productivity.
*   **Target Audience**: Interns, Junior Developers, and Freshers joining a new software team.
*   **The Solution**: DevMate acts as an "Always-On Senior Dev". It ingests the project's documentation and code, allowing the user to ask questions, generic quizzes, and get code explanations instantly without interrupting the team.

## 🌟 Features

*   **💬 AI Chat Agent**: Ask questions about your project (setup, architecture, bugs) and get instant answers.
*   **🧠 Contextual Memory**: The bot remembers previous messages for a natural conversation flow.
*   **📚 Source Citations**: Every answer includes references to the specific documents used.
*   **🎮 Gamified Quiz Mode**: A generated multiple-choice quiz to test your understanding of the knowledge base.
*   **💻 Code Explainer**: Paste complex code snippets and get line-by-line explanations suitable for juniors.
*   **🎙️ Voice Support**: Speak to DevMate using your microphone.

## 🛠️ Technology Stack

*   **Frontend**: Streamlit
*   **LLM**: Amazon Bedrock (Nova Lite v1)
*   **Embeddings**: Amazon Titan Embeddings v1
*   **Vector Store**: FAISS
*   **Orchestration**: LangChain

## 🚀 Getting Started

### Prerequisites

1.  Python 3.10+
2.  AWS Account with access to Bedrock Models (`amazon.nova-lite-v1:0` and `amazon.titan-embed-text-v1`).

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/YOUR_USERNAME/DevMate.git
    cd DevMate
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Credentials**:
    Create a `.env` file in the root directory:
    ```env
    AWS_ACCESS_KEY_ID=your_access_key
    AWS_SECRET_ACCESS_KEY=your_secret_key
    AWS_REGION=us-east-1
    BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
    ```

### Usage

1.  **Ingest Knowledge Base**:
    Place your text/PDF/Markdown files in the `data/docs/` folder.
    ```bash
    python ingest_docs.py
    ```

2.  **Run the App**:
    ```bash
    streamlit run app.py
    ```

3.  **Open Browser**: Go to `http://localhost:8501`.

## 📁 Project Structure

```
DevMate/
├── app.py              # Main Streamlit frontend
├── rag.py              # RAG logic, Quiz generation, Code explanation
├── bedrock_client.py   # AWS Bedrock client configuration
├── ingest_docs.py      # Script to create FAISS index from data
├── requirements.txt    # Python dependencies
├── .env                # API Keys (Not verified)
└── data/               # Your documentation files
```

---
*Built with ❤️ by Immanuel.*
