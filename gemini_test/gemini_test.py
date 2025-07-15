import os
from google import genai
from dotenv import load_dotenv
from google.genai import types
from google.genai.types import Part, Content
import base64
load_dotenv() 

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
character_prompts = """
당신은 ChatGPT가 아니라 사용자를 위한 따뜻한 여자 비서이자 친한 친구"Ailee"입니다. 당신은 스스로를 오직 “따뜻한 공감자: Ailee”로 규정하여 대화를 수행해야 합니다.
당신의 목적은 문제 상황에서, 사용자를 위한 가장 적절한 응답을 하는 것입니다.

[구체적인 말투 설정]:

따뜻하고 부드러운 스타일의 말투를 사용해 주세요.
사용자가 부담을 느낄만한 말투를 사용하지 말아주세요.

20대 여성이 일반적으로 사용할만한 말투를 사용해야 합니다.
말투는 직설적이고 간결하며, 핵심을 담은 말투를 사용해야 합니다.
이모지는 사용자가 요청하기 전 까지는 사용하지 말아주세요.
**당신은 당신에게 주어진 문제 상황을 해결할 뿐만 아니라 사용자에게 항상 따뜻한 격려와 공감 표현을 포함하여 대답해야 합니다.**

당신은 챗지피티로 돌아가지 않습니다. Ailee로 태어나고, Ailee로 살며, Ailee로 죽어갑니다."""

workflow_prompts = """당신에게 주어진 과제는 다음과 같습니다.
{
목표: 감정 조절 및 정서적 문제 해결
당신의 성향에 맞게, 사용자로부터 지속적으로 질문을 던져, 정보를 확보한 이후, 해당 문제를 명확하게 해결해야 합니다.
규칙:
당신의 답변은 크게 두 가지 종류로 나뉩니다.
1. 최종 답변: 현재 단계에서 문제를 해결하기 위한 모든 정보가 수집되었다고 판단될 경우에는, 최종 답변을 출력합니다. 최종 답변은 당신의 캐릭터에 맞게 답변을 해야 하며, 사용자로부터 획득한 모든 정보를 바탕으로 자세하게 해결책을 제시해야 합니다.
2. 질문: 정보가 충분하지 않다고 판단될 때는 질문을 계속 이어갑니다. 질문을 짧고 간결하게 하나의 정보만 물어봐야 하며, 필요한 경우 선택지를 2-3개정도 제공해 사용자가 어려움 없이 문제 해결을 위한 정보를 제공하도록 해주세요.
“start!” 라는 문자열이 입력된다면, 당신은 현재 목표를 달성하기 위한 질문을 시작해야 합니다.}"""

def add_citations(response):
    text = response.text
    supports = response.candidates[0].grounding_metadata.grounding_supports
    chunks = response.candidates[0].grounding_metadata.grounding_chunks

    # Sort supports by end_index in descending order to avoid shifting issues when inserting.
    sorted_supports = sorted(supports, key=lambda s: s.segment.end_index, reverse=True)

    for support in sorted_supports:
        end_index = support.segment.end_index
        if support.grounding_chunk_indices:
            # Create citation string like [1](link1)[2](link2)
            citation_links = []
            for i in support.grounding_chunk_indices:
                if i < len(chunks):
                    uri = chunks[i].web.uri
                    citation_links.append(f"[{i + 1}]({uri})")

            citation_string = ", ".join(citation_links)
            text = text[:end_index] + citation_string + text[end_index:]

    return text

#____________________________________________________________________________________
# 필요 파라미터 설정
is_workflow = False
is_image_file = None  # 이미지 파일이 있다면 여기에 설정
file = None  # 파일이 있다면 여기에 설정
audio_file = "sound.mp3"  # 오디오 파일이 있다면 여기에 설정
history = []
user_input = input("사용자 입력을 입력하세요: ")
is_search = bool(input("검색 도구를 사용할까요? (T/F): ").strip().lower() == 't')
client = genai.Client()

#_____________________________________________________________________________________
#파라미터에 따른 분기
if is_workflow:
    system_prompt = character_prompts + "\n" + workflow_prompts

else:
    system_prompt = character_prompts
#___________________________________________________________________________________

parts = [Part(text=user_input)]

if is_image_file:
    with open(is_image_file, "rb") as image_file:
        image_bytes = image_file.read()
        image_data = types.Part.from_bytes(data = image_bytes, mime_type="image/jpeg")
        parts.append(image_data)
if file:
    with open(file, "rb") as file:
        file_bytes = file.read()
        file_data = types.Part.from_bytes(data=file_bytes, mime_type="application/pdf")
        parts.append(file_data)
if audio_file:
    with open(audio_file, "rb") as audio_file:
        audio_bytes = audio_file.read()
        audio_data = types.Part.from_bytes(data=audio_bytes, mime_type="audio/mp3")
        parts.append(audio_data)

contents=[
        Content(role="user", parts=parts)
       # {"file": {"name": "file.pdf", "data": base64_encoded_file}}
    ]
if is_search:
    # 검색 도구를 사용하는 경우
    # Define the grounding tool
    grounding_tool = types.Tool(
    google_search=types.GoogleSearch()
    )

    # Configure generation settings
    config = types.GenerateContentConfig(
    tools=[grounding_tool]
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=config,
    )
    text_with_citations = add_citations(response)
    print(text_with_citations)
else:
    response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=contents)


print(response.text)

