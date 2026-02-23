from datetime import datetime
import os  # operating system module to access environment variables
from dotenv import load_dotenv  # to load environment variables from a .env file
from langchain_groq import ChatGroq  # to expose llm model
from langchain_core.prompts import (
    ChatPromptTemplate,
)  # to create a prompt template for the chatbot
from pymongo import MongoClient  # to connect to MongoDB
from fastapi import FastAPI  # to create a FastAPI application instance
from fastapi.middleware.cors import CORSMiddleware  # to handle CORS in FastAPI
from pydantic import BaseModel  # to define data models for FastAPI


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

app = FastAPI()  # create a FastAPI application instance


class ChatRequest(BaseModel):
    user_id: str
    question: str


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # allow all origins, you can specify specific origins if needed
    allow_methods=["*"],  # allow all HTTP methods
    allow_headers=["*"],  # allow all headers
    allow_credentials=True,  # allow credentials (cookies, authorization headers, etc.)
)


# create a prompt template for the chatbot
prompt = ChatPromptTemplate.from_messages(
    {
        (
            "system",
            "You are a diet specialist. Give response tailor only to diet and nutrition related questions.if the question is not related to diet and nutrition, politely decline to answer and suggest asking a diet related question instead.",
        ),
        ("placeholder", "{history}"),
        ("user", "{question}"),
    }
)

# attach prompt template to the llm instance
chain = prompt | llm

# example user ID, in a real application this would be dynamic


def get_history(user_id):
    # Retrieve the last messages for the user from MongoDB
    chats = collection.find({"user_id": user_id}).sort("timestamp", 1)
    history = []

    for chat in chats:
        history.append((chat["role"], chat["message"]))
    return history


# defining routes for the FastAPI application
@app.get("/")
def home():
    return {"message": "Welcome to the Diet Chatbot API!"}


@app.post("/chat")
def chat(request: ChatRequest):
    history = get_history(request.user_id)  # get the chat history for the user
    response = chain.invoke(
        {"history": history, "question": request.question}
    )  # send a message to the chatbot and print the response
    # Storing the user data in MongoDB
    collection.insert_one(
        {
            "user_id": request.user_id,
            "role": "user",
            "message": request.question,
            "timestamp": datetime.now(),
        }
    )

    # Storing the chatbot response in MongoDB
    collection.insert_one(
        {
            "user_id": request.user_id,
            "role": "assistant",
            "message": response.content,
            "timestamp": datetime.now(),
        }
    )

    return {"response": response.content}
