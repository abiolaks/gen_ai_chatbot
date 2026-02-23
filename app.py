from datetime import datetime
import os  # operating system module to access environment variables
from dotenv import load_dotenv  # to load environment variables from a .env file
from langchain_groq import ChatGroq  # to expose llm model
from langchain_core.prompts import (
    ChatPromptTemplate,
)  # to create a prompt template for the chatbot
from pymongo import MongoClient  # to connect to MongoDB


load_dotenv()  # load environment variables from .env file
groq_api_key = os.getenv("GROQ_API_KEY")  # get the API key from environment variable
model = os.getenv("MODEL")  # get the model name from environment variable
mongo_uri = os.getenv("MONGODB_URI")  # get the MongoDB URI from environment variable


# create an instance of the ChatGroq class with the API key and model name
llm = ChatGroq(api_key=groq_api_key, model=model)
client = MongoClient(mongo_uri)  # create a MongoDB client instance

# specify the mongo database and collection to use
db = client["chat"]  # specify the database name
collection = db["users"]  # specify the collection name


# create a prompt template for the chatbot
prompt = ChatPromptTemplate.from_messages(
    {
        (
            "system",
            "You are a diet specialist. Give response tailor only to diet and nutrition related questions.if the question is not related to diet and nutrition, politely decline to answer and suggest asking a diet related question instead.",
        ),
        ("placeholder", "{history}"),
        ("user", "{questions}"),
    }
)

# attach prompt template to the llm instance
chain = prompt | llm

user_id = "user123"  # example user ID, in a real application this would be dynamic


def get_history(user_id):
    # Retrieve the last 10 messages for the user from MongoDB
    chats = collection.find({"user_id": user_id}).sort("timestamp", 1).limit(10)
    history = []

    for chat in chats:
        history.append({"role": chat["role"], "content": chat["message"]})

    return history


while True:
    question = input(
        "Enter your diet-related question (or type 'exit' to quit): "
    )  # prompt the user for a question
    if question.lower() in [
        "exit",
        "quit",
        "bye",
    ]:  # check if the user wants to exit the chatbot
        break

    history = get_history(user_id=user_id)  # get the chat history for the user

    # invoke the chatbot with a message and print the response
    response = chain.invoke(
        {"history": history, "questions": question}
    )  # send a message to the chatbot and print the response
    print(response.content)

    # Storing the user data in MongoDB
    collection.insert_one(
        {
            "user_id": user_id,
            "role": "user",
            "message": question,
            "timestamp": datetime.now(),
        }
    )

    # Storing the chatbot response in MongoDB
    collection.insert_one(
        {
            "user_id": user_id,
            "role": "assistant",
            "message": response.content,
            "timestamp": datetime.now(),
        }
    )

    # let make the llm retain memory
