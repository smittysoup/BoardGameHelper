import os, re
from flask_cors import CORS, cross_origin
import ReadDoc
import openai
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
from langchain.chains import ConversationChain, LLMChain,SequentialChain, TransformChain
from langchain.memory import  ConversationBufferMemory    
from langchain.prompts import PromptTemplate
from langchain.schema import  SystemMessage
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

UploadPath = './UploadedFiles'

llm_davinci = AzureOpenAI(
    engine="davinci",
    temperature=0
)

conv_memory = ConversationBufferMemory(
    memory_key="chat_history_lines"
)
 

def get_response_from_docs(prompt,summarize_chain,path):
    documents = ReadDoc.RetrieveDocs(query=prompt, persistDirectoryPath=path)

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


def chat_with_user(prompt, path):    
    
    if not conv_memory.chat_memory.messages:
        
        summarize_prompt = PromptTemplate(input_variables=['input','context'], 
                    template=("""You are an expert board game player and teacher. You have memorized all the rules to every board game ever made. Use the rules in your memory along with any other context you have to answer the players questions. 
                              \n\nRules:\n{context}\nPlayer Question:\n{input}""")
                    )
        summarize_chain = LLMChain(llm=llm_davinci, prompt=summarize_prompt,output_key="response", verbose=True) 
        
        conv_memory.chat_memory.add_user_message(prompt)
        generated_text=get_response_from_docs(prompt, summarize_chain, path)
        conv_memory.chat_memory.add_ai_message((generated_text['response']).replace("\n\n"," "))
        y=""
        for i in conv_memory.chat_memory.messages:
                y += i.content
        
        print("New Memory: " + y)
    else:  
        y=""
        for i in conv_memory.chat_memory.messages:
                y += i.content
        
        print("existing Memory: " + y)

        _DEFAULT_TEMPLATE = ("""
            {chat_history_lines}            
            \n\nRules:\n{context}\nPlayer Question:\n{input}
            """)
            
        PROMPT = PromptTemplate(
            input_variables=["chat_history_lines", "input", "context"], 
            template=(_DEFAULT_TEMPLATE),
            template_format='f-string',
            validate_template=True
        )

        #conversation = ConversationChain(
        conversation = ConversationChain(
            prompt=PROMPT,
            llm=llm_davinci, 
            memory=conv_memory,
            verbose=True)
        generated_text = get_response_from_docs(prompt, conversation, path)

    generated_text["response"] = generated_text["response"].replace("\nAI: ", "").strip()

    print(generated_text)
    return generated_text


def UploadFile():
    if not os.path.isdir(UploadPath):
        # UploadPath doesn't exist, create it
        os.makedirs(UploadPath)
        
    file = request.files['file']
    if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(UploadPath, filename))
            return "File Saved"
        
       
if __name__ == '__main__':
    chat_with_user()