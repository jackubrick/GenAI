from langchain_openai import AzureChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from utils import constants as const


llm_00 = AzureChatOpenAI(model="genai00-gpt-35-turbo-0613", temperature=0.0) 

retriever = const.DB.as_retriever(k=5) 

qa_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | const.RAG_PROMPT
    | llm_00
    | StrOutputParser()
)