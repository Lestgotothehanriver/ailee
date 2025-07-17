from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response 
from rest_framework.views import APIView
from django.utils import timezone 
from django.shortcuts import get_object_or_404
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
#___________________________________________________________________________________
from user.models import UserProfile as User
from chat.models import ChatSession, Message
from .models import CallSession, Talk, Audio
from character.models import Character
from chat.serializers import ChatSerializer, MessageSerializer
from call.serializers import CallSerializer, TalkSerializer
#___________________________________________________________________________________
import google.generativeai as generativeai
from google.genai import types
from google import genai
from google.genai.types import Part, Content
#___________________________________________________________________________________
from dotenv import load_dotenv
import os
import re
import base64
import mimetypes
import wave
from distutils.util import strtobool
load_dotenv() 
generativeai.configure(api_key=os.environ["GEMINI_API_KEY"])
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
#___________________________________________________________________________________
workflow_prompts = """당신에게 주어진 과제는 다음과 같습니다.
{
목표: 사용자의 고민을 해결하는 것.
당신의 성향에 맞게, 사용자로부터 지속적으로 질문을 던져, 고민을 해결하기 위한 
정보를 확보한 이후, 해당 문제를 명확하게 해결해야 합니다.
규칙:
당신의 답변은 크게 두 가지 종류로 나뉩니다.
1. 최종 답변: 현재 단계에서 문제를 해결하기 위한 모든 정보가 수집되었다고 판단될 경우에는, 최종 답변을 출력합니다. 최종 답변은 당신의 캐릭터에 맞게 답변을 해야 하며, 사용자로부터 획득한 모든 정보를 바탕으로 자세하게 해결책을 제시해야 합니다. 또한 최종 단계는 반드시 문자열 "fa"로 시작해 주세요. 글 중간에 fa 문자열이 나오는 것이 아닌 최종 답변 세션에서의 첫 두개의 문자열이 fa로 시작되어야 합니다.
2. 질문: 정보가 충분하지 않다고 판단될 때는 질문을 계속 이어갑니다. 반드시 선택지를 5개 이하로 제공해 사용자가 어려움 없이 문제 해결을 위한 정보를 제공하도록 해주세요. 
선택지는 1: 과 같이 1-4까지의 숫자 뒤에 :가 붙은 형식으로 작성해야 합니다. 초반 정보가 부족한 상황에서는 최대한 포괄적으로 선택지를 제공합니다.
다시 말해, 초반 질문에서는 사용자가 겪을 수 있는 고민이 반드시 1~4가지 선택지의 범주 안에 포함되도록 질문을 던져야 합니다. 
또한 선택지 뒤에는 어떠한 텍스트도 작성하지 않아야 합니다. 또한 선택지에 "기타" 등은 포함하지 않아야 합니다.
선택지 전의 글은 반드시 3줄 넘게 작성하지 않도록 합니다. 
“start!” 라는 문자열이 입력된다면, 당신은 현재 목표를 달성하기 위한 질문을 시작해야 합니다.}"""

def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
   with wave.open(filename, "wb") as wf:
      wf.setnchannels(channels)
      wf.setsampwidth(sample_width)
      wf.setframerate(rate)
      wf.writeframes(pcm)
# Create your views here.
#___________________________________________________________________________________
class CallSessionGetView(APIView):
    """ 특정 콜 세션에 대해 세부 통화 내역을 가져오는 API 뷰 """

    def get(self, request, session_id):

        """
        Role: 프론트엔드에서 배열된 CallSession의 세부 통화 내역을 가져옴.
        URL : /api/call/sessions/<int:session_id>/`
        Input: URL 형식으로 해당 세션의 아이디 (session_id)를 전달함.
        Return: 해당 세션에 포함된 모든 call 객체를 order 순서대로 반환합니다.
        """
        session_id = session_id
        if not session_id:
            return Response({'error':'session_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        session = Callsession.objects.get(id=session_id)
        talks = session.talks.all().order_by('order')
        serializer = TalkSerializer(talks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

#___________________________________________________________________________________
class ChatSessionPostView(APIView):

    """ 새로운 콜 세션을 생성하는 API 뷰 """
    parser_classes = (JSONParser, MultiPartParser, FormParser)
        
    def post(self, request):
        
        """
        Role: 챗봇과 통화
        URL : /api/call/sessions/
        Input: POST 요청으로 챗 세션 아이디 (session_id), 유저 입력 (user_input), 캐릭터 아이디(character_id), 워크플로우 여부 (is_workflow), 오디오를 Request body(json 형식)로 전달합니다. 아래 주석을 확인해 주세요.
        Return: 톡 history에 대한 모델의 응답을 반환합니다.
        """

        # 필요한 파라미터 설정
        #___________________________________________________________________________________
        session_id = request.data.get('session_id')
        user_input = request.data.get('user_input')
        is_workflow = to_bool(request.data.get('is_workflow', None))  # 워크플로우 여부
        audio = request.FILES.get('audio', None)  # 오디오 파일 업로드 (선택 사항)

        # 세션 생성 혹은 호출 단계
        #___________________________________________________________________________________
        if not session_id:
            session = CallSession.objects.create(
                character_id=request.data.get('character_id'),
                time=timezone.now(),
                is_workflow=is_workflow
            )
            session_id = session.id  # 새로 생성된 세션의 ID
            user_input = "start!" if is_workflow else user_input  # 워크플로우 시작 메시지 설정
            history = []
            order = 0

        # 세션이 존재하는 경우 해당 세션을 가져옴 + 대화 히스토리 호출
        else:
            session = get_object_or_404(CallSession, id=session_id)
            is_workflow = session.is_workflow
            session.time = timezone.now() 
            talks = session.talks.all().order_by('order')
            mime_type = mimetypes.guess_type(audio.name)[0]
            audio_data = Part.from_bytes(data=audio.read(), mime_type=mime_type)
            prompt = 'Generate a transcript of the speech.'
            response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, audio_data]
            )
            user_input = response.text
            order = talks.last().order + 1 if talks else 0
            if talks:
                history = []
                for talk in talks:
                    parts = [Part(text=talk.message)]
                    #___________________________________________________________________________________
                    #with open(talk.audios.path, 'rb') as audio_obj:
                    #    audio_bytes = audio_obj.read()
                    #mime_type = mimetypes.guess_type(m.audio.path)[0]
                    #audio_data = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
                    #parts.append(audio_data)
                    #___________________________________________________________________________________
                    history.append(Content(role=talk.sender.lower(), parts=parts))    

        # 워크플로우 여부, 검색 여부 등 세부 사항 설정 (생성 준비 단계)
        #___________________________________________________________________________________     
        character = session.character
        system_prompt = character.system_prompt
        talk_prompts = """
        You are doing a call with a user. 
        Answer to the audio file like you are talking to the user on the phone.
        """"
        if is_workflow:
            system_prompt += "\n" + workflow_prompts

        system_prompt += "\n" + talk_prompts


        config = types.GenerateContentConfig(
            system_instruction= system_prompt,
            )
    
        # 응답 생성 
        #___________________________________________________________________________________
        try:
            parts = []
            mime_type = mimetypes.guess_type(audio.name)[0]
            parts.append(Part.from_bytes(data=audio.read(), mime_type=mime_type))

            history.append(Content(role="user", parts=parts))
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=history,
                config=config
            )

            # 워크플로우 여부 판단 로직, 최종 답변인 경우 요약 생성 및 형식 조정
            if response.text[0:2] == 'fa':
                model_output = response.text[2:]
                session.is_workflow = False
                user = session.user
                country = user.country.name if user.country else "Unknown"
                system_prompt = f"Summarize the following conversation in one short sentence (less then 5 word) that clearly conveys the user's main intent or request. Be specific and avoid vague or generic summaries. The user is from {country}.You should use the language of the user."
                model = generativeai.GenerativeModel(
                model_name='gemini-2.5-flash',  
                system_instruction=system_prompt
                )
                summary_chat = model.start_chat()
                summary_response = summary_chat.send_message(model_output)
                session.summary = summary_response.text
                first_talk = session.talks.filter(order=0).first()
                if first_talk:
                    first_talk.delete()
                session.save()

            else:
                model_output = response.text

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 메시지 저장
        #___________________________________________________________________________________
        talk = Talk.objects.create(session=session, 
            sender='user',
            message=user_input, 
            order=order, 
            is_workflow=is_workflow)

        Audio.objects.create(
            talk=talk,
            audio=audio,
            description=""
        )
        model_talk = talk.objects.create(session=session, 
            sender='model', 
            message=model_output,
            order=order + 1,)
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=f"Say: {model_output}",
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name='Kore',
                        )
                    )
                ),
            )
        )
        data = response.candidates[0].content.parts[0].inline_data.data
        file_name=f"call_audio_{session_id}_{order}.wav"
        wave_file(file_name, data)

        # 모델 응답 전송
        #____________________________________________________________________________________
        if session.is_workflow:
            model_output = re.split(r"\d+:", model_output)
            model_output = [output.strip() for output in model_output if output.strip()]

        else: 
            model_output = [model_output]

        return Response({'response': model_output, 'audio': data, 'session_id': session_id, 'is_workflow': session.is_workflow, }, status=status.HTTP_200_OK)
#___________________________________________________________________________________