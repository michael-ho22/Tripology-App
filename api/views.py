from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .serializers import UserSerializer, LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
import googlemaps
import requests
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Place, Itinerary, ItineraryPlace
from .serializers import ItinerarySerializer
from django.conf import settings

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ItineraryPlanningView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data

        # Extract user input
        desired_places = data.get('desired_places', [])
        total_available_time = data.get('total_available_time')  # in minutes

        # TODO: Implement AI-based suggestions if desired_places is empty

        # Fetch place details using Yelp API
        places = []
        for place_query in desired_places:
            place = self.fetch_place_from_yelp(place_query)
            if place:
                places.append(place)

        # Optimize itinerary
        itinerary_places = self.optimize_itinerary(places, total_available_time)

        # Create Itinerary
        itinerary = Itinerary.objects.create(user=user, total_time=total_available_time)
        for idx, (place, time_allocated) in enumerate(itinerary_places):
            ItineraryPlace.objects.create(
                itinerary=itinerary,
                place=place,
                order=idx,
                time_allocated=time_allocated
            )

        serializer = ItinerarySerializer(itinerary)
        return Response(serializer.data)

    def fetch_place_from_yelp(self, query):
        url = 'https://api.yelp.com/v3/businesses/search'
        headers = {'Authorization': f'Bearer {settings.YELP_API_KEY}'}
        params = {'term': query, 'location': 'YourDefaultLocation', 'limit': 1}

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            businesses = data.get('businesses', [])
            if businesses:
                business = businesses[0]
                place, created = Place.objects.get_or_create(
                    name=business['name'],
                    defaults={
                        'address': ', '.join(business['location']['display_address']),
                        'latitude': business['coordinates']['latitude'],
                        'longitude': business['coordinates']['longitude'],
                        'category': business['categories'][0]['title'] if business['categories'] else '',
                        'average_time_spent': 60,  # Default to 1 hour
                        'is_outdoor': False  # Simplification
                    }
                )
                return place
        return None

    def optimize_itinerary(self, places, total_available_time):
        # Simplified optimization: order by proximity and allocate equal time
        # TODO: Implement advanced optimization considering traffic and weather

        # Initialize Google Maps client
        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

        # Starting point (could be user's current location)
        origin = 'YourDefaultStartingPointAddress'

        # Calculate distances from origin to each place
        distances = []
        for place in places:
            distance_result = gmaps.distance_matrix(
                origins=[origin],
                destinations=[(place.latitude, place.longitude)],
                mode='driving',
                departure_time=datetime.now()
            )
            distance = distance_result['rows'][0]['elements'][0]['duration']['value']  # in seconds
            distances.append((place, distance))

        # Sort places by distance
        distances.sort(key=lambda x: x[1])

        # Allocate time
        time_per_place = total_available_time // len(places)
        itinerary_places = [(place, time_per_place) for place, _ in distances]

        return itinerary_places