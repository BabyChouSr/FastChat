"""
Test the OpenAI compatible server
Launch:
python3 launch_openai_api_test_server.py --multimodal
"""

import openai

from fastchat.utils import run_cmd

openai.api_key = "EMPTY"  # Not support yet
openai.api_base = "http://localhost:8000/v1"


def encode_image(image):
    import base64
    from io import BytesIO
    import requests

    from PIL import Image

    if image.startswith("http://") or image.startswith("https://"):
        response = requests.get(image)
        image = Image.open(BytesIO(response.content)).convert("RGB")
    else:
        image = Image.open(image).convert("RGB")

    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_b64_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return img_b64_str


def test_list_models():
    model_list = openai.Model.list()
    names = [x["id"] for x in model_list["data"]]
    return names


def test_chat_completion(model):
    image_url = "https://picsum.photos/seed/picsum/1024/1024"
    image_url_two = "https://picsum.photos/id/237/200/300"
    base64_image_url = f"data:image/jpeg;base64,{encode_image(image_url)}"

    # No Image
    completion = openai.ChatCompletion.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Tell me about alpacas."},
                ],
            }
        ],
        temperature=0,
    )
    print(completion.choices[0].message.content)

    completion = openai.ChatCompletion.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "<image>\nWhat’s in this image?"},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        temperature=0,
    )
    print(completion.choices[0].message.content)

    completion = openai.ChatCompletion.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "<image>\nWhat’s in this image?"},
                    {"type": "image_url", "image_url": {"url": base64_image_url}},
                ],
            }
        ],
        temperature=0,
    )
    print(completion.choices[0].message.content)


def test_chat_completion_stream(model):
    image_url = "https://picsum.photos/seed/picsum/1024/1024"

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "<image>\nWhat’s in this image?"},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        }
    ]
    res = openai.ChatCompletion.create(
        model=model, messages=messages, stream=True, temperature=0
    )
    for chunk in res:
        content = chunk["choices"][0]["delta"].get("content", "")
        print(content, end="", flush=True)
    print()

if __name__ == "__main__":
    models = test_list_models()
    print(f"models: {models}")

    for model in models:
        print(f"===== Test {model} ======")
        test_chat_completion(model)
        test_chat_completion_stream(model)