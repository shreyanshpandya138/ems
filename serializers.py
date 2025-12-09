from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile, Event, RSVP, Review, EventInvite

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username','email')

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = UserProfile
        fields = ('user','full_name','bio','location','profile_picture')

class EventSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    invited_ids = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), write_only=True, required=False)
    class Meta:
        model = Event
        fields = ('id','title','description','organizer','location','start_time','end_time','is_public','created_at','updated_at','invited_ids')
        read_only_fields = ('created_at','updated_at','organizer')

    def create(self, validated_data):
        invited_ids = validated_data.pop('invited_ids', [])
        user = self.context['request'].user
        validated_data['organizer'] = user
        event = Event.objects.create(**validated_data)
        for u in invited_ids:
            EventInvite.objects.create(event=event, user=u)
        return event

    def update(self, instance, validated_data):
        invited_ids = validated_data.pop('invited_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if invited_ids is not None:
            # replace invites
            instance.invited.clear()
            for u in invited_ids:
                EventInvite.objects.get_or_create(event=instance, user=u)
        return instance

    def validate(self, data):
        start = data.get('start_time', getattr(self.instance,'start_time', None))
        end = data.get('end_time', getattr(self.instance,'end_time', None))
        if start and end and start >= end:
            raise serializers.ValidationError("start_time must be before end_time")
        return data

class RSVPSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = RSVP
        fields = ('id','event','user','status','updated_at')
        read_only_fields = ('id','user','updated_at')

    def create(self, validated_data):
        user = self.context['request'].user
        event = validated_data['event']
        obj, created = RSVP.objects.update_or_create(event=event, user=user, defaults={'status': validated_data['status']})
        return obj

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Review
        fields = ('id','event','user','rating','comment','created_at')
        read_only_fields = ('id','user','created_at')

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        event = validated_data['event']
        review, created = Review.objects.update_or_create(event=event, user=user, defaults={
            'rating': validated_data['rating'],
            'comment': validated_data.get('comment','')
        })
        return review
