from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'owner'):
            # Instance must have an attribute named `owner`.
            return obj.owner and obj.owner == request.user
        else:
            return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        if hasattr(obj, 'owner'):
            # Instance must have an attribute named `owner`.
            return obj.owner and obj.owner == request.user
        else:
            return True


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):

        # Instance must have an attribute named `owner`.
        if hasattr(obj, 'owner'):
            return request.user and obj.owner and (obj.owner == request.user or request.user.is_staff)
        else:
            return request.user and request.user.is_staff


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):

        # Instance must have an attribute named `owner`.
        if hasattr(obj, 'owner'):
            return request.user and obj.owner and (obj.owner == request.user or request.user.is_superuser)
        else:
            return request.user and request.user.is_superuser


