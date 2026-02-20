import os # operating system module to access environment variables
from dotenv import load_dotenv # to load environment variables from a .env file
from langchain_groq import ChatGroq # to expose llm model
from langchain_core.prompts import ChatPromptTemplate # to create a prompt template for the chatbot
from pymongo import MongoClient # to connect to MongoDB


load_dotenv() # load environment variables from .env file
groq_api_key = os.getenv("GROQ_API_KEY") # get the API key from environment variable
model = os.getenv("MODEL") # get the model name from environment variable
mongo_uri = os.getenv("MONGODB_URI") # get the MongoDB URI from environment variable


# create an instance of the ChatGroq class with the API key and model name
llm = ChatGroq(api_key=groq_api_key, model=model)
client = MongoClient(mongo_uri) # create a MongoDB client instance

# specify the mongo database and collection to use
db = client["chat"] # specify the database name
collection = db["users"] # specify the collection name



# create a prompt template for the chatbot
prompt = ChatPromptTemplate.from_messages(
    {
        ("system", "You are a diet specialist. Give response tailor only to diet and nutrition related questions.if the question is not related to diet and nutrition, politely decline to answer and suggest asking a diet related question instead."),
        ("user", "{questions}")
    }
)

# attach prompt template to the llm instance
chain = prompt | llm

userid = "user123" # example user ID, in a real application this would be dynamic

while True:
    question = input("Enter your diet-related question (or type 'exit' to quit): ") # prompt the user for a question
    if question.lower() in ["exit", "quit", "bye"]: # check if the user wants to exit the chatbot
        break

    # invoke the chatbot with a message and print the response
    response = chain.invoke({"questions": question}) # send a message to the chatbot and print the response
    
    collection.insert_one({"user_id": userid, "question": question, "response": response}) # store the user question and chatbot response in MongoDB
print(response.content) # print the content of the response