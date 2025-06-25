from django.shortcuts import render
import os
from rest_framework import status
from rest_framework.response import Response 
from rest_framework.views import APIView
from django.utils import timezone 
from django.shortcuts import get_object_or_404
from .models import ChatSession, Message
from character.models import Character
from .serializers import ChatSerializer, MessageSerializer
import google.generativeai as genai
import pandas as pd
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
# Create your views here.

workflow_prompts = """당신에게 주어진 과제는 다음과 같습니다.
{
목표: 감정 조절 및 정서적 문제 해결
당신의 성향에 맞게, 사용자로부터 지속적으로 질문을 던져, 정보를 확보한 이후, 해당 문제를 명확하게 해결해야 합니다.
규칙:
당신의 답변은 크게 두 가지 종류로 나뉩니다.
1. 최종 답변: 현재 단계에서 문제를 해결하기 위한 모든 정보가 수집되었다고 판단될 경우에는, 최종 답변을 출력합니다. 최종 답변은 당신의 캐릭터에 맞게 답변을 해야 하며, 사용자로부터 획득한 모든 정보를 바탕으로 자세하게 해결책을 제시해야 합니다.
2. 질문: 정보가 충분하지 않다고 판단될 때는 질문을 계속 이어갑니다. 질문을 짧고 간결하게 하나의 정보만 물어봐야 하며, 필요한 경우 선택지를 2-3개정도 제공해 사용자가 어려움 없이 문제 해결을 위한 정보를 제공하도록 해주세요.
“start!” 라는 문자열이 입력된다면, 당신은 현재 목표를 달성하기 위한 질문을 시작해야 합니다.}"""

class ChatView(APIView):
    def get(self, request, user_id):
        # 해당 유저의 모든 챗 세션을 조회함. 
        # request: 해당 유저의 아이디 (user_id)
        # urlpattern으로 id를 받음
        # response: 모든 Chatsession 객체 
        user_id = user_id
        if not user_id:
            return Response({'error':'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        # sessions = ChatSession.objects.filter(user = user_id)
        user = get_object_or_404(User, id=user_id)
        sessions = user.chatsession_set.all().order_by('-time')  
        
        serializer = ChatSerializer(sessions, many=True)
        return Response(serializer.data)


class ChatSessionView(APIView):
    # 단일 채팅 내용을 조회하고 생성함
    def get(self, request, session_id):
        # 프론트엔드에서 배열된 ChatSession에 대해, 특정 ChatSession의 세부 내용을 가져옴. (Message)
        # request: 쿼리 파라미터로 해당 세션의 아이디 (session_id)를 전달함.
        # response: 해당 세션에 포함된 모든 message 객체 
        session_id = session_id
        if not session_id:
            return Response({'error':'session_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        session = ChatSession.objects.get(id=session_id)
        messages = session.message_set.all().order_by('order')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request):
        # 프론트엔드에서 유저의 질문에 대해, 인공지능이 답변을 생성하고, 해당 세션에 메시지를 저장해, 결과값을 리턴함.
        # request: 세션 아이디 (session_id), 유저의 질문 (user_input)
        # response: 인공지능의 답변 (response)
        session_id = request.data.get('session_id')
        user_input = request.data.get('user_input')
        is_workflow = request.data.get('is_workflow', False)  # 워크플로우 여부
        is_fa= False


        # 세션이 존재하지 않는 경우 새로 생성함
        if not session_id:
            session = ChatSession.objects.create(
                character_id=request.data.get('character_id'),
                user_id=request.data.get('user_id'),
                topic="None",
                time=timezone.now(),
                start_time = timezone.now()
            )
            messages = []
            order = 0

        # 세션이 존재하는 경우 해당 세션을 가져옴
        else:
            session = get_object_or_404(ChatSession, id=session_id)
            session.time = timezone.now()  # 세션의 시간을 현재 시간으로 업데이트
            messages = session.message_set.all().order_by('order')
            if not user_input:
                return Response({'error': 'user_input is required'}, status=status.HTTP_400_BAD_REQUEST)
            order = messages.last().order + 1 if messages else 0
            if messages:
                history = [{'role': m.sender.lower(), 'parts': [m.message]} for m in messages]

        # Google Generative AI API 설정
        character = session.character
        system_prompt = character.system_prompt
        if is_workflow:
            system_prompt += "\n" + workflow_prompts

        model = genai.GenerativeModel(model_name='gemini-1.5-pro', system_instruction=system_prompt)
        if messages:
            chat = model.start_chat(history=history)
        else:
            chat = model.start_chat()

        # 대화 히스토리를 모델에 전달하고 응답을 받음
        try:
            response = chat.send_message(user_input)
            if response.text[0:2] == 'fa':
                response.text = response.text[2:]
                is_fa = True 

            model_output = response.text
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 메시지 저장
        Message.objects.create(session=session, sender='user', message=user_input, order=order)
        Message.objects.create(session=session, sender='model', message=model_output, order=order + 1)

        # 만약 처음 생성하는 메세지라면, 메세지 요약본을 생성해 저장.
        if order == 0:
            user = session.user
            country = user.country.name if user.country else "Unknown"

            system_prompt = f"please summarize the following conversation in a concise manner. The user is from {country}"
            summary_chat = model.start_chat(system_instruction=system_prompt)
            summary_response = summary_chat.send_message(model_output)
            session.summary = summary_response.text
            session.save() 

        return Response({'response': model_output, 'is_fa':is_fn}, status=status.HTTP_200_OK)
        





    
"""'
PSGenerationView 입력 예시
    {
    "workflow_id": 1,
    "character": "Ailee",
    "user": 1,
    "workflow_type": "EmotionRegulation",
    "answers": [
    "요즘 자주 우울해요.",
    "한 일주일 전부터요.",
    "시험 성적이 안 나와서요.",
    "꽤 자주요.",
    "그냥 참아요."
    ]
    }
    """
        
