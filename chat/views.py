from django.shortcuts import render
import os
from user.models import UserProfile as User
from rest_framework import status
from rest_framework.response import Response 
from rest_framework.views import APIView
from django.utils import timezone 
from django.shortcuts import get_object_or_404
from .models import ChatSession, Message
from character.models import Character
from .serializers import ChatSerializer, MessageSerializer
import google.generativeai as genai
from dotenv import load_dotenv
from rest_framework.parsers import MultiPartParser, FormParser
import re
import base64
load_dotenv() 

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
# Create your views here.

workflow_prompts = """당신에게 주어진 과제는 다음과 같습니다.
{
목표: 감정 조절 및 정서적 문제 해결
당신의 성향에 맞게, 사용자로부터 지속적으로 질문을 던져, 정보를 확보한 이후, 해당 문제를 명확하게 해결해야 합니다.
규칙:
당신의 답변은 크게 두 가지 종류로 나뉩니다.
1. 최종 답변: 현재 단계에서 문제를 해결하기 위한 모든 정보가 수집되었다고 판단될 경우에는, 최종 답변을 출력합니다. 
최종 답변은 당신의 캐릭터에 맞게 답변을 해야 하며, 사용자로부터 획득한 모든 정보를 바탕으로 자세하게 해결책을 제시해야 합니다. 또한 최종 답변은 반드시 문자열 "fa"로 시작해 주세요.
2. 질문: 정보가 충분하지 않다고 판단될 때는 질문을 계속 이어갑니다. 본인의 캐릭터에 맞는 말투를 사용해 질문을 해야 합니다.
반드시 질문을 짧고 간결하게, 하나의 정보만 물어봐야 하며, 반드시 선택지를 4개 제공해 사용자가 어려움 없이 문제 해결을 위한 정보를 제공하도록 해주세요. 
선택지는 1: 과 같이 1-4까지의 숫자 뒤에 :가 붙은 형식으로 작성해야 합니다. 또한 선택지들 뒤에는 어떠한 텍스트도 작성하지 않아야 합니다. 
“start!” 라는 문자열이 입력된다면, 당신은 현재 목표를 달성하기 위한 질문을 시작해야 합니다.}"""

def return_workflow(workflow):
    """
    Role: 워크플로우 프롬프트를 반환하는 함수    
    Input: 워크플로우 이름
    Return: 워크플로우에 대한 프롬프트 문자열을 반환합니다.
    """
    workflow_prompts = f"""당신에게 주어진 과제는 다음과 같습니다.
    목표: {workflow}
    당신의 성향에 맞게, 사용자로부터 지속적으로 질문을 던져, 정보를 확보한 이후, 해당 문제를 명확하게 해결해야 합니다.
    규칙:
    당신의 답변은 크게 두 가지 종류로 나뉩니다.
    1. 최종 답변: 현재 단계에서 문제를 해결하기 위한 모든 정보가 수집되었다고 판단될 경우에는, 최종 답변을 출력합니다. 
    최종 답변은 당신의 캐릭터에 맞게 답변을 해야 하며, 사용자로부터 획득한 모든 정보를 바탕으로 자세하게 해결책을 제시해야 합니다. 또한 최종 답변은 반드시 문자열 "fa"로 시작해 주세요.
    2. 질문: 정보가 충분하지 않다고 판단될 때는 질문을 계속 이어갑니다. 본인의 캐릭터에 맞는 말투를 사용해 질문을 해야 합니다.
    반드시 질문을 짧고 간결하게, 하나의 정보만 물어봐야 하며, 반드시 선택지를 4개 제공해 사용자가 어려움 없이 문제 해결을 위한 정보를 제공하도록 해주세요. 
    선택지는 1: 과 같이 1-4까지의 숫자 뒤에 :가 붙은 형식으로 작성해야 합니다. 또한 선택지들 뒤에는 어떠한 텍스트도 작성하지 않아야 합니다. 
    “start!” 라는 문자열이 입력된다면, 당신은 현재 목표를 달성하기 위한 질문을 시작해야 합니다."""
    return workflow_prompts
        



class ChatView(APIView):
    """ 유저의 모든 챗 세션을 조회하는 API 뷰 """

    def get(self, request, user_id):

        """ 
        Role: 해당 유저의 모든 챗 세션을 조회함. 
        URL : /api/chat/users/<int:user_id>/sessions/ 
        Input: URL 형식에서 확인할 수 있다 싶이, URL로 유저 아이디를 전달받습니다.
        Return: 해당 유저의 모든 챗 세션을 반환합니다.
        """

        user_id = user_id
        if not user_id:
            return Response({'error':'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        # sessions = ChatSession.objects.filter(user = user_id)
        user = get_object_or_404(User, id=user_id)
        sessions = user.chatsession_set.all().order_by('-time')  
        
        serializer = ChatSerializer(sessions, many=True)
        return Response(serializer.data)



class ChatSessionGetView(APIView):
    """ 특정 챗 세션에 대한 메시지를 조회하거나, 삭제하는 API 뷰"""

    def get(self, request, session_id):

        """
        Role: 프론트엔드에서 배열된 ChatSession에 대해, 특정 ChatSession의 세부 내용을 가져옴. (Message)
        URL : /api/chat/sessions/<int:session_id>/
        Input: URL 형식으로 해당 세션의 아이디 (session_id)를 전달함.
        Return: 해당 세션에 포함된 모든 message 객체를 order 순으로 전달합니다
        """

        session_id = session_id
        if not session_id:
            return Response({'error':'session_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        session = ChatSession.objects.get(id=session_id)
        messages = session.message_set.all().order_by('order')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def delete(self, request, session_id):
        """
        Role: 프론트엔드에서 특정 ChatSession을 삭제함.
        URL : /api/chat/sessions/<int:session_id>/
        Input: URL 형식으로 해당 세션의 아이디 (session_id)를 전달함.
        Return: 성공적으로 삭제되었다는 메시지를 반환합니다.
        """

        session_id = session_id
        if not session_id:
            return Response({'error':'session_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            session = ChatSession.objects.get(id=session_id)
            session.delete()
            return Response({'message': 'Session deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except ChatSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

class ChatSessionPostView(APIView):

    """ 새로운 챗 세션을 생성하거나, 기존 챗 세션에 메시지를 추가하는 API 뷰 """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        
        """
        Role: 프론트엔드에서 새로운 메시지를 추가함. (Message)
        URL : /api/chat/sessions/
        Input: POST 요청으로 세션 아이디 (session_id), 유저 입력 (user_input), 워크플로우 여부 (is_workflow)를 Request body(json 형식)로 전달합니다. 아래 주석을 확인해 주세요.
        Return: 메세지 history에 대한 모델의 응답을 반환합니다.
        """
        session_id = request.data.get('session_id')
        user_input = request.data.get('user_input')
        is_workflow = request.data.get('is_workflow', False)  # 워크플로우 여부
        workflow_id = request.data.get('workflow_id', None)  # 워크플로우 ID (선택 사항)
        image_file = request.FILES.get('image_file', None)  # 이미지 파일 (선택 사항)
        is_search = request.data.get('is_search', False)  # 검색 여부 (선택 사항)
        file = request.FILES.get('file', None)  # 파일 업로드 (선택 사항)

        # 세션이 존재하지 않는 경우 새로 생성함
        #___________________________________________________________________________________
        if not session_id:
            session = ChatSession.objects.create(
                character_id=request.data.get('character_id'),
                user_id=request.data.get('user_id'),
                topic="None",
                time=timezone.now(),
                start_time = timezone.now(),
                is_workflow=is_workflow
            )
            session_id = session.id  # 새로 생성된 세션의 ID
            user_input = "start!" if is_workflow else user_input  # 워크플로우 시작 메시지 설정
            messages = []
            order = 0

        # 세션이 존재하는 경우 해당 세션을 가져옴 + 대화 히스토리 생성
        #___________________________________________________________________________________
        else:
            session = get_object_or_404(ChatSession, id=session_id)
            session.time = timezone.now() 
            messages = session.message_set.all().order_by('order')
            if not user_input:
                return Response({'error': 'user_input is required'}, status=status.HTTP_400_BAD_REQUEST)
            order = messages.last().order + 1 if messages else 0
            if messages:
                history = []
                for m in messages:
                    parts = [{"type": "text", "text": m.message}]
                    if m.image:
                        with open(m.image.path, 'rb') as img_file:
                            img_data = img_file.read()
                        parts.append({"type": "image", "image": {"data": img_data}})
                    history.append({'role': m.sender.lower(), 'parts': parts})              
                    
                history = [{'role': m.sender.lower(), 'parts': [m.message]} for m in messages]

        # Google Generative AI API 설정 + 대화 히스토리를 모델에 전달하고 응답을 받음
        #___________________________________________________________________________________
        character = session.character
        system_prompt = character.system_prompt
        if is_workflow:
            system_prompt += "\n" + workflow_prompts
        if is_search:
        # 검색 도구를 사용하는 경우
            system_prompt += "\n" + "You can use Google Search to find information related to the user's query."
            model = genai.GenerativeModel(
            model_name='gemini-2.5-flash', 
            system_instruction=system_prompt,
            tools = [genai.tools.google_search()]
            )
        else:
            model = genai.GenerativeModel(
            model_name='gemini-2.5-flash', 
            system_instruction=system_prompt
            )
        if messages:
            chat = model.start_chat(history=history)
        else:
            chat = model.start_chat()

        # 워크플로우 여부에 따라 메시지를 처리
        #___________________________________________________________________________________
        try:
            parts = [{"type": "text", "text": user_input}]
            if image_file:
                parts.append({"type": "image", "image": {"data": image_file.read()}})
            if file:
                file_bytes = file.read()
                encoded_file = base64.b64encode(file_bytes).decode('utf-8')
                parts.append({"type": "file", "file": {"data": encoded_file, "name": file.name}})
            response = chat.send_message(parts=parts)
            if response.text[0:2] == 'fa':
                model_output = response.text[2:]
                session.is_workflow = False

                #요약 생성
                user = session.user
                country = user.country.name if user.country else "Unknown"
                system_prompt = f"Summarize the following conversation in one short sentence (less then 5 word) that clearly conveys the user's main intent or request. Be specific and avoid vague or generic summaries. The user is from {country}.You should use the language of the user."
                model = genai.GenerativeModel(
                model_name='gemini-2.5-flash',  # 또는 'gemini-1.5-flash'가 아니라면 'gemini-2.5-flash' 시도
                system_instruction=system_prompt
                )
                summary_chat = model.start_chat()
                summary_response = summary_chat.send_message(model_output)
                session.summary = summary_response.text
                #"start!"문자열을 담은 첫 메시지를 삭제
                first_message = session.message_set.filter(order=0).first()
                if first_message:
                    first_message.delete()
                
                session.save()

            else:
                model_output = response.text
                if is_search:
                    citation = ""
                    for cite in response.citations:
                        citation += f"{cite.uri}\n"

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 메시지 저장
        #___________________________________________________________________________________
        Message.objects.create(session=session, sender='user', message=user_input, order=order, 
        image=image_file if image_file else None, citation=citation if is_search else None)
        Message.objects.create(session=session, sender='model', message=model_output, order=order + 1)

        # 만약 처음 생성하는 워크플로우가 아닌 메세지라면, 메세지 요약본을 생성해 저장.
        #___________________________________________________________________________________
        if order == 0 and not session.is_workflow:
            user = session.user
            country = user.country.name if user.country else "Unknown"

            system_prompt = f"Summarize the following conversation in one short sentence (less then 5 word) that clearly conveys the user's main intent or request. Be specific and avoid vague or generic summaries. The user is from {country}."
            model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',  # 또는 'gemini-1.5-flash'가 아니라면 'gemini-2.5-flash' 시도
            system_instruction=system_prompt
            )
            summary_chat = model.start_chat()
            summary_response = summary_chat.send_message(model_output)
            session.summary = summary_response.text
            session.save() 

        if session.is_workflow:
            model_output = re.split(r"\d+:", model_output)
            model_output = [output.strip() for output in model_output if output.strip()]

        else: 
            model_output = [model_output]

        return Response({'response': model_output, 'session_id': session_id, 'is_workflow': session.is_workflow}, status=status.HTTP_200_OK)

    def put(self, request, session_id):
        """
        Role: 프론트엔드에서 특정 챗 세션의 메시지를 수정해, 이후의 대화 (order 기준) 내역을 삭제한뒤, 해당 메시지에 대한 새로운 응답을 생성해 반환함.
        URL : /api/chat/sessions/<int:session_id>/
        Input: URL 형식으로 해당 세션의 아이디 (session_id)를 전달하고, Request body로 수정할 메시지 내용을 전달합니다.
        Return: 성공적으로 수정되었다는 메시지를 반환합니다.
        """

        if not session_id:
            return Response({'error':'session_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        session = get_object_or_404(ChatSession, id=session_id)
        message_id = request.data.get('message_id')
        new_content = request.data.get('new_content')

        if not message_id or not new_content:
            return Response({'error': 'message_id and new_content are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            message = Message.objects.get(id=message_id, session=session)
            message.message = new_content
            order = message.order
            message.save()
        except Message.DoesNotExist:
            return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)

        # 세션의 이후 메시지들을 삭제하고 새로운 응답을 생성
         
        delete_messages = session.message_set.filter(order__gt=message.order)
        delete_messages.delete()
        messages = session.message_set.all().order_by('order')

        # Google Generative AI API 설정
        character = session.character
        system_prompt = character.system_prompt
        if session.is_workflow:
            system_prompt += "\n" + return_workflow(workflow_prompts)
        model = genai.GenerativeModel(
        model_name='gemini-2.5-flash', 
        system_instruction=system_prompt
        )

        if messages:
            history = [{'role': m.sender.lower(), 'parts': [m.message]} for m in messages]
            chat = model.start_chat(history=history)
        else:
            chat = model.start_chat()

        # 대화 히스토리를 모델에 전달하고 응답을 받음
        try:
            response = chat.send_message(new_content)
            if response.text[0:2] == 'fa':
                model_output = response.text[2:]
                session.is_workflow = False

                #요약 생성
                user = session.user
                country = user.country.name if user.country else "Unknown"
                system_prompt = f"Please summarize the following conversation into 1–3 concise keywords that represent the core topic or request. The user is from {country}."
                model = genai.GenerativeModel(
                model_name='gemini-2.5-flash', 
                system_instruction=system_prompt
                )
                summary_chat = model.start_chat()
                summary_response = summary_chat.send_message(model_output)
                session.summary = summary_response.text
                session.save()

            else:
                model_output = response.text
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 메시지 저장
        Message.objects.create(session=session, sender='model', message=model_output, order=order + 1)

        return Response({'response': model_output, 'session_id': session_id, 'is_workflow': session.is_workflow}, status=status.HTTP_200_OK)





        



"""ChatSessionView Request Body 예시
{
    "session_id": 1,  # 세션 아이디 (없으면 새로 생성)
    "user_input": "미적분학에 대해서 알려줘",  # 유저 입력
    "is_workflow": False,  # 워크플로우 여부 (선택 사항)
    "character_id": 1,  # 캐릭터 아이디 (선택 사항)
    "user_id": 1  # 유저 아이디 (선택 사항)
}
"""



    
