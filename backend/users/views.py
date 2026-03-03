from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login
from .models import User, Rank
from .serializers import UserSerializer, RankSerializer

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        dni = request.data.get('dni')
        
        if not username or not dni:
            return Response({'error': 'Username and DNI are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # In this platform, DNI is the password
        user = authenticate(request, username=username, password=dni)
        
        if user:
            login(request, user)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        else:
            # Check if user exists but password (dni) is wrong, 
            # or try to find user by username and check dni field directly if not using it as password
            try:
                user_obj = User.objects.get(username=username)
                if user_obj.dni == dni:
                    # Sync password with DNI so Basic Auth works in subsequent calls
                    user_obj.set_password(dni)
                    user_obj.save()
                    login(request, user_obj)
                    serializer = UserSerializer(user_obj)
                    return Response(serializer.data)
            except User.DoesNotExist:
                pass
                
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserScoreView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class RankViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Rank.objects.all().order_by('min_score')
    serializer_class = RankSerializer
    permission_classes = [IsAuthenticated]
