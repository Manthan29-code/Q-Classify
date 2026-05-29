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
    {
        "id": "gemini-3.1-flash-lite",
        "name": "gemini-3.1-flash-lite",
        "description": "Latest, fast & intelligent",
        "recommended": True
    },
    {
        "id": "gemini-2.5-pro",
        "name": "Gemini 2.5 Pro",
        "description": "Most capable, best for complex tasks"
    },
    {
        "id": "gemini-2.0-flash",
        "name": "Gemini 2.0 Flash",
        "description": "Fast with multimodal support"
    },
    {
        "id": "gemini-1.5-pro",
        "name": "Gemini 1.5 Pro",
        "description": "1M token context, high accuracy"
    },
    {
        "id": "gemini-1.5-flash",
        "name": "Gemini 1.5 Flash",
        "description": "Balanced speed & quality"
    },
    {
        "id": "gemini-1.5-flash-8b",
        "name": "Gemini 1.5 Flash-8B",
        "description": "Fastest, most economical"
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
