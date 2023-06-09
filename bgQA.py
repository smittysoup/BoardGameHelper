import os, re
import CreateVectorDb
import openai
from dotenv import load_dotenv
from langchain.chains import ConversationChain, LLMChain,SequentialChain, TransformChain
from langchain.memory import  ConversationBufferMemory    
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI

load_dotenv()
openai.api_key=os.getenv("OPENAI_API_KEY")

class DocQA:
    def __init__(self,path):
         self._path=path
         self._persistDirectoryPath = r'games'
         self._llm = OpenAI(
                model_name="text-davinci-003",
                temperature=0
            )
         self._conv_memory = ConversationBufferMemory(
                            memory_key="chat_history_lines"
                        )
         self._vect = CreateVectorDb.VectorDB(self._path)

    def get_response_from_docs(self,summarize_chain,prompt):
        documents = self._vect.RetrieveDoc(query=prompt,k=8)

        context = ""
        for dc in documents:
            print("Document: " + dc.page_content)
            context += dc.page_content
        context = context.replace(":","-").replace("{","").replace("}","").replace("\n"," ").strip()
        #print(context)

        try:
            return summarize_chain({"input":prompt, "context":context})
        except:
            return {"response": "Unable to get response from Game Master. Please try your query again."}

    def new_chain(self):        
        #prompt for first run chain
        summarize_prompt = PromptTemplate(input_variables=['input','context'], 
                    template=("""You are an expert board game player and teacher. 
                              You have memorized all the rules to every board game ever made. 
                              Use the rules in your memory along with any other context you have to answer the players questions below. 
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
        self._conv_memory.chat_memory.add_ai_message(response["response"])

    def chat_with_user(self, prompt): 
        
        if not (prompt.endswith('.') or prompt.endswith('!') or prompt.endswith('?')):
            prompt += '?'  

        if not self._conv_memory.chat_memory.messages:
            chain = self.new_chain() 
            try:
                response = self.get_response_from_docs(chain, prompt)               
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
        #print(response["response"])

        return response

if __name__ == '__main__':
    dqa = DocQA(r'Wingspan')
    print(dqa.chat_with_user("How many players can play?"))
        
       