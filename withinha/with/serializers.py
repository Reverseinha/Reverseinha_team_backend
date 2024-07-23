from rest_framework import serializers
from .models import SurveyQuestion, SurveyResponse, MyUser, Post, Comment, Day, Goal, DiaryEntry

class SurveyQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyQuestion
        fields = '__all__'

class SurveyResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyResponse
        fields = '__all__'

class SignUpSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True, label="비밀번호 확인")
    survey_responses = SurveyResponseSerializer(many=True, write_only=True)

    class Meta:
        model = MyUser
        fields = ['id', 'email', 'username', 'birth_date', 'gender', 'phone_number', 'password', 'password_confirm', 'survey_responses']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "비밀번호가 일치하지 않습니다. 알맞게 입력해주세요."})
        return data

    def create(self, validated_data):
        survey_responses_data = validated_data.pop('survey_responses')
        validated_data.pop('password_confirm')
        user = MyUser.objects.create_user(**validated_data)
        
        for survey_response_data in survey_responses_data:
            SurveyResponse.objects.create(user=user, **survey_response_data)
        
        return user

class LoginSerializer(serializers.Serializer):
    id = serializers.CharField(label="ID")
    password = serializers.CharField(write_only=True, label="비밀번호")

class PostSerializer(serializers.ModelSerializer):
    total_likes = serializers.ReadOnlyField()
    total_comments = serializers.ReadOnlyField()
    author_name = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'created_at', 'image', 'author_name', 'total_likes', 'total_comments'] 
        read_only_fields = ['created_at']

class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'author_username', 'content', 'created_at']
        read_only_fields = ['created_at']

class DaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Day
        fields = '__all__'

class GoalSerializer(serializers.ModelSerializer):
    day = DaySerializer()

    class Meta:
        model = Goal
        fields = '__all__'

    def create(self, validated_data):
        day_data = validated_data.pop('day')
        day, created = Day.objects.get_or_create(date=day_data['date'])
        goal = Goal.objects.create(day=day, **validated_data)
        return goal

class DiaryEntrySerializer(serializers.ModelSerializer):
    day = DaySerializer()

    class Meta:
        model = DiaryEntry
        fields = '__all__'

    def create(self, validated_data):
        day_data = validated_data.pop('day')
        day, created = Day.objects.get_or_create(date=day_data['date'])
        diary_entry = DiaryEntry.objects.create(day=day, **validated_data)
        return diary_entry