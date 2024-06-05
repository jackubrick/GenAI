from bs4 import BeautifulSoup
import json
from langchain_openai import AzureChatOpenAI 
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
import os
import requests
from typing import Set, List
from utils import constants as const


ddg_search = DuckDuckGoSearchAPIWrapper()
llm_00 = AzureChatOpenAI(model="genai00-gpt-35-turbo-0613", temperature=0.0) 
llm_07 = AzureChatOpenAI(model="genai00-gpt-35-turbo-0613") # Default temperature=0.7
RESULTS_PER_QUESTION = 3
SCRAPED_URLS_FILE = "./ResearchRetrievalBot/utils/scraped_urls.txt"


# Functions used for Web scraping, Retrieval, and Caching of text used later by rag.py file:

def load_scraped_urls(file_path: str) -> Set[str]:
    # If urls don't exist for this topic, create empty set:
    if not os.path.exists(file_path):
        return set() 
    with open(file_path, "r") as file:
        return set(line.strip() for line in file)
    
SCRAPED_URLS = load_scraped_urls(SCRAPED_URLS_FILE)

def save_scraped_urls(file_path: str, urls: List[str]) -> None:
    if not urls:
        return
    with open(file_path, "a") as file:     # Append the new urls.
        file.write("\n".join(urls) + "\n") # Save new urls on each line.

def web_search(query: str, num_results: int = RESULTS_PER_QUESTION) -> List[str]:
    results = ddg_search.results(query=query, max_results=num_results)

    # Save only the new urls which haven't been scraped yet:
    new_urls = [r["link"] for r in results if r["link"] not in SCRAPED_URLS]
    save_scraped_urls(SCRAPED_URLS_FILE, new_urls)
    
    return [r["link"] for r in results]

def save_scraped_text(url, page_text):
    if url not in SCRAPED_URLS:
        texts = const.TEXT_SPLITTER.split_text(page_text)
        const.DB.add_texts(texts=texts,
                        embedding=const.EMBEDDING_FUNCTION,
                        persist_directory=const.VECTOR_DB_CACHE) # Persist and cache the vectordb for RAG

def scrape_text(url: str):
    try:
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            page_text = soup.get_text(separator=" ", strip=True)

            # -> Split the text results, embed them, and save them locally to a cache of the VectorStore
            save_scraped_text(url, page_text)

            return page_text
        else:
            return f"Failed to retrieve the webpage: Status code {response.status_code}"
        
    except Exception as e:
        print(e)
        return f"Failed to retrieve the webpage: {e}"


# LangChain Chains for Research&Retrieval Bot:

# 1. URL search, Web Scraper and Summarisation Chain
scrape_runnable = RunnablePassthrough.assign(
    text=lambda x: scrape_text(x["url"])[:12000] # Limits to 12000 chars per article to keep within context window limit
) 

summarise_chain = RunnablePassthrough.assign(
    output = scrape_runnable
           | const.SUMMARY_PROMPT
           | llm_07 
           | StrOutputParser() 
) | (lambda x: f"URL: {x['url']}\n\nSUMMARY: {x['output']}") # -> f-string with 'URL: and SUMMARY: '

url_search_runnable = RunnablePassthrough.assign(
    urls = lambda x: web_search(x["question"])
) 
web_search_and_summarise_chain = url_search_runnable | (lambda x: [{"question": x["question"], "url": u} for u in x["urls"]]) | summarise_chain.map()  #  Return a new Runnable that maps a list of inputs to a list of outputs, by calling invoke() with each input.  Runnable that delegates calls to another Runnable with each element of the input sequence. It allows you to call multiple inputs with the bounded Runnable.


# 2. Chain to Generate Questions and leverage Parallelisation for speed
generate_alternative_questions_chain = const.SEARCH_PROMPT | llm_00 | StrOutputParser() | json.loads # -> Generates 3 alternative Google search prompts.

full_research_chain = generate_alternative_questions_chain | (lambda x: [{"question": q} for q in x]) | web_search_and_summarise_chain.map() 


# 3. Final Research Chain bringing everything together
runnable = RunnablePassthrough.assign(
    research_summary = full_research_chain 
                    | (lambda lst_of_lsts: "\n\n".join(["\n\n".join(lst) for lst in lst_of_lsts])) # -> string of 'URL:  SUMMARY: ' for all 9 urls scraped.
) 
chain = runnable | const.RESEARCH_ASSISTANT_PROMPT | llm_07 | StrOutputParser() 