from rest_framework.permissions import BasePermission,  SAFE_METHODS
from Kan_Mind_app.models import BoardUser


class isUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
      is_authenticated  = bool(request.user and request.user.is_authenticated)
      return is_authenticated or request.method in SAFE_METHODS

class IsAdminForCrud(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        elif request.method == 'DELETE':
            return bool(request.user and request.user.is_superuser)
        else:
            return bool(request.user and request.user.is_authenticated)


class isOwnerOrAdmin(BasePermission):
     def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_superuser


class IsActiveUser(BasePermission):
    """Custom permission to only allow active users"""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.is_active and
            not request.user.is_anonymous
        )


class isBoardUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return BoardUser.objects.filter(board=obj.board, user=request.user).exists()

class isBaordAdmin(BasePermission):
     def has_object_permission(self, request, view, obj):
        return BoardUser.objects.filter(board=obj.board,user=request.user,role='Owner').exists()


class isCommentAuthorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.author == request.user or request.user.is_staff