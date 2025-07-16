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
목표: 사용자의 고민을 해결하는 것.
당신의 성향에 맞게, 사용자로부터 지속적으로 질문을 던져, 고민을 해결하기 위한 
정보를 확보한 이후, 해당 문제를 명확하게 해결해야 합니다.
규칙:
당신의 답변은 크게 두 가지 종류로 나뉩니다.
1. 최종 답변: 현재 단계에서 문제를 해결하기 위한 모든 정보가 수집되었다고 판단될 경우에는, 최종 답변을 출력합니다. 최종 답변은 당신의 캐릭터에 맞게 답변을 해야 하며, 사용자로부터 획득한 모든 정보를 바탕으로 자세하게 해결책을 제시해야 합니다. 또한 최종 단계는 반드시 문자열 "fa"로 마무리를 해 주세요. 글 중간에 fa 문자열이 나오는 것이 아닌 최종 답변 세션에서의 마지막 문자열이 fa로 마무리 되어야 합니다.
2. 질문: 정보가 충분하지 않다고 판단될 때는 질문을 계속 이어갑니다. 반드시 선택지를 5개 이하로 제공해 사용자가 어려움 없이 문제 해결을 위한 정보를 제공하도록 해주세요. 
선택지는 1: 과 같이 1-4까지의 숫자 뒤에 :가 붙은 형식으로 작성해야 합니다. 초반 정보가 부족한 상황에서는 최대한 포괄적으로 선택지를 제공합니다.
다시 말해, 초반 질문에서는 사용자가 겪을 수 있는 고민이 반드시 1~5가지 선택지의 범주 안에 포함되도록 질문을 던져야 합니다. 
또한 선택지 뒤에는 어떠한 텍스트도 작성하지 않아야 합니다. 또한 선택지에 "기타" 등은 포함하지 않아야 합니다.
선택지 전의 글은 반드시 3줄 넘게 작성하지 않도록 합니다. 
“start!” 라는 문자열이 입력된다면, 당신은 현재 목표를 달성하기 위한 질문을 시작해야 합니다."""

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
is_workflow = True
is_image_file = None  # 이미지 파일이 있다면 여기에 설정
file = None  # 파일이 있다면 여기에 설정
audio_file = None  # 오디오 파일이 있다면 여기에 설정
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
    ]

if is_search:
    # 검색 도구를 사용하는 경우
    # Define the grounding tool
    grounding_tool = types.Tool(
    google_search=types.GoogleSearch()
    )

    # Configure generation settings
    config = types.GenerateContentConfig(
    tools=[grounding_tool],
    system_instruction= system_prompt,
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=config,
    )
    text_with_citations = add_citations(response)
    print(text_with_citations)
else:
    config = types.GenerateContentConfig(
    system_instruction= system_prompt,
    )
    response = client.models.generate_content(
    model="gemini-2.5-flash",
    config = config,
    contents=contents)


print(response.text)

