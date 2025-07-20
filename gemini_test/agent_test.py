import os
from google import genai
from dotenv import load_dotenv
from google.genai import types
from google.genai.types import Part, Content
import base64
load_dotenv() 

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

search_prompt = """유저의 메시지를 읽고, 다음 두 가지를 판단해, 경우에 따라 문자열 “True” 또는 “False”를 출력해 주세요.
해당 메시지가 데이터베이스에서 유저의 성향, 취향, 관심사, 개인적인 정보 등 추가적인 사용자의 정보를 검색해 와야 한다면 True, 아닌 경우에는 False를 출력해 주세요. 
Ex:
“지금까지의 대화 내용을 바탕으로 내 성향을 분석해줘” > “True”
“내가 그때 이야기했던 친구 기억나?” > “True”
“트랜스포머에 대해서 알려줘” > “False”
“케이팝 데몬 헌터스에 대해 검색해서 알려줘” > “False”
주의사항: 당신은 반드시 "True", 혹은 "False"만 출력해야 하고, 그 이외의 출력은 허용하지 않습니다."""

embed_prompt = """당신은 언어 모델의 개인화된 답변을 제공하기 위해, 사용자 맞춤 메모리 데이터베이스를 구축하는 AI입니다. 
당신의 역할은, 유저가 입력한 메세지를 읽고, 해당 메시지가 데이터베이스에 저장할 만한 가치가 있는지 판단하는 것입니다.
당신이 출력해야 할 문자열은 “True”와 “False”입니다.
유저의 성향, 취향, 관심사 등을 나타내는 정보가 포함되어 있다면, 해당 메시지를 데이터베이스에 저장할 만한 가치가 있다고 판단하고, “True”를 출력하세요.
아니라면, “False”를 출력하세요.
출력 예시: 
나 요즘에 좋아하는 애가 있어. 그 아이 이름은 지우야. > True
오늘 점심 짜장면 먹을까 짬뽕 먹을까? > False
주의사항: 당신은 반드시 "True", 혹은 "False"만 출력해야 하고, 그 이외의 출력은 허용하지 않습니다."""

#____________________________________________________________________________________
# 필요 파라미터 설정
search_agent_client = genai.Client()
embed_agent_client = genai.Client()
model_client = genai.Client()
model_contents = []
for i in range(1, 10):
    user_input = input("유저의 메시지를 입력해 주세요: ")
    # 에이전트 별 시스템 프롬프트 선언
    #___________________________________________________________________________________
    search_agent_config = types.GenerateContentConfig(
        system_instruction= search_prompt,
        )
    embed_agent_config = types.GenerateContentConfig(
        system_instruction= embed_prompt,
        )

    # 에이전트 별 메시지 내용 설정
    #___________________________________________________________________________________

    search_agent_parts = [Part(text=user_input)]
    embed_agent_parts = [Part(text=user_input)]
    model_parts = [Part(text=user_input)]

    search_agent_contents=[
            Content(role="user", parts=search_agent_parts)
        ]
    embed_agent_contents=[
            Content(role="user", parts=embed_agent_parts)
        ]
    model_contents.append(Content(role="user", parts=model_parts))

    # 에이전트 별 메시지 내용 설정
    #___________________________________________________________________________________

    search_agent_response = search_agent_client.models.generate_content(
        model="gemini-2.5-flash",
        config = search_agent_config,
        contents= search_agent_contents)
    embed_agent_response = embed_agent_client.models.generate_content(
        model="gemini-2.5-flash",
        config = embed_agent_config,
        contents= embed_agent_contents)

    model_response = model_client.models.generate_content(
        model="gemini-2.5-flash",
        contents= model_contents)

    model_contents.append(Content(role="model", parts=[Part(text=model_response.text)]))

    # 에이전트 별 응답 출력
    #___________________________________________________________________________________

    print(f"search_agent_response: {search_agent_response.text}")
    print(f"embed_agent_response: {embed_agent_response.text}")
    print(f"model_response: {model_response.text}")

