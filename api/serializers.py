from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Place, Itinerary, ItineraryPlace

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = '__all__'

class ItineraryPlaceSerializer(serializers.ModelSerializer):
    place = PlaceSerializer()

    class Meta:
        model = ItineraryPlace
        fields = ('order', 'time_allocated', 'place')

class ItinerarySerializer(serializers.ModelSerializer):
    places = ItineraryPlaceSerializer(source='itineraryplace_set', many=True)

    class Meta:
        model = Itinerary
        fields = ('id', 'user', 'created_at', 'total_time', 'total_cost', 'places')
