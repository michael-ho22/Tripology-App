from django.urls import path
from .views import RegisterView, LoginView, ItineraryPlanningView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('plan-itinerary/', ItineraryPlanningView.as_view(), name='plan-itinerary'),
]

