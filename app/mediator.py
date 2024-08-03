
from django.conf import settings
from django.contrib.auth.models import User

from app.models import Chat, ChatHistory, ConflictInfo

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI

import json
import time
from typing import Sequence


def generate_questions(party, parties, conflict_description):

    query = f"""You are an expert mediator in charge of mediating a conflict between {parties}. You are preparing \
    to begin a mediation and your task is to carefully read the description of the conflict and \
    generate a list of questions related to the conflict to have a clear understanding of what the problem is. \
    Please generate at least five questions for {party}, to clear understant his or her point of view, \
    The questions should be specific to the conflict to be mediated, but below are some example questions that you can use: \
    What is the problem? \
    Since when has it occurred? \
    Why do you think it happens? \
    What have you done to solve it? \
    What results have you obtained? \
    Why have you opted for the mediation service? \
    How do you see the interests and positions of the other party? \
    What do you think it really takes for the other party to reach an agreement with you on this issue? \
    What expectations do you have from this mediation process? \
    This is the description of the conflict from {party}'s point of view: {conflict_description}"
    """
    
    class Question(BaseModel):
        question: str = Field(description="The question to ask")
        
    class Questions(BaseModel):
        questions: Sequence[Question] = []

    parser = JsonOutputParser(pydantic_object=Questions)
    
    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    model = ChatGoogleGenerativeAI(model="gemini-pro")
    chain = prompt | model | parser
    results = chain.invoke({"query": query})

    return results["questions"]


def generate_user_answer(name, conflict_description, chat_history):

    latest_chat_history_message = chat_history.last()

    query = f"""You are {name}, and your task is to answer the question of a mediator \
    who is helping you resolve a conflict in which you are involved. \
    Answer the question briefly, concisely and clearly, using a maximum of 50 words in one paragraph. \
    This is the context of the conflict: {conflict_description} \
    And this is the question you have to answer: {latest_chat_history_message}
    """
    messages = [HumanMessage(content=query)]

    prompt = ChatPromptTemplate.from_messages([MessagesPlaceholder(variable_name="messages"),])
    model = ChatGoogleGenerativeAI(model="gemini-pro")
    chain = prompt | model

    response = chain.invoke({"messages": messages})
    return response.content


def check_if_answered(unanswered_question, chat_history):
    messages_summary = ""
    for chat_history_message in chat_history:
        messages_summary += chat_history_message.message + "\n"

    query = f"""Review the following list of messages from an interview, \
    and try to find the answer to this question in them:{unanswered_question}. \
    If you find it return the answer, if not return 'not found'. \
    This is the chat history: {messages_summary}"""

    prompt = ChatPromptTemplate.from_messages([MessagesPlaceholder(variable_name="messages"),])
    model = ChatGoogleGenerativeAI(model="gemini-pro")
    chain = prompt | model

    messages = [HumanMessage(content=query)]

    response = chain.invoke({"messages": messages})
    return response.content


def check_if_question(last_chat_history_message):
    query = f"""Review the following message and answer 'true' if it is a question, \
    or 'false' if it is not a question. This is the message:{last_chat_history_message}"""

    prompt = ChatPromptTemplate.from_messages([MessagesPlaceholder(variable_name="messages"),])
    model = ChatGoogleGenerativeAI(model="gemini-pro")
    chain = prompt | model

    messages = [HumanMessage(content=query)]

    response = chain.invoke({"messages": messages})
    return response.content


def generate_caucus_answer(name, parties, conflict_description, chat_history):

    query = f"""You are an expert mediator in charge of mediating a conflict between {parties}. \
    Now you are talking with {name}, and you have to respond in the best way using your experience as a mediator. \
    This is the description of the conflict from {name}'s point of view: {conflict_description} \
    """
    messages = [HumanMessage(content=query)]

    for chat_history_message in chat_history:
        if chat_history_message.is_llm == True:
            messages.append(AIMessage(content=chat_history_message.message))
        else:
            messages.append(HumanMessage(content=chat_history_message.message))

    prompt = ChatPromptTemplate.from_messages([MessagesPlaceholder(variable_name="messages"),])
    model = ChatGoogleGenerativeAI(model="gemini-pro")
    chain = prompt | model

    response = chain.invoke({"messages": messages})
    return response.content


def merge_conflict_infos(conflict_infos):
    query = f"""Below you have the descriptions of a conflict by each of the parties involved. \
    Read each description carefully and make as detailed a summary as possible about what \
    the problem is between them. The description of each part is between html tags with the person's name as the tag name.
    """

    for conflict_info in conflict_infos:
        query += "<" + conflict_info.created_by.first_name + " " + conflict_info.created_by.last_name + ">"
        query += conflict_info.description
        query += "</" + conflict_info.created_by.first_name + " " + conflict_info.created_by.last_name + ">\n"

    messages = [HumanMessage(content=query)]

    prompt = ChatPromptTemplate.from_messages([MessagesPlaceholder(variable_name="messages"),])
    model = ChatGoogleGenerativeAI(model="gemini-pro")
    chain = prompt | model

    response = chain.invoke({"messages": messages})
    return response.content


def generate_multiparty_intro(conflict_info_summary, parties, chat_description, chat_history):
    query = f"""You are MrFusion, are an expert mediator in charge of mediating a conflict between {parties}. \
    Below you have a summary of the conflict to be discussed: {conflict_info_summary} \n
    Your task is to present yourself as a mediator of the conflict, summarize the topic to be discussed \
    and speak to each of the participants to explain how you we going to proceed to reach an agreement \
    that satisfies all parties. Please also note that the purpose of this particular chat is as follows: {chat_description}. \
    """

    messages = [HumanMessage(content=query)]

    for chat_history_message in chat_history:
        if chat_history_message.is_llm == True:
            messages.append(AIMessage(content=chat_history_message.message))
        else:
            messages.append(HumanMessage(content=chat_history_message.message))

    prompt = ChatPromptTemplate.from_messages([MessagesPlaceholder(variable_name="messages"),])
    model = ChatGoogleGenerativeAI(model="gemini-pro")
    chain = prompt | model

    response = chain.invoke({"messages": messages})
    return response.content


def generate_multiparty_answer(conflict_info_summary, parties, chat_description, chat_history):

    query = f"""You are Mr Fusion, an expert mediator in charge of mediating a conflict between {parties}. \
    Your task is to review the history of messages and generate a message to follow the conversation \
    with the intention to help the parties to reach an agreement. \
    Remain neutral, do not take the side of any party.\
    Respond briefly, concisely and clearly, using a maximum of 50 words in one paragraph. \
    Very important: return only the response of Mr Fusion, not the responses of the other participants of the conflict.
    Below you have a summary of the conflict to be discussed: {conflict_info_summary} \n
    The goal for this particular chat is the following: {chat_description}. \
    """

    messages = [HumanMessage(content=query)]

    for chat_history_message in chat_history:
        if chat_history_message.is_llm == True:
            messages.append(AIMessage(content=chat_history_message.message))
        else:
            messages.append(HumanMessage(content=chat_history_message.message))

    prompt = ChatPromptTemplate.from_messages([MessagesPlaceholder(variable_name="messages"),])
    model = ChatGoogleGenerativeAI(model="gemini-pro")
    chain = prompt | model

    response = chain.invoke({"messages": messages})
    content = response.content

    return content


def check_if_agreement(conflict_info_summary, parties, chat_history):

    class Agreement(BaseModel):
        is_agreement: str = Field(description="Yes or no depending on whether an agreement has been reached or not")
        agreement_description: str = Field(description="The description of the agreement they have reached")

    messages_summary = ""
    for chat_history_message in chat_history:
        if chat_history_message.is_llm == False:
            messages_summary += chat_history_message.message + "\n"

    query = f"""The following conversation is between different parties to a conflict. Your task is to analyze all the \
    messages and determine whether an agreement to the conflict has been reached or not. \
    Not any agreement is valid, only answer yes if a specific and detailed agreement has been reached that resolves the conflict, \
    if there are only good intentions to reach an agreement, answer no.
    If yes, return the explanation of the agreement reached, asking if everyone agrees. If not, only return "no".
    This is a summary of the conflict to be discussed: {conflict_info_summary} \n
    This is the list of messages between the parties to a conflict:{messages_summary}"""

    parser = JsonOutputParser(pydantic_object=Agreement)
    
    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    model = ChatGoogleGenerativeAI(model="gemini-pro")
    chain = prompt | model

    response = chain.invoke({"query": query})
    return response.content


def generate_multiparty_closing(conflict_info_summary, parties, agreement):
    query = f"""After a long mediation between {parties} in which you were the mediator, the parties to a conflict \
    have reached an agreement. Make a summary of the agreement they have reached, and if everyone agrees, \
    close the session by congratulating the participants and thanking them for their collaboration.
    This is the conflict summary: {conflict_info_summary}
    This is the agreement they have reached: {agreement}"""

    messages = [HumanMessage(content=query)]

    prompt = ChatPromptTemplate.from_messages([MessagesPlaceholder(variable_name="messages"),])
    model = ChatGoogleGenerativeAI(model="gemini-pro")
    chain = prompt | model

    response = chain.invoke({"messages": messages})
    return response.content


def gentlify(chat_message):
    query = f"""Please, without changing the meaning of the message, soften the following text \
    to make it more gentle and less aggressive: {chat_message}"""

    query = f"""The following message may be offensive or aggressive, please soften the tone \
    to make it more conciliatory but without changing the meaning of the message. \
    If you cannot do this, return the message without modifying it. Message to gentlify: {chat_message}"""

    messages = [HumanMessage(content=query)]

    prompt = ChatPromptTemplate.from_messages([MessagesPlaceholder(variable_name="messages"),])
    model = ChatGoogleGenerativeAI(model="gemini-pro")
    chain = prompt | model

    response = chain.invoke({"messages": messages})
    return response.content
