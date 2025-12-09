from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import models
from .models import Event, RSVP, Review
from .serializers import EventSerializer, RSVPSerializer, ReviewSerializer
from .permissions import IsOrganizer, IsInvitedOrPublic
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['location','is_public','organizer']
    search_fields = ['title','location','description','organizer__username']
    ordering_fields = ['start_time','created_at']

    def get_queryset(self):
        user = self.request.user
        qs = Event.objects.all()
        if not user.is_authenticated:
            return qs.filter(is_public=True)
        return qs.filter(models.Q(is_public=True) | models.Q(organizer=user) | models.Q(invited=user)).distinct()

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOrganizer()]
        if self.action in ['retrieve']:
            return [permissions.IsAuthenticatedOrReadOnly(), IsInvitedOrPublic()]
        return [permissions.IsAuthenticatedOrReadOnly()]

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def rsvp(self, request, pk=None):
        event = self.get_object()
        serializer = RSVPSerializer(data={'event': event.id, 'status': request.data.get('status')}, context={'request': request})
        serializer.is_valid(raise_exception=True)
        rsvp = serializer.save()
        return Response(RSVPSerializer(rsvp).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def reviews(self, request, pk=None):
        event = self.get_object()
        qs = Review.objects.filter(event=event)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = ReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ReviewSerializer(qs, many=True)
        return Response(serializer.data)

from rest_framework.views import APIView
class UpdateRSVPView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, event_id, user_id):
        rsvp = get_object_or_404(RSVP, event__id=event_id, user__id=user_id)
        user = request.user
        if rsvp.user != user and rsvp.event.organizer != user:
            return Response({'detail':'Not allowed'}, status=status.HTTP_403_FORBIDDEN)
        serializer = RSVPSerializer(rsvp, data={'status': request.data.get('status'), 'event': rsvp.event.id}, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(RSVPSerializer(rsvp).data)

class CreateReviewView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        event_id = self.kwargs['event_id']
        event = get_object_or_404(Event, pk=event_id)
        serializer.save(user=self.request.user, event=event)
