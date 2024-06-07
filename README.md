# Research and Retrieval Bot

#### This Streamlit Application aims to enable comprehensive online research on a variety of tasks, as well as automating the Retrieval process in RAG.

This project aims to streamline manual research, providing reliable, comprehensive, and unbiased reports. Unlike default llm chatbots, this Research and Retrieval Bot aims to avoid outdated information and hallucinations, ensuring well-rounded answers for any research topic you provide it. It produces a consolidated Research Article and all documents it uses to inform its research will be persisted to a local cache of a Chroma vector database, which can be queried against using the RAG chain and chatbot, allowing users to ask more in-depth questions on content mentioned in the research article.  
<img width="662" alt="image" src="https://github.com/jackubrick/GenAI/assets/171839384/4d2e7202-0a47-4520-992c-c5a448346968">
  
#### Getting Started
- pip install the python packages in the requirements.txt file
- Download a version of pytorch (https://pytorch.org/) depending on the specifications of your pc (by default this application assumes `device='cuda'`
  
Here is an example of asking it about the new 'GPT 4o' model (**full article available in markdown in 'results' folder**):  
![image](https://github.com/jackubrick/GenAI/assets/171839384/38e25c3a-7fac-4ec3-9483-017996892419)
