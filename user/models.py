from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django_countries.fields import CountryField

class UserProfile(models.Model):
    ACTIVATION_TIME_CHOICES = [
        ('morning', '🌅 아침 (6~11시)'),
        ('afternoon', '☀️ 낮 (12~17시)'),
        ('evening', '🌙 저녁 / 밤 (18~24시)'),
        ('dawn', '🌃 새벽 (1~5시)'),
    ]

    CHARACTER_CHOICES = [
        ("Ailee", "나의 생각/감정을 정리해주는 친구"),
        ("Joon", "결정을 도와주는 상담가"),
        ("Nick", "개념 설명을 쉽게 해주는 조교"),
        ("Chad", "강력한 성장과 동기부여를 도와주는 친구"),
        ("Rin", "뇌과학적으로 나의 생각/감정을 정리해주는 친구")
    ]

    main_character = models.CharField(max_length=10, choices=CHARACTER_CHOICES)
    country = CountryField()
    name = models.CharField(max_length=50)
    birth_date = models.DateField()
    job = models.CharField(max_length=50, blank=True, null=True)
    

    activation_time = models.CharField(max_length=20, choices=ACTIVATION_TIME_CHOICES)

    # MBTI 점수 (0~100)
    i_e = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    n_s = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    t_f = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    p_j = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])

    # 캐릭터별 대화 수
    ailee_chat_count = models.PositiveSmallIntegerField(default=0)
    joon_chat_count = models.PositiveSmallIntegerField(default=0)
    nick_chat_count = models.PositiveSmallIntegerField(default=0)
    chad_chat_count = models.PositiveSmallIntegerField(default=0)
    rin_chat_count = models.PositiveSmallIntegerField(default=0)

    # 문제유형별 대화 수
    emotion_count = models.PositiveSmallIntegerField(default=0)
    decision_count = models.PositiveSmallIntegerField(default=0)
    social_count = models.PositiveSmallIntegerField(default=0)
    identity_count = models.PositiveSmallIntegerField(default=0)
    motivation_count = models.PositiveSmallIntegerField(default=0)
    learning_count = models.PositiveSmallIntegerField(default=0)

    gmail = models.EmailField(max_length=254)
    password = models.CharField(max_length=128)

    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)

"""# A가 B를 팔로우
a = UserProfile.objects.get(id=1)
b = UserProfile.objects.get(id=2)
a.following.add(b)

# A가 팔로우하는 사람들
a_following = a.following.all()

# B를 팔로우하고 있는 사람들
b_followers = b.followers.all()

# 언팔로우
a.following.remove(b)"""
