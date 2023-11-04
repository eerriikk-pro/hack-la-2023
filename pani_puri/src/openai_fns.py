import os

import openai
from langchain import OpenAI, PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import LanceDB
from parse_files import load_summarize_chain, parse, parse_to_string, text_to_docs

openai.api_key = os.environ.get("OPENAI_API_KEY", "default")
