from django.contrib.auth.models import User
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import renderers
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from snippets.models import Snippet
from snippets.permissions import IsOwnerOrReadOnly
from snippets.serializers import SnippetSerializer, UserSerializer

CACHE_TIMEOUT = 60 * 60 * 2  # 2 Hours


class SnippetViewSet(CacheResponseMixin, ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    serializer_class = SnippetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly]
    object_cache_timeout = CACHE_TIMEOUT
    list_cache_timeout = CACHE_TIMEOUT

    def get_queryset(self):
        print(self.request.user)
        user = self.request.user
        if user.is_authenticated:
            queryset = Snippet.objects.filter(owner=user)
        else:
            queryset = Snippet.objects.none()
        return queryset

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UserViewSet(CacheResponseMixin, ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    object_cache_timeout = CACHE_TIMEOUT
    list_cache_timeout = CACHE_TIMEOUT
