from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

from celsus.models import CurtainAccessToken


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user in obj.owners.all())

class IsFileOwnerOrPublic(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.project.enable:
            return True
        return bool(request.user and request.user.is_authenticated and request.user in obj.project.owners.all())


class IsCurtainOwnerOrPublic(BasePermission):
    def has_object_permission(self, request, view, obj):
        print(obj.enable)
        if obj.enable:
            return True
        if obj.project:
            if obj.project.enable:
                return True
            if bool(request.user and request.user.is_authenticated):
                return bool(request.user in obj.project.owners.all())
        else:
            if bool(request.user and request.user.is_authenticated):
                return bool(request.user in obj.owners.all())
        return False


class HasCurtainToken(BasePermission):
    def has_object_permission(self, request, view, obj):
        token = view.kwargs.get("token", "")
        if token != "":
            t = CurtainAccessToken.objects.filter(token=token).first()
            if t:
                if t.curtain.link_id == view.kwargs.get("link_id", ""):
                    try:
                        access_token = AccessToken(token)
                        access_token.check_exp()
                        return True
                    except TokenError:
                        return False
        return False


class IsCurtainOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if bool(request.user and request.user.is_authenticated):
            return bool(request.user in obj.owners.all())
        return False