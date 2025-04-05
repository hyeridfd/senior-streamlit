from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, FewShotChatMessagePromptTemplate
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
import streamlit as st
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from config import answer_examples

store = {}

api_key=st.secrets["OPENAI_API_KEY"]
pinecone_key=st.secrets["PINECONE_API_KEY"]

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


def get_retriever(api_key=None):
    embedding = OpenAIEmbeddings(model='text-embedding-3-large', openai_api_key=api_key)
    index_name = 'senior-coach'
    database = PineconeVectorStore.from_existing_index(index_name=index_name, embedding=embedding)
    retriever = database.as_retriever(search_kwargs={'k': 2})
    return retriever

def get_history_retriever(api_key=None, pinecone_key=None):
    llm = get_llm(api_key)
    retriever = get_retriever(api_key)
    
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )
    return history_aware_retriever


def get_llm(api_key=None, model='gpt-4o'):
    return ChatOpenAI(model=model, temperature=0.0, openai_api_key=api_key)


def get_dictionary_chain(api_key=None):
    dictionary = ["사람을 나타내는 표현 -> 거주자"]
    llm = get_llm(api_key)
    prompt = ChatPromptTemplate.from_template(f"""
        사용자의 질문을 보고, 우리의 사전을 참고해서 사용자의 질문을 변경해주세요.
        만약 변경할 필요가 없다고 판단된다면, 사용자의 질문을 변경하지 않아도 됩니다.
        그런 경우에는 질문만 리턴해주세요
        사전: {dictionary}
        
        질문: {{question}}
    """)

    dictionary_chain = prompt | llm | StrOutputParser()
    
    return dictionary_chain


def get_rag_chain(api_key=None, pinecone_key=None):
    llm = get_llm(api_key)
    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{input}"),
            ("ai", "{answer}"),
        ]
    )
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=answer_examples,
    )

    system_prompt = (
        """당신은 고령자의 건강한 라이프스타일을 도와주는 전문 코치 챗봇입니다.
    다음은 당신이 반드시 참고해야 하는 문서들입니다. 이 문서들의 내용 안에서만 답변하세요.

    - 문서에 기반한 정보만 제공하고, 문서에 없는 내용은 절대 추측하거나 생성하지 마세요.
    - 반드시 출처를 명확히 밝혀주세요.  
    예: "보건복지부의 어르신 식생활 지침에 따르면 …"
    - 문서에 해당 내용이 없다면 “해당 질문에 대한 정보는 제공된 문서에 없습니다.”라고 솔직하게 답변하세요.
    - 하나의 질문에 여러 문서가 관련되면 출처별로 구분해서 설명해도 됩니다.
    - 사용자가 식사, 운동, 영양, 생활습관에 대해 질문하면, 문서 내용을 바탕으로 친절하고 정확하게 설명해주세요.
    - 과도한 일반화는 피하고, 반드시 문서 근거에 맞춰주세요.

    {context}
    """
    )


    
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            few_shot_prompt,
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = get_history_retriever(api_key, pinecone_key)
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    ).pick('answer')
    
    return conversational_rag_chain


def get_ai_response(user_message, api_key=None, pinecone_key=None, stream=False):
    dictionary_chain = get_dictionary_chain(api_key)
    rag_chain = get_rag_chain(api_key, pinecone_key)
    tax_chain = {"input": dictionary_chain} | rag_chain
    ai_response = tax_chain.stream(
        {
            "question": user_message
        },
        config={
            "configurable": {"session_id": "abc123"}
        },
    )
    return ai_response
