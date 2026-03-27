import os
from google import genai
from google.genai import types
from utils import QueryIntent, COLUMNS_SCHEMA
import json

def parse_query_to_intent(query: str, chat_history: list, client: genai.Client) -> QueryIntent:
    """Uses LLM to parse natural language query into a structured Intent JSON, considering conversation history."""
    
    # Format recent history
    history_str = ""
    if chat_history:
        history_str = "Recent Conversation Context:\n"
        for msg in chat_history[-5:]: # Keep last 5 messages for context
            history_str += f"{msg['role'].capitalize()}: {msg['content']}\n"
    
    system_instruction = f"""
    You are an expert Data Engineer. Your job is to convert natural language queries into a structured database intent.
    The database contains real estate customer leads.
    
    {COLUMNS_SCHEMA}
    
    {history_str}
    
    Rules for conditions:
    - If user asks for 'in Pune', do NOT add a location filter, because all data is in Pune. Only filter location if they mention specific areas like 'Kharadi', 'Hinjewadi'.
    - If they ask for 'high-intent', you might filter 'Last Call Status' == 'Connected'.
    - If they say "last call", make sure to use the "Last Call Connected Time" column, NOT "Expected Possession".
    - 'Expected Possession' is formatted like 'Jun 2026'. Use "contains" for month matching (e.g. "contains", "Feb").
    - 'Last Call Connected Time' is formatted like 'DD-MM-YYYY HH:MM'. If filtering this by a specific month (e.g., Feb 2026), use "contains" with "02-2026". If filtering a specific date, use "contains" with "DD-MM-YYYY".
    - If they use keywords like 'near', 'around', or 'close to' a date, use the 'near' operator to filter within +/- 7 days (e.g., operator: "near", value: "15-02-2026").
    - Ensure numerical data like 90 lakhs is converted to numbers (9000000).
    - If no conditions match, leave the 'conditions' array empty.
    - IMPORTANT: If the user's current query is a follow-up (e.g. "what about 2BHKs?"), incorporate the filters established in the 'Recent Conversation Context' into the new JSON intent!
    
    You MUST output valid JSON ONLY matching exactly this Pydantic schema:
    {{
       "intent_type": "filter | filter_count | average | sum | min | max | summary | median | sort_top | sort_bottom",
       "conditions": [
           {{"column": "Exact Column Name", "operator": "== | != | > | < | >= | <= | contains | near", "value": "value"}}
       ],
       "target_column": "Column Name for math ops (null if none)",
       "limit": "Integer for top/bottom N items, like 5 for 'top 5' (null if none)",
       "nth": "Integer for Nth largest/lowest item, like 2 for '2nd largest' (null if none)"
    }}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[query],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                temperature=0.0
            ),
        )
        return QueryIntent.parse_raw(response.text)
    except Exception as e:
        print(f"Error parsing query: {e}")
        return None

def generate_nl_response(query: str, query_result: str, client: genai.Client) -> str:
    """Takes the raw data result and the user's query and generates a human-friendly string."""
    system_instruction = """
    You are a Data API. You must provide ONLY the direct answer to the user's query based on the raw result. 
    DO NOT include conversational filler like "Here is the answer".
    If the raw result is a number, format it as a short direct sentence.
    If the raw result contains "Found X matched records", output exactly "X records were found matching your criteria." and do not evaluate anything else.
    If the Result literally says 'None', output: "No exact match found."
    """
    
    prompt = f"User Query: {query}\n\nRaw Result Engine Output: \n{query_result}\n\nDirect Answer:"
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.1
            )
        )
        return response.text
    except Exception as e:
        return f"Error generating response: {e}"
