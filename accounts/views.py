import os

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .serializers import RegisterSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def ensure_superuser(request):
    secret = request.data.get("secret", "")
    if secret != os.environ.get("ADMIN_SECRET", "fix-my-admin-now"):
        return Response({"error": "Invalid secret"}, status=status.HTTP_403_FORBIDDEN)

    email = request.data.get("email", "muneneemmanuel953@gmail.com")
    password = request.data.get("password", "Admin123!")
    user, created = User.objects.get_or_create(
        email=email,
        defaults={"username": email.split("@")[0]},
    )
    user.is_staff = True
    user.is_superuser = True
    user.set_password(password)
    user.save()
    return Response({
        "email": email,
        "created": created,
        "message": "Superuser ready",
    })
    