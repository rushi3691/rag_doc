import os
from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from langchain_text_splitters import RecursiveCharacterTextSplitter
from llama_index.core.node_parser import LangchainNodeParser
from llama_index.core.schema import Document
from llama_index.core import PromptTemplate
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.chat_engine import CondenseQuestionChatEngine
from llama_index.llms.anthropic import Anthropic
import chainlit as cl

os.environ["ANTHROPIC_API_KEY"] = ""

class llamaRAG:
    def __init__(self, docs=[]):
        self.llm = Anthropic(model="claude-3-5-sonnet-20240620")
        self.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5",
            cache_folder="./cache"
        )
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=36,
            length_function=len,
            is_separator_regex=False,
        )
        self.parser = LangchainNodeParser(text_splitter)
        self.docs = docs
        self.index = None

    def get_vector_store(self, vector_db_path="./vector_store"):
        if not os.path.exists(vector_db_path):
            nodes = self.parser.get_nodes_from_documents(self.docs)
            index_mkd = VectorStoreIndex(nodes, embed_model=self.embed_model)
            index_mkd.storage_context.persist(persist_dir=vector_db_path)
        else:
            ctx = StorageContext.from_defaults(persist_dir=vector_db_path)
            index_mkd = load_index_from_storage(ctx, embed_model=self.embed_model)
        self.index = index_mkd
        return index_mkd

    def get_query_engine(self, vector_db_path="./vector_store"):
        if self.index is None:
            self.index = self.get_vector_store(vector_db_path)
        return self.index.as_query_engine(
            response_mode="tree_summarize",
            llm=self.llm
        )

def read_markdown_files(directory):
    docs = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    doc_id = os.path.relpath(file_path, directory).replace("/", "_").replace("\\", "_")
                    doc = Document(doc_id=doc_id, text=f.read())
                    docs.append(doc)
    return docs

# Specify the directory containing the Markdown files
directory = "../../hackathon/documentation/docs"
docs = read_markdown_files(directory)

custom_prompt = PromptTemplate(
    """\
Given a conversation (between Human and Assistant) and a follow up message from Human, \
rewrite the message to be a standalone question that captures all relevant context \
from the conversation.
<Chat History>
{chat_history}
<Follow Up Message>
{question}
<Standalone question>
"""
)

rag = llamaRAG(docs)
query_engine = rag.get_query_engine(vector_db_path="./store")
chat_engine = CondenseQuestionChatEngine.from_defaults(
    query_engine=query_engine,
    condense_question_prompt=custom_prompt,
    verbose=True,
    llm=rag.llm
)

@cl.on_chat_start
async def start():
    pass

@cl.on_message
async def main(message: cl.Message):
    query = message.content
    streaming_response = chat_engine.stream_chat(message=query)
    
    resp, msg = "", cl.Message(content="")
    for token in streaming_response.response_gen:
        resp += token + " "
        await msg.stream_token(token)
    await msg.update()
    
    print(resp)