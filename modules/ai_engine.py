import json
import re
import time

_GEMINI_KEY_RE = re.compile(r"^AIza[0-9A-Za-z_\-]{35,}$")


def looks_like_gemini_key(key):
    """Free, instant, local format check for Google AI Studio / Gemini API
    keys (standard Google API key shape: 'AIza' prefix, 39 chars total —
    matched here with a bit of slack on length in case Google ever issues
    a slightly longer one). Used to reject obviously-not-a-key text (a
    placeholder, a stray word, anything typed while testing) before ever
    reporting the sidebar status as 'Connected' — confirmed live: typing
    plain text into the API key field previously flipped the status green
    immediately, since the old check was just `bool(api_key)`."""
    key = (key or "").strip()
    return bool(_GEMINI_KEY_RE.match(key))


def validate_api_key(api_key, model_name, timeout_ms=8000):
    """Live check that an API key actually authenticates with Google,
    without spending generation quota/tokens — fetches metadata for one
    model (client.models.get) instead of calling generate_content.
    Confirmed live: an invalid key raises the same underlying error a
    real generate_content call would (google.genai.errors.ClientError,
    400 INVALID_ARGUMENT, reason 'API_KEY_INVALID', message 'API key not
    valid. Please pass a valid API key.') — this call is just far
    cheaper and faster than a full generation request.

    Returns
    -------
    str
        "valid"   — Google confirmed the key authenticates.
        "invalid" — Google explicitly rejected the key itself.
        "unknown" — the call failed for any other reason (network,
                    timeout, transient rate limit, the specific model
                    being temporarily unavailable, ...). This is NOT
                    proof the key is bad — callers must not report it
                    as an invalid key on this basis alone.
    """
    from google import genai
    from google.genai import types

    try:
        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=timeout_ms),
        )
        client.models.get(model=model_name)
        return "valid"
    except Exception as e:
        msg = str(e).lower()
        if any(s in msg for s in ("api_key_invalid", "api key not valid", "permission_denied", "unauthenticated")):
            return "invalid"
        return "unknown"


def _require_text(response):
    """Gemini can return a response with no usable text (blocked by safety
    filters, hit a token limit before finishing, etc.) — response.text is
    then None. Every caller here immediately calls .replace()/returns it
    directly, which would surface as a raw 'NoneType has no attribute
    replace' AttributeError to the user instead of an explanation. Raise a
    clear, actionable error instead."""
    text = getattr(response, "text", None)
    if not text:
        finish_reason = None
        try:
            finish_reason = response.candidates[0].finish_reason
        except Exception:
            pass
        detail = f" (finish_reason: {finish_reason})" if finish_reason else ""
        raise ValueError(
            f"The AI returned no usable response{detail} — it may have been "
            f"blocked by content filters or hit a length limit. Try "
            f"rephrasing your request."
        )
    return text


def call_gemini_with_retry(client, model_name, contents):
    """
    Call Gemini generate_content with retries and stable fallback models on transient 503/429 errors
    or model deprecation/404 errors.
    """
    models_to_try = [model_name]
    # Standard stable fallbacks (active Gemini models)
    fallbacks = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-2.5-pro",
        "gemini-1.5-pro",
    ]
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

                # If model is deprecated / retired / 404 NOT_FOUND, immediately try next fallback model
                is_not_found = any(x in err_str for x in [
                    "404", "not_found", "no longer available", "not found", "deprecated"
                ])
                if is_not_found:
                    break

                # Check for transient rate limit or demand overload
                is_transient = any(x in err_str for x in ["503", "429", "unavailable", "exhausted", "demand", "limit"])
                if not is_transient:
                    # If it's a bad API key or non-transient error, raise immediately
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
    raw_text = _require_text(response).replace("```json", "").replace("```", "").strip()
    return json.loads(raw_text)


def get_top3_recommendations(client, db_string, query, model_name, cost_instruction=""):
    """
    Ask AI for material recommendations (top 1 to 3 based on available candidates in db_string).

    Returns
    -------
    list of dicts, each with: MaterialName, Confidence, Reasoning, Pros, Cons,
    (optionally EstimatedCostINR)
    """
    db_lines = [line.strip() for line in db_string.strip().split('\n') if line.strip()]
    num_available = max(0, len(db_lines) - 1)  # subtract header row

    if num_available <= 0:
        return []

    target_count = min(3, num_available)

    cost_json_example = ""
    if cost_instruction:
        cost_json_example = ',\n            "EstimatedCostINR": 250'

    if target_count == 1:
        task_str = "Recommend the ONLY BEST material from this specific database. Since only 1 material is available in the filtered database, your JSON array MUST contain EXACTLY 1 object. DO NOT repeat or duplicate the material under any circumstances."
    elif target_count == 2:
        task_str = "Recommend the TOP 2 BEST materials from this specific database, ranked from best to second best. Since only 2 materials are available in the filtered database, your JSON array MUST contain EXACTLY 2 objects. Every recommended material MUST be unique and distinct. DO NOT duplicate any material."
    else:
        task_str = "Recommend the TOP 3 BEST materials from this specific database, ranked from best to least suitable. Return up to 3 items in the JSON array. Every recommended material MUST be unique and distinct. DO NOT duplicate any material."

    prompt = f"""
    You are an expert Mechanical and Environmental Engineer.
    A user has given you the following requirement: "{query}"

    Here is your trusted, filtered database of materials ({num_available} total candidate(s)):
    {db_string}

    Your task:
    {task_str}
    Consider not only standard properties, but also Fatigue Strength, Hardness, Corrosion/UV Resistance, Weldability, and compliance (Bio-compatible, Food Grade).
    Pay close attention to "Embodied Carbon" and favor low-carbon footprint solutions when sustainability is requested or relevant.
    For each material, provide the exact name from the database, a confidence score (0-100),
    detailed engineering reasoning (mentioning performance and sustainability tradeoffs), a list of pros, and a list of cons.
    {cost_instruction}

    IMPORTANT: You MUST return ONLY a valid JSON array containing EXACTLY {target_count} unique material item(s). Do not use Markdown code blocks. Do not add any extra text.
    Format EXACTLY like this:
    [
        {{
            "MaterialName": "Exact Name from Database",
            "Confidence": 95,
            "Reasoning": "Detailed engineering and environmental explanation.",
            "Pros": ["High strength-to-weight ratio", "Excellent machinability"],
            "Cons": ["Higher cost", "Limited high-temperature use"]{cost_json_example}
        }}
    ]
    """

    response = call_gemini_with_retry(client, model_name, prompt)
    raw_text = _require_text(response).replace("```json", "").replace("```", "").strip()
    results = json.loads(raw_text)

    # Ensure we always return a list
    if isinstance(results, dict):
        results = [results]

    # Deduplicate results strictly by normalized material name
    seen_names = set()
    unique_results = []
    for item in results:
        mname = item.get("MaterialName", "").strip().lower()
        if mname and mname not in seen_names:
            seen_names.add(mname)
            unique_results.append(item)

    return unique_results[:target_count]


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
    return _require_text(response)


def explain_filter_failure(client, filter_vals, model_name):
    prompt = f"""
    The user is trying to find materials in a database but their filters returned 0 results.
    Here are their active physical constraints:
    {filter_vals}
    
    Please explain briefly (1-3 sentences) why this combination of constraints might be physically impossible or extremely rare in engineering, and suggest which constraint they should relax.
    """
    response = call_gemini_with_retry(client, model_name, prompt)
    return response.text
