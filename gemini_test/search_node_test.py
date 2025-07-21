import os
from google import genai
from dotenv import load_dotenv
from google.genai import types
from google.genai.types import Part, Content
import base64
load_dotenv() 

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

search_prompt = """유저의 메시지를 읽고, 다음 두 가지를 판단해, 경우에 따라 문자열 “True” 또는 “False”를 출력해 주세요.
해당 메시지가 최신 정보를 검색해 와야 한다면 True, 아닌 경우에는 False를 출력해 주세요.
Ex:
"케데헌에 대해 알려줘" > "True"
"미적분학에 대해서 알려줘" > "False"
주의사항: 당신은 반드시 "True", 혹은 "False"만 출력해야 하고, 그 이외의 출력은 허용하지 않습니다."""

def is_search_required(user_input: str, client: genai.Client) -> bool:
    """
    Role: 사용자의 입력이 Qdrant에서 벡터 검색을 수행해야 하는지 판단하는 함수
    arguments:
        user_input: 사용자의 입력 메시지
        client: genai.Client 객체
    Return: bool - 검색이 필요한 경우 True, 아닌 경우 False
    """
    search_agent_config = types.GenerateContentConfig(
        system_instruction=search_prompt,
    )
    search_agent_parts = [Part(text=user_input)]
    search_agent_contents = [
        Content(role="user", parts=search_agent_parts)
    ]
    search_agent_response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=search_agent_config,
        contents=search_agent_contents
    )
    return search_agent_response.text == "True"

#____________________________________________________________________________________
# 필요 파라미터 설정
model_client = genai.Client()
model_contents = []
for i in range(1, 10):
    user_input = input("유저의 메시지를 입력해 주세요: ")

    model_parts = [Part(text=user_input)]
    model_contents.append(Content(role="user", parts=model_parts))

    is_search = is_search_required(user_input, client)
    if is_search:
        # Define the grounding tool
        grounding_tool = types.Tool(
        google_search=types.GoogleSearch()
        )
        # Configure generation settings
        config = types.GenerateContentConfig(
        tools=[grounding_tool]
        )

    response = model_client.models.generate_content(
        model="gemini-2.5-flash",
        config=config if is_search else None,
        contents=model_contents
    )
    if is_search:
        citations = []
        titles = []
        chunks = response.candidates[0].grounding_metadata.grounding_chunks
        if chunks:
            for chunk in chunks:
                uri = chunk.web.uri
                title = chunk.web.title
                citations.append(uri)
                titles.append(title)
    model_contents.append(Content(role="model", parts=[Part(text=response.text)]))
    print(f"Response: {response.text}")
    if is_search:
        print(f"Citations: {citations}")
        print(f"Titles: {titles}")
    




