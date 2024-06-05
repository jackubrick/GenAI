import streamlit as st
import pandas as pd
import numpy as np
from utils import research_retrieval as ra
import re
import time
from langchain_openai import AzureChatOpenAI
from wonderwords import RandomWord, Defaults


def letters_and_numbers(article):
    article = re.sub(r'[ ]+', '_', article.strip())  
    article = re.sub(r'[^a-zA-Z0-9d_]+', '', article)
    return article


st.title("Research and Retrieval Bot")
st.write('Choose a Research Topic ')

if "messages" not in st.session_state:
    st.session_state.messages = []

if st.button("Generate Random Research Topic"):
    
    #rw = RandomWord(noun=Defaults.NOUNS)
    rw = RandomWord()
    random_word = rw.word()

    llm_random = AzureChatOpenAI(model="genai00-gpt-35-turbo-0613", temperature=0.7) 
    random_topic = llm_random.invoke(f"Generate one cutting-edge research topic related to this Topic: {random_word}.  Be succinct.")

    st.write(random_topic.content)

# Displays all produced messages on the screen:
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input(placeholder="What topic would you like me to research?"):

    # --------------------------
    start_time = time.time()
    # --------------------------

    user_message = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_message)

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        response = ra.chain.invoke({"question": prompt})
        st.markdown(response)

        # -----------------------------------------------------
        elapsed_time = time.time() - start_time
        print(f"Execution time: {elapsed_time:.6f} seconds")
        # -----------------------------------------------------

        # Rename and save:
        article = letters_and_numbers(prompt)
        with open(f'ResearchRetrievalBot/results/{article}.md', 'w') as file:
            file.write(response)

    assistant_message = {"role": "assistant", "content": response}
    st.session_state.messages.append(assistant_message)