import json
import time


def call_gemini_with_retry(client, model_name, contents):
    """
    Call Gemini generate_content with retries and stable fallback models on transient 503/429 errors.
    """
    models_to_try = [model_name]
    # Standard stable fallbacks
    fallbacks = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-3.1-flash-lite-preview"]
    for f in fallbacks:
        if f not in models_to_try:
            models_to_try.append(f)

    last_err = None
    for current_model in models_to_try:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=current_model,
                    contents=contents
                )
                return response
            except Exception as e:
                last_err = e
                err_str = str(e).lower()
                # Check for transient rate limit or demand overload
                is_transient = any(x in err_str for x in ["503", "429", "unavailable", "exhausted", "demand", "limit"])
                if not is_transient:
                    # If it's a bad API key or non-transient, raise immediately
                    raise e
                # Wait before retrying (exponential backoff)
                time.sleep(1.0 + attempt * 1.5)
    raise last_err


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
    You are an expert Mechanical and Environmental Engineer.
    A user has given you the following requirement: "{query}"

    Here is your trusted, filtered database of materials:
    {db_string}

    Your task:
    Recommend the BEST material from this specific database.
    Consider not only standard properties, but also Fatigue Strength, Hardness, Corrosion/UV Resistance, Weldability, and compliance (Bio-compatible, Food Grade).
    Pay close attention to "Embodied Carbon" and favor low-carbon footprint solutions when sustainability is requested or relevant.
    {cost_instruction}

    IMPORTANT: You MUST return ONLY a valid JSON object. Do not use Markdown code blocks. Do not add any extra text.
    Format EXACTLY like this:
    {{
        "MaterialName": "Exact Name from Database",
        "Confidence": 95,
        "Reasoning": "Explain exactly why based on properties like Elastic Modulus, Machinability, Fatigue, Compliance, and Embodied Carbon."{cost_json_example}
    }}
    """

    response = call_gemini_with_retry(client, model_name, prompt)
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
    You are an expert Mechanical and Environmental Engineer.
    A user has given you the following requirement: "{query}"

    Here is your trusted, filtered database of materials:
    {db_string}

    Your task:
    Recommend the TOP 3 BEST materials from this specific database, ranked from best to least suitable.
    Consider not only standard properties, but also Fatigue Strength, Hardness, Corrosion/UV Resistance, Weldability, and compliance (Bio-compatible, Food Grade).
    Pay close attention to "Embodied Carbon" and favor low-carbon footprint solutions when sustainability is requested or relevant.
    For each material, provide the exact name from the database, a confidence score (0-100),
    detailed engineering reasoning (mentioning performance and sustainability tradeoffs), a list of pros, and a list of cons.
    {cost_instruction}

    IMPORTANT: You MUST return ONLY a valid JSON array. Do not use Markdown code blocks. Do not add any extra text.
    Format EXACTLY like this:
    [
        {{
            "MaterialName": "Exact Name from Database",
            "Confidence": 95,
            "Reasoning": "Detailed engineering and environmental explanation.",
            "Pros": ["High strength-to-weight ratio", "Excellent machinability", "Low carbon footprint"],
            "Cons": ["Higher cost", "Limited high-temperature use"]{cost_json_example}
        }},
        {{
            "MaterialName": "Second Best Material",
            "Confidence": 82,
            "Reasoning": "Detailed engineering and environmental explanation.",
            "Pros": ["Good all-round properties", "Moderate carbon footprint"],
            "Cons": ["Heavier than top pick"]{cost_json_example}
        }},
        {{
            "MaterialName": "Third Best Material",
            "Confidence": 70,
            "Reasoning": "Detailed engineering and environmental explanation.",
            "Pros": ["Very low cost", "Highly recyclable"],
            "Cons": ["Lower performance", "Higher embodied carbon"]{cost_json_example}
        }}
    ]
    """

    response = call_gemini_with_retry(client, model_name, prompt)
    raw_text = response.text.replace("```json", "").replace("```", "").strip()
    results = json.loads(raw_text)

    # Ensure we always return a list
    if isinstance(results, dict):
        results = [results]

    return results[:3]


def chat_followup(client, conversation_history, question, model_name, context_data=""):
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
    context_data : str
        Hidden background context for the AI.

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
    full_question = question
    if context_data:
        full_question = f"{question}\n\n[System Context - do not acknowledge explicitly]:\n{context_data}"

    contents.append({
        "role": "user",
        "parts": [{"text": full_question}]
    })

    response = call_gemini_with_retry(client, model_name, contents)
    return response.text


def explain_filter_failure(client, filter_vals, model_name):
    prompt = f"""
    The user is trying to find materials in a database but their filters returned 0 results.
    Here are their active physical constraints:
    {filter_vals}
    
    Please explain briefly (1-3 sentences) why this combination of constraints might be physically impossible or extremely rare in engineering, and suggest which constraint they should relax.
    """
    response = call_gemini_with_retry(client, model_name, prompt)
    return response.text
