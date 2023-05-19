import enum
import os
from typing import List

import chromadb
import numpy as np
import openai
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.document_loaders import (TextLoader, UnstructuredMarkdownLoader,
                                        UnstructuredWordDocumentLoader)
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import AzureOpenAI, OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

load_dotenv()

# OpenAI Settings
os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_BASE"] = "https://cchmodels.openai.azure.com/"
os.environ["OPENAI_API_VERSION"] = "2023-03-15-preview"

openai.api_base="https://cchmodels.openai.azure.com/"
openai.api_type="azure"
openai.api_key=os.getenv("OPENAI_API_KEY")
openai.api_version="2023-03-15-preview"

class FileTypes(str, enum.Enum):
    Docx = '.docx'
    Markdown = '.md'
    Text = '.txt'

UploadPath = r'CustomerCommunities\API\uploads'

# Defining main function
def main():
    persistDirectoryPath = "Collections_v2"
    
    # Process the newly uploaded files
    ProcessFile(persistDirectoryPath)

# Process the newly uploaded files and delete them after processing
def ProcessFile(persistDirectoryPath: str):
    for filename in os.listdir(UploadPath):
        filePath = os.path.join(UploadPath, filename)
        
        # checking if it is a file
        if os.path.isfile(filePath):
            fileType = GetFileType(filePath)
            print(filePath)
            print(fileType)
            data = ReadData(filePath, fileType)
            if(data is not None):
                texts = TextToTokens(data)
                isSuccess = Embeddings(texts, persistDirectoryPath)
                
                # Delete the file after processing
                if(isSuccess):
                    os.remove(filePath)
                    
# Get file extension
def GetFileType(filePath: str):
    fileSplit = os.path.splitext(filePath)
    return fileSplit[1]

# Read the data from a docx file.
def ReadData(filePath: str, fileType: str):
    loader = None
    data = None
    if(fileType == FileTypes.Docx):
        loader = UnstructuredWordDocumentLoader(filePath)
        data = loader.load()
    elif(fileType == FileTypes.Markdown):
        loader = UnstructuredMarkdownLoader(filePath)
        data = loader.load()
    elif(fileType == FileTypes.Text):
        loader = TextLoader(filePath)
        data = loader.load()
    return data

# Convert docx content to text tokens
def TextToTokens(docContent:any):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=0)
    texts = text_splitter.split_documents(docContent)
    return texts

# Embed and store the text in a persistent DB
def Embeddings(texts:List[any], persistDirectoryPath:str):
    embedding = OpenAIEmbeddings(model="text-embedding-ada-002", deployment="Embeddings",chunk_size=1)
    vectorDB = Chroma.from_documents(documents=texts, embedding=embedding, persist_directory=persistDirectoryPath)
    return vectorDB is not None

# Retrieve the docs from persisted DB
def RetrieveDocs(query:str,persistDirectoryPath:str):
    embedding = OpenAIEmbeddings(model="text-embedding-ada-002", deployment="Embeddings",chunk_size=1)
    vectordb = Chroma(persist_directory=persistDirectoryPath, embedding_function=embedding)
    retrievedDocs = vectordb.similarity_search(query)
    return retrievedDocs

if __name__ == '__main__':
    main()