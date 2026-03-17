from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
import os
import asyncio
from datetime import datetime

load_dotenv()

@tool
def get_current_time():
    """Returns current time."""
    return datetime.now().strftime("%H:%M:%S")

async def test():
    api_key = os.getenv("GOOGLE_API_KEY")
    llm = ChatGoogleGenerativeAI(model="gemini-flash-lite-latest", google_api_key=api_key)
    tools = [get_current_time]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="intermediate_steps"),
    ])
    
    agent = create_openai_functions_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    print("Testing agent...")
    try:
        res = await executor.ainvoke({"input": "What time is it?", "intermediate_steps": []})
        print(f"Result: {res['output']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
