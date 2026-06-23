"""
Q-Classify Available Models Configuration
Easy to update when Google launches new Gemini models

To add a new model:
1. Add a new dictionary to AVAILABLE_MODELS list
2. Set 'id' to the exact model name used in API calls
3. Add user-friendly 'name' and 'description'
4. Optionally mark as 'recommended': True
"""

# Available Gemini Models for selection
AVAILABLE_MODELS = [
    # Gemini 3.x series (latest generation)
    {
        "id": "gemini-3.5-flash",        # Stable model ID [web:11][web:14][web:17][web:20]
        "name": "Gemini 3.5 Flash",
        "description": "Most intelligent for agentic & coding tasks (stable).",
        "recommended": True,
    },
    {
        "id": "gemini-3.1-pro",          # Stable 3.1 Pro ID [web:12][web:15][web:18]
        "name": "Gemini 3.1 Pro",
        "description": "Advanced intelligence, complex problem solving, strong reasoning (preview).",
    },
    {
        "id": "gemini-3-flash-preview",  # Older preview identifier; still used in some guides [web:11][web:20]
        "name": "Gemini 3 Flash",
        "description": "Frontier-class performance at lower cost (preview).",
    },
    {
        "id": "gemini-3.1-flash-lite",   # 3.1 Flash-Lite ID from model listings [web:1]
        "name": "Gemini 3.1 Flash-Lite",
        "description": "Fastest & most cost-efficient Gemini 3 model, great for high-volume use.",
    },

    # Gemini 2.5 family (still widely supported)
    {
        "id": "gemini-2.5-pro",          # 2.5 Pro ID [web:3][web:6][web:9]
        "name": "Gemini 2.5 Pro",
        "description": "Most advanced 2.5 model for complex reasoning and coding.",
    },
    {
        "id": "gemini-2.5-flash",        # 2.5 Flash ID [web:3][web:6][web:9]
        "name": "Gemini 2.5 Flash",
        "description": "Best price-performance for low-latency, high-volume tasks that need reasoning.",
    },
    {
        "id": "gemini-2.5-flash-lite",   # 2.5 Flash-Lite ID [web:13][web:16][web:19]
        "name": "Gemini 2.5 Flash-Lite",
        "description": "Fastest & most budget-friendly 2.5 multimodal model.",
    },
]

# Default model (used when no selection made)
DEFAULT_MODEL = "gemini-3.1-flash-lite"

# Default temperature
DEFAULT_TEMPERATURE = 0.3

# Temperature presets for quick selection
TEMPERATURE_PRESETS = {
    "Precise": 0.1,
    "Balanced": 0.3,
    "Creative": 0.7,
    "Experimental": 1.0
}


def get_model_ids() -> list:
    """Get list of all model IDs for selectbox"""
    return [m["id"] for m in AVAILABLE_MODELS]


def get_model_display_name(model_id: str) -> str:
    """Get display name for a model ID"""
    for m in AVAILABLE_MODELS:
        if m["id"] == model_id:
            return m["name"]
    return model_id


def get_recommended_model() -> str:
    """Get the recommended model ID"""
    for m in AVAILABLE_MODELS:
        if m.get("recommended"):
            return m["id"]
    return DEFAULT_MODEL
