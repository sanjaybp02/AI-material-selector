import json


def get_single_recommendation(client, db_string, query, model_name, cost_instruction=""):
    """
    Ask AI for a single best material recommendation.

    Returns
    -------
    dict with keys: MaterialName, Confidence, Reasoning, (optionally EstimatedCostINR)
    """
    cost_json_example = ""
    if cost_instruction:
        cost_json_example = ',\n                    "EstimatedCostINR": 250'

    prompt = f"""
    You are an expert Mechanical Engineer.
    A user has given you the following requirement: "{query}"

    Here is your trusted, filtered database of materials:
    {db_string}

    Your task:
    Recommend the BEST material from this specific database.
    {cost_instruction}

    IMPORTANT: You MUST return ONLY a valid JSON object. Do not use Markdown code blocks. Do not add any extra text.
    Format EXACTLY like this:
    {{
        "MaterialName": "Exact Name from Database",
        "Confidence": 95,
        "Reasoning": "Explain exactly why based on properties like Elastic Modulus or Machinability."{cost_json_example}
    }}
    """

    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )

    raw_text = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(raw_text)


def get_top3_recommendations(client, db_string, query, model_name, cost_instruction=""):
    """
    Ask AI for top 3 material recommendations with pros/cons.

    Returns
    -------
    list of dicts, each with: MaterialName, Confidence, Reasoning, Pros, Cons,
    (optionally EstimatedCostINR)
    """
    cost_json_example = ""
    if cost_instruction:
        cost_json_example = ',\n            "EstimatedCostINR": 250'

    prompt = f"""
    You are an expert Mechanical Engineer.
    A user has given you the following requirement: "{query}"

    Here is your trusted, filtered database of materials:
    {db_string}

    Your task:
    Recommend the TOP 3 BEST materials from this specific database, ranked from best to least suitable.
    For each material, provide the exact name from the database, a confidence score (0-100),
    detailed engineering reasoning, a list of pros, and a list of cons.
    {cost_instruction}

    IMPORTANT: You MUST return ONLY a valid JSON array. Do not use Markdown code blocks. Do not add any extra text.
    Format EXACTLY like this:
    [
        {{
            "MaterialName": "Exact Name from Database",
            "Confidence": 95,
            "Reasoning": "Detailed engineering explanation.",
            "Pros": ["High strength-to-weight ratio", "Excellent machinability"],
            "Cons": ["Higher cost", "Limited high-temperature use"]{cost_json_example}
        }},
        {{
            "MaterialName": "Second Best Material",
            "Confidence": 82,
            "Reasoning": "Detailed engineering explanation.",
            "Pros": ["Good all-round properties"],
            "Cons": ["Heavier than top pick"]{cost_json_example}
        }},
        {{
            "MaterialName": "Third Best Material",
            "Confidence": 70,
            "Reasoning": "Detailed engineering explanation.",
            "Pros": ["Very low cost"],
            "Cons": ["Lower performance"]{cost_json_example}
        }}
    ]
    """

    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )

    raw_text = response.text.replace("```json", "").replace("```", "").strip()
    results = json.loads(raw_text)

    # Ensure we always return a list
    if isinstance(results, dict):
        results = [results]

    return results[:3]


def chat_followup(client, conversation_history, question, model_name):
    """
    Send a follow-up question with conversation context.

    Parameters
    ----------
    conversation_history : list[dict]
        List of {"role": "user"|"model", "parts": [{"text": "..."}]} dicts.
    question : str
        The new user question.
    model_name : str
        The model to use.

    Returns
    -------
    str
        The AI's response text.
    """
    # Build the conversation for the API
    contents = []
    for msg in conversation_history:
        contents.append({
            "role": msg["role"],
            "parts": [{"text": msg["text"]}]
        })

    # Add the new question
    contents.append({
        "role": "user",
        "parts": [{"text": question}]
    })

    response = client.models.generate_content(
        model=model_name,
        contents=contents
    )

    return response.text
