import os
import requests
from langchain.llms import Ollama
from groq import Groq
from dotenv import load_dotenv

# Load your .env keys
load_dotenv()

# Initialize Ollama (DeepSeek model locally)
ollama_llm = Ollama(model="deepseek-coder")

# Initialize Groq (external fast LLM)
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

conversation_memory = []

# Simple function to call Ollama locally
def ask_ollama(prompt):
    response = ollama_llm(prompt)
    return response

# Simple function to call Groq for enhanced reasoning
def ask_groq(prompt):
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an expert AI lawyer specialized in reasoning and argument analysis."},
            {"role": "user", "content": prompt}
        ],
        model="mixtral-8x7b-32768"  # You can change this to other Groq models
    )
    return chat_completion.choices[0].message.content

# Final Reasoning Agent
def ai_lawyer(user_input):
    # Step 1: Use Ollama (Deepseek) to understand and analyze first
    deepseek_response = ask_ollama(f"Analyze this legal question: {user_input}")
    
    # Step 2: Use Groq for additional chain-of-thought reasoning
    enhanced_reasoning = ask_groq(f"Based on this analysis:\n\n{deepseek_response}\n\nGive a detailed, logical argument and conclusion.")

    # Save to memory
    conversation_memory.append({"user": user_input, "ollama_analysis": deepseek_response, "groq_reasoning": enhanced_reasoning})

    # Combine the answer
    final_answer = f"🔍 Deep Analysis:\n{deepseek_response}\n\n⚖️ Enhanced Legal Reasoning:\n{enhanced_reasoning}"
    return final_answer

# Example Usage
if __name__ == "__main__":
    print("👨‍⚖️ AI Lawyer is ready! Ask your legal questions.\n")
    while True:
        user_query = input("You: ")
        if user_query.lower() in ["exit", "quit"]:
            break
        response = ai_lawyer(user_query)
        print("\n" + response + "\n")
