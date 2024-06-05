from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
# from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.embeddings import HuggingFaceBgeEmbeddings


MODEL_NAME = "BAAI/bge-small-en-v1.5"

EMBEDDING_FUNCTION = HuggingFaceBgeEmbeddings(
    model_name=MODEL_NAME,
    model_kwargs={'device': 'cuda'},
    encode_kwargs={'normalize_embeddings': True} # set True to compute cosine similarity
)

VECTOR_DB_CACHE = "ResearchRetrievalBot/chroma_db"
DB = Chroma(persist_directory=VECTOR_DB_CACHE, embedding_function=EMBEDDING_FUNCTION)

TEXT_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size = 1000, # 500
    chunk_overlap  = 100,
    length_function = len,
    is_separator_regex = False,
)

RAG_TEMPLATE = """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:
"""
# prompt = hub.pull("rlm/rag-prompt")
RAG_PROMPT = ChatPromptTemplate.from_template(RAG_TEMPLATE)



SUMMARY_TEMPLATE = """{text} 
-----------
Using the above text, answer in short the following question: 
> {question}
-----------
if the question cannot be answered using the text, simply summarize the text. Include all factual information, numbers, stats etc if available."""  
SUMMARY_PROMPT = ChatPromptTemplate.from_template(SUMMARY_TEMPLATE)


SEARCH_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "user",
            "Write 3 google search queries to search online that form an "
            "objective opinion from the following: {question}\n"
            "You must respond with a list of strings in the following format: "
            '["query 1", "query 2", "query 3"].',
        ),
    ]
)


WRITER_SYSTEM_PROMPT = "You are an AI critical thinker research assistant. Your sole purpose is to write well written, critically acclaimed, objective and structured reports on given text." 
RESEARCH_REPORT_TEMPLATE = """Information:
--------
{research_summary}
--------
Using the above information, answer the following question or topic: "{question}" in a detailed report -- \
The report should focus on the answer to the question, should be well structured, informative, \
in depth, with facts and numbers if available and a minimum of 1,200 words.
You should strive to write the report as long as you can using all relevant and necessary information provided.
You must write the report with markdown syntax.
You MUST determine your own concrete and valid opinion based on the given information. Do NOT deter to general and meaningless conclusions.
Write all used source urls at the end of the report, and make sure to not add duplicated sources, but only one reference for each.
You must write the report in apa format.
Please do your best, this is very important to my career."""  
RESEARCH_ASSISTANT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", WRITER_SYSTEM_PROMPT),
        ("user", RESEARCH_REPORT_TEMPLATE),
    ]
)