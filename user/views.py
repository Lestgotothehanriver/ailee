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
    사용자 프로필을 생성하는 API
    """

    def post(self, request):

        """
        Role: 사용자 프로필을 생성합니다.
        URL : /api/user/create/
        Input: 사용자 프로필 생성에 필요한 데이터를 request body로 전달합니다.
        Return: 사용자 프로필 생성 성공 여부를 반환합니다.
        """

        email = request.data.get("email")
        password = request.data.get("password")
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

        """
        Role: 사용자 프로필을 조회합니다.
        URL : /api/user/<int:user_id>/
        Input: URL 형식으로 사용자 ID를 전달합니다.
        Return: 사용자 프로필 정보를 반환합니다.
        """

        user_profile = UserProfile.objects.get(id=user_id)
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, user_id):
        
        """
        Role: 사용자 프로필을 수정합니다.
        URL : /api/user/<int:user_id>/
        Input: URL 형식으로 사용자 ID를 전달하고, 수정할 데이터를 request body로 전달합니다.
        Return: 수정된 사용자 프로필 정보를 반환합니다.
        """

        user_profile = UserProfile.objects.get(id=user_id)
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

        """
        Role: 사용자 로그인을 처리합니다.
        URL : /api/user/login/
        Input: 이메일과 비밀번호를 request body로 전달합니다.
        Return: 로그인 성공 시 사용자 프로필 정보를 반환합니다.
        """

        email = request.data.get('email')
        password = request.data.get('password')
        try: 
            user = UserProfile.objects.filter(gmail=email, password=password).first()
            serializer = UserProfileSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_404_NOT_FOUND)

class UserFollowView(APIView):
    """
    사용자 팔로우 API
    """
    
    def post(self, request, user_id):
        """
        Role: 사용자를 팔로우합니다.
        URL: api/user/<int:user_id>/follow/
        Input: URL형식으로 유저 아이디를 전달하고, Request body에 팔로우할 사용자의 ID를 전달합니다.
        Return: 팔로우 성공 여부를 반환합니다.
        """

        current_user_id = user_id
        target_user_id = request.data.get("user_id")
        try:
            current_user = UserProfile.objects.get(id=current_user_id)
            target_user = UserProfile.objects.bet(id=target_user_id)
            current_user.following.add(target_user)
            return Response({'message': 'User followed successfully'}, status = status.HTTP_200_OK)

        except UserProfile.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, user_id):
        """
        Role: 사용자의 팔로우를 취소합니다.
        URL: api/user/<int:user_id>/follow/
        Input: URL형식으로 유저 아이디를 전달하고, Request body에 언팔로우할 사용자의 ID를 전달합니다.
        Return: 언팔로우 성공 여부를 반환합니다.
        """

        current_user_id = user_id
        target_user_id = request.data.get("user_id")
        try:
            current_user = UserProfile.objects.get(id=current_user_id)
            target_user = UserProfile.objects.get(id=target_user_id)
            current_user.following.remove(target_user)
            return Response({'message': 'User unfollowed successfully'}, status=status.HTTP_200_OK)

        except UserProfile.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class UserFollowingView(APIView):
    """
    사용자 팔로우 목록 조회 API
    """

    def get(self, request, user_id):
        """
        Role: 사용자가 팔로우하는 사람들의 목록을 조회합니다.
        URL: api/user/<int:user_id>/following/
        Input: URL 형식으로 사용자 ID를 전달합니다.
        Return: 팔로우하는 사람들의 목록을 반환합니다.
        """

        user = UserProfile.objects.get(id=user_id)
        following = user.following.all()
        serializer = UserProfileSerializer(following, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserFollowerView(APIView):
    """
    사용자 팔로워 목록 조회 API
    """

    def get(self, request, user_id):
        """
        Role: 사용자를 팔로우하는 사람들의 목록을 조회합니다.
        URL: api/user/<int:user_id>/followers/
        Input: URL 형식으로 사용자 ID를 전달합니다.
        Return: 팔로워들의 목록을 반환합니다.
        """

        user = UserProfile.objects.get(id=user_id)
        followers = user.followers.all()
        serializer = UserProfileSerializer(followers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




        






"""사용자 프로필 생성 json 예시

"""