from django.shortcuts import render
from user.models import UserProfile
from .serializer import UserProfileSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django_countries.fields import CountryField

# Create your views here.
class UserCreateView(APIView):
    """
    사용자 프로필 생성 API
    """
    def post(self, request):
        # 사용자 프로필 생성 로직 구현
        email = request.data.get("email")
        passwoard = request.data.get("password")
        name = request.data.get("name")    
        main_character = request.data.get("main_character")
        country = request.data.get("country")
        birth_date = request.data.get("birth_date")
        mbti = {
            "i_e": request.data.get("i_e"),
            "n_s": request.data.get("n_s"),
            "t_f": request.data.get("t_f"),
            "p_j": request.data.get("p_j") }    
        activation_time = request.data.get("activation_time")
        # 저장
        UserProfile.objects.create(
            gmail=email,
            password=password,
            name=name,
            main_character=main_character,
            country=country,
            birth_date=birth_date,
            i_e=mbti["i_e"],
            n_s=mbti["n_s"],
            t_f=mbti["t_f"],
            p_j=mbti["p_j"],
            activation_time=activation_time
        )
        return Response({"message": "User profile created successfully"}, status=status.HTTP_201_CREATED)

class UserProfileView(APIView):
    """
    사용자 프로필 조회 및 수정 API
    """
    def get(self, request, user_id):
        # 사용자 프로필 조회 로직 구현
        # Url pattern에서 user_id를 받아옴
        user_profile = UserProfile.objects.get(id=user_id)
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, user_id):
        # 사용자 프로필 수정 로직 구현
        user_profile = UserProflie.objects.get(id=user_id)
        serializer  = UserProfileSerializer(user_profile, data = request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    """
    사용자 로그인 API
    """
    def post(self, request):
        # 사용자 로그인 로직 구현
        email = request.data.get('email')
        password = request.data.get('password')
        try: 
            user = UserProfile.objects.filter(gmail=email, password=password).first()
            serializer = UserProfileSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_404_NOT_FOUND)



