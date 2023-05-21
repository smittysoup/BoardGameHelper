import enum, os, shutil, openai
from typing import List
from dotenv import load_dotenv
from langchain.document_loaders import (TextLoader, UnstructuredMarkdownLoader,
                                        UnstructuredWordDocumentLoader,PyPDFLoader)
from langchain.embeddings import OpenAIEmbeddings
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
    PDF = '.pdf'

class VectorDB():
    def __init__(self,collectionName:str = "default"):        
        self._collectionName = collectionName
        self._persistDirectoryPath = r'games'
        #chroma uses from_docs, which takes a list of documents and returns a vectorstore
        #Document is a base class that contains a string(content) and metadata dictionary
        self._embedding = OpenAIEmbeddings(model="text-embedding-ada-002", deployment="Embeddings",chunk_size=1)
        self._vectorDB = Chroma(collection_name=self._collectionName, embedding_function=self._embedding,persist_directory=self._persistDirectoryPath)
        self._vectorDB.persist()

    # Process the newly uploaded files and delete them after processing
    def ProcessFile(self, movepath:str):
        '''
        main function to process the files
        1. Reads a list of files in the passed directory
        2. For each file, determines the file type and uses document loader to load the file as text
        3. Converts the text to tokens for embedding.  After conversion, moves the file to a processed folder
        4. Embeds the tokens and stores the embedding in a persistent DB
        '''
        texts = []
        for filename in os.listdir(self._persistDirectoryPath):
            print(filename) # just for debugging
            filePath = os.path.join(self._persistDirectoryPath, filename)
            # checking if it is a file
            if os.path.isfile(filePath):
                fileType = GetFileType(filePath)
                print(fileType) # just for debugging
                data = ReadData(filePath, fileType)                
                #Move the file after processing
                MoveFilePath(filePath, movepath)                
                if(data is not None):
                    texts = TextToTokens(data)
                    Embeddings(texts, self._persistDirectoryPath)      
                  
        #Move the file after processing
        def MoveFilePath(filePath:str, movepath:str):
            '''
            moves the file to a processed folder
            '''
            movepath = os.path.join(movepath, self._persistDirectoryPath)
            shutil.move(filePath, movepath)
                        
        # Get file extension
        def GetFileType(filePath: str):
            fileSplit = os.path.splitext(filePath)
            return fileSplit[1]

        # Read the data from a docx file.
        def ReadData(filePath: str, fileType: str):
            '''
            Select loader based on file type.  Convert the file to text
            '''
            loader = None
            data = None
            if(fileType == FileTypes.PDF):
                loader = PyPDFLoader(filePath)
                data = loader.load_and_split()
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
        def Embeddings(documents:List[any]):
            try:
                self._vectorDB.add_documents(documents)
                return True
            except:
                return False

    # Retrieve the docs from persisted DB
    def RetrieveDoc(self,query:str,k:int=4):
        print(self._vectorDB.get())
        retrievedDocs = self._vectorDB.max_marginal_relevance_search(query,k)
        return retrievedDocs

if __name__ == '__main__':
    vect=VectorDB("Wingspan") #update collection name as needed
    vect.ProcessFile(r'processed')