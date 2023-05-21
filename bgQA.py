import os, re
import CreateVectorDb
import openai
from dotenv import load_dotenv
from langchain.chains import ConversationChain, LLMChain,SequentialChain, TransformChain
from langchain.memory import  ConversationBufferMemory    
from langchain.prompts import PromptTemplate
from langchain.llms import AzureOpenAI


load_dotenv()

os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_BASE"] = "https://cchmodels.openai.azure.com/"
os.environ["OPENAI_API_VERSION"] = "2023-03-15-preview"
os.environ["OPENAI_API_KEY"] = "fb8a38d152ca43a9a84b7b9e996bc1d0"

openai.api_base="https://cchmodels.openai.azure.com/"
openai.api_type="azure"
openai.api_key=os.getenv("OPENAI_API_KEY")
openai.api_version="2023-03-15-preview"

class DocQA:
    def __init__(self,path):
         self._path=path
         self._persistDirectoryPath = r'games'
         self._llm = AzureOpenAI(
                engine="davinci",
                temperature=0
            )
         self._conv_memory = ConversationBufferMemory(
                            memory_key="chat_history_lines"
                        )
         self._vect = CreateVectorDb.VectorDB(self._path)

    def get_response_from_docs(self,summarize_chain):
        documents = self._vect.RetrieveDocs(query=self._prompt,k=8)

        context = ""
        for dc in documents:
            print("Document: " + dc.page_content)
            context += dc.page_content
        context = context.replace(":","-").replace("{","").replace("}","").replace("\n"," ").strip()
        #print(context)

        try:
            return summarize_chain({"input":self._prompt, "context":context})
        except:
            return {"response": "Unable to get response from Game Master. Please try your query again."}

    def new_chain(self):        
        #prompt for first run chain
        summarize_prompt = PromptTemplate(input_variables=['input','context'], 
                    template=("""You are an expert board game player and teacher. You have memorized all the rules to every board game ever made. Use the rules in your memory along with any other context you have to answer the players questions. 
                            \n\nRules:\n{context}\nPlayer Question:\n{input}""")                        )
            
        return LLMChain(
                    llm=self._llm, 
                    prompt=summarize_prompt,
                    output_key="response", 
                    verbose=True) 

    def existing_chain(self):
        #prompt for existing chain
        summarize_prompt = PromptTemplate(input_variables=['chat_history_lines','input','context'], 
                    template=("""{chat_history_lines}            
                            \n\nRules:\n{context}\nPlayer Question:\n{input}""")                        )
            
        return ConversationChain(
                prompt=summarize_prompt,
                llm=self._llm, 
                memory=self._conv_memory,
                output_key="response",
                verbose=True)
    
    def update_memories(self,prompt,response):
        self._conv_memory.chat_memory.add_user_message(prompt)
        self._conv_memory.chat_memory.add_ai_message(response)

    def chat_with_user(self, prompt):    

        if not self._conv_memory.chat_memory.messages:
            chain = self.new_chain() 
            try:
                response=self.get_response_from_docs(chain, prompt)               
            except:
                response = {"response": "Unable to get response from Game Master. Please try your query again."}
            self.update_memories(prompt,response)

        else:  
            chain = self.existing_chain()
            try:
                response=self.get_response_from_docs(chain, prompt)               
            except:
                response = {"response": "Unable to get response from Game Master. Please try your query again."}

        response["response"] = response["response"].replace("\nAI: ", "").strip()

        return response

        
       