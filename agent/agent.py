from langchain_community.chat_models import ChatOllama

llm = ChatOllama(
    model="qwen2",
    base_url="http://localhost:11434"
)