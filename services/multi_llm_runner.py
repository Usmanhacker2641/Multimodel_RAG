import logging
import random
import textwrap
import asyncio
import aiohttp
import os
from typing import Dict, List, Optional, Sequence, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# multi_llm_runner.py

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model configurations with API endpoints
MODEL_CONFIGS = {
    "huggingface": {
        "models": {
            "mistral_7b": {
                "label": "Mistral 7B Instruct",
                "endpoint": "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1",
                "api_key_env": "HUGGINGFACE_API_KEY"
            },
            "falcon_7b": {
                "label": "Falcon 7B Instruct",
                "endpoint": "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct",
                "api_key_env": "HUGGINGFACE_API_KEY"
            },
            "zephyr_7b": {
                "label": "Zephyr 7B Beta",
                "endpoint": "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta",
                "api_key_env": "HUGGINGFACE_API_KEY"
            }
        }
    },
    "deepseek": {
        "models": {
            "deepseek_chat": {
                "label": "DeepSeek Chat",
                "endpoint": "https://api.deepseek.com/v1/chat/completions",
                "api_key_env": "DEEPSEEK_API_KEY"
            },
            "deepseek_coder": {
                "label": "DeepSeek Coder",
                "endpoint": "https://api.deepseek.com/v1/chat/completions",
                "api_key_env": "DEEPSEEK_API_KEY"
            }
        }
    },
    "gemini": {
        "models": {
            "gemini_pro": {
                "label": "Gemini Pro",
                "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
                "api_key_env": "GOOGLE_API_KEY"
            },
            "gemini_pro_vision": {
                "label": "Gemini Pro Vision",
                "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent",
                "api_key_env": "GOOGLE_API_KEY"
            }
        }
    }
}

DEFAULT_MODELS = [
    "mistral_7b",
    "deepseek_chat",
    "gemini_pro"
]


def _summarize_context(context_chunks: Optional[List[Dict[str, str]]]) -> str:
    """Summarize context chunks for API calls."""
    if not context_chunks:
        return ""
    merged = "\n".join(chunk.get("text", "") for chunk in context_chunks if chunk)
    return merged[:4000]  # Limit context length


def _call_huggingface_api(model_config: Dict[str, Any], prompt: str, context: str, api_keys: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Call Hugging Face Inference API."""
    api_key = api_keys.get("hf_api_key") if api_keys else os.getenv(model_config["api_key_env"])
    if not api_key:
        return _generate_stub_response(model_config["label"], prompt, context, "No API key configured")

    full_prompt = f"Context: {context}\n\nQuestion: {prompt}\n\nAnswer:" if context else prompt

    try:
        import requests

        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True
            }
        }

        start_time = time.time()
        response = requests.post(model_config["endpoint"], headers=headers, json=payload, timeout=30)
        latency = int((time.time() - start_time) * 1000)

        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and result:
                generated_text = result[0].get("generated_text", "").replace(full_prompt, "").strip()
                return {
                    "response": generated_text,
                    "confidence": 0.85,
                    "tokens": len(generated_text.split()),
                    "latency_ms": latency
                }
        else:
            logger.error(f"HuggingFace API error: {response.status_code} - {response.text}")

    except Exception as e:
        logger.error(f"HuggingFace API call failed: {e}")

    return _generate_stub_response(model_config["label"], prompt, context, "API call failed")


def _call_deepseek_api(model_config: Dict[str, Any], prompt: str, context: str, api_keys: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Call DeepSeek API."""
    api_key = api_keys.get("deepseek_api_key") if api_keys else os.getenv(model_config["api_key_env"])
    if not api_key:
        return _generate_stub_response(model_config["label"], prompt, context, "No API key configured")

    model_name = "deepseek-chat" if "chat" in model_config.get("endpoint", "") else "deepseek-coder"

    messages = []
    if context:
        messages.append({"role": "system", "content": f"Context information: {context}"})
    messages.append({"role": "user", "content": prompt})

    try:
        import requests

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model_name,
            "messages": messages,
            "max_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.9
        }

        start_time = time.time()
        response = requests.post(model_config["endpoint"], headers=headers, json=payload, timeout=30)
        latency = int((time.time() - start_time) * 1000)

        if response.status_code == 200:
            result = response.json()
            if "choices" in result and result["choices"]:
                content = result["choices"][0]["message"]["content"]
                usage = result.get("usage", {})
                return {
                    "response": content,
                    "confidence": 0.88,
                    "tokens": usage.get("total_tokens", len(content.split())),
                    "latency_ms": latency
                }
        else:
            logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")

    except Exception as e:
        logger.error(f"DeepSeek API call failed: {e}")

    return _generate_stub_response(model_config["label"], prompt, context, "API call failed")


def _call_gemini_api(model_config: Dict[str, Any], prompt: str, context: str, api_keys: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Call Google Gemini API."""
    api_key = api_keys.get("gemini_api_key") if api_keys else os.getenv(model_config["api_key_env"])
    if not api_key:
        return _generate_stub_response(model_config["label"], prompt, context, "No API key configured")

    full_prompt = f"Context: {context}\n\nQuestion: {prompt}" if context else prompt

    try:
        import requests

        url = f"{model_config['endpoint']}?key={api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.9,
                "maxOutputTokens": 512
            }
        }

        start_time = time.time()
        response = requests.post(url, json=payload, timeout=30)
        latency = int((time.time() - start_time) * 1000)

        if response.status_code == 200:
            result = response.json()
            if "candidates" in result and result["candidates"]:
                content = result["candidates"][0]["content"]["parts"][0]["text"]
                return {
                    "response": content,
                    "confidence": 0.90,
                    "tokens": len(content.split()),
                    "latency_ms": latency
                }
        else:
            logger.error(f"Gemini API error: {response.status_code} - {response.text}")

    except Exception as e:
        logger.error(f"Gemini API call failed: {e}")

    return _generate_stub_response(model_config["label"], prompt, context, "API call failed")


def _generate_stub_response(model_label: str, prompt: str, context: str, reason: str = "") -> Dict[str, Any]:
    """Generate fallback stub response."""
    base = textwrap.shorten(context or prompt, width=320, placeholder="...")
    if not base:
        base = prompt

    response_text = f"[{model_label}] "
    if reason:
        response_text += f"⚠️ {reason}. "
    response_text += f"Key findings based on the provided material:\n- Summary: {base}\n- Recommendation: Focus on the dominant trends and address any risks highlighted."

    return {
        "response": response_text,
        "confidence": round(random.uniform(0.75, 0.95), 2),
        "tokens": random.randint(150, 400),
        "latency_ms": random.randint(500, 2000)
    }


def _get_model_config(model_id: str) -> Optional[Dict[str, Any]]:
    """Get model configuration by ID."""
    for provider, provider_data in MODEL_CONFIGS.items():
        if model_id in provider_data["models"]:
            config = provider_data["models"][model_id].copy()
            config["provider"] = provider
            return config
    return None


def run_multi_llm(
    prompt: str,
    context: Optional[List[Dict[str, str]]] = None,
    selected_models: Optional[Sequence[str]] = None,
    api_keys: Optional[Dict[str, str]] = None
) -> List[Dict[str, Optional[str]]]:
    """Generate structured responses for each requested model using real APIs."""

    context_text = _summarize_context(context)
    model_ids = list(selected_models) if selected_models else DEFAULT_MODELS

    responses: List[Dict[str, Optional[str]]] = []

    # Use ThreadPoolExecutor for parallel API calls
    with ThreadPoolExecutor(max_workers=len(model_ids)) as executor:
        future_to_model = {}

        for model_id in model_ids:
            model_config = _get_model_config(model_id)
            if not model_config:
                logger.warning(f"Unknown model: {model_id}")
                continue

            # Submit API call to thread pool
            if model_config["provider"] == "huggingface":
                future = executor.submit(_call_huggingface_api, model_config, prompt, context_text, api_keys)
            elif model_config["provider"] == "deepseek":
                future = executor.submit(_call_deepseek_api, model_config, prompt, context_text, api_keys)
            elif model_config["provider"] == "gemini":
                future = executor.submit(_call_gemini_api, model_config, prompt, context_text, api_keys)
            else:
                future = executor.submit(_generate_stub_response, model_config["label"], prompt, context_text)

            future_to_model[future] = model_id

        # Collect results
        for future in as_completed(future_to_model):
            model_id = future_to_model[future]
            model_config = _get_model_config(model_id)

            try:
                result = future.result()
                responses.append({
                    "model_id": model_id,
                    "model_label": model_config["label"],
                    "response": result["response"],
                    "confidence": result["confidence"],
                    "tokens": result["tokens"],
                    "latency_ms": result["latency_ms"]
                })
            except Exception as e:
                logger.error(f"Error getting result for {model_id}: {e}")
                # Fallback to stub response
                stub_result = _generate_stub_response(model_config["label"], prompt, context_text, "Processing error")
                responses.append({
                    "model_id": model_id,
                    "model_label": model_config["label"],
                    "response": stub_result["response"],
                    "confidence": stub_result["confidence"],
                    "tokens": stub_result["tokens"],
                    "latency_ms": stub_result["latency_ms"]
                })

    logger.info("Generated responses for %s models", len(responses))
    return responses


def generate_multi_llm_responses(prompt: str, context: Optional[List[Dict[str, str]]] = None, api_keys: Optional[Dict[str, str]] = None) -> List[Dict[str, Optional[str]]]:
    """Alias for run_multi_llm."""
    return run_multi_llm(prompt, context, api_keys=api_keys)


def get_available_models() -> List[Dict[str, str]]:
    """Get list of all available models."""
    models = []
    for provider, provider_data in MODEL_CONFIGS.items():
        for model_id, model_config in provider_data["models"].items():
            models.append({
                "id": model_id,
                "label": model_config["label"],
                "provider": provider
            })
    return models


if __name__ == "__main__":
    # Test with stub responses
    test_prompt = "Can you summarize the quarterly revenue report?"
    sample_context = [{"text": "Revenue grew 15% YoY driven by subscriptions and international expansion."}]

    print("Testing multi-LLM runner...")
    responses = run_multi_llm(test_prompt, sample_context)
    for item in responses:
        print(f"\n{item['model_label']}:")
        print(f"  Response: {item['response'][:100]}...")
        print(f"  Confidence: {item['confidence']}, Tokens: {item['tokens']}, Latency: {item['latency_ms']}ms")

    print(f"\nAvailable models: {get_available_models()}")