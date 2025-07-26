from rest_framework.permissions import BasePermission,  SAFE_METHODS

class isUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
      is_authenticated  = bool(request.user and request.user.is_authenticated)
      return is_authenticated or request.method in SAFE_METHODS

class isAdminForDeleteORPatchandReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS: # fragt ob die request methode GET ist
            return True
        elif request.method == 'DELETE':
            return bool(request.user and request.user.is_superuser)
        else:
            return bool(request.user and request.user.is_authenticated)


class isOwnerOrAdmin(BasePermission):

    def has_object_permission(self, request, view, obj):
         if request.method in SAFE_METHODS:
            return True
         elif request.method == 'DELETE':
            return bool(request.user and request.user.is_superuser)
         else:
             return bool(request.user and request.user == obj.user)# obj = gleich eintrag in der daten bank

class isAdminOnly(BasePermission):
    def has_permission(self,request, view):
        if request.user.is_superuser :
            return True
        return False