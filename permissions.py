from rest_framework import permissions

class IsOrganizer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.organizer == request.user

class IsInvitedOrPublic(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.is_public:
            return True
        if request.user.is_anonymous:
            return False
        if obj.organizer == request.user:
            return True
        return obj.invited.filter(pk=request.user.pk).exists()
