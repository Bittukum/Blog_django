from rest_framework import generics,status
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import( UserSignupSerializer,UserSerializer,BlogPostSerializer,CommentSerializer,EmailSerializer,LikeSerializer)
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .models import (BlogPost,Like)
from .pagination import BlogPostPagination
from rest_framework.exceptions import ValidationError
from django.core.mail import send_mail



class UserSignupView(APIView):

    """ Api to  sign up the new user"""
    def post(self, request):

        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(email=email, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            user_data = UserSerializer(user).data 
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                "user":user_data
            }, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class BlogPostCreateView(generics.CreateAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class BlogPostDetailView(generics.RetrieveAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BlogPost.DoesNotExist:
            # Handle the case where the blog post does not exist
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        

""" THis we can use if  we are using PostgreSQL"""
# class BlogPostListView(generics.ListAPIView):
#     serializer_class = BlogPostSerializer
#     permission_classes = [IsAuthenticated]
#     pagination_class = BlogPostPagination

#     def get_queryset(self):
#         queryset = BlogPost.objects.all().order_by('-created_at')
#         search = self.request.query_params.get('search', None)
#         if search:
#             queryset = queryset.annotate(
#                 search=SearchVector('title', 'content'),
#                 rank=SearchRank(SearchVector('title', 'content'), search)
#             ).filter(search=search).order_by('-rank')
            
#             queryset = queryset.annotate(
#                 similarity=TrigramSimilarity('title', search)
#             ).filter(similarity__gt=0.1).order_by('-similarity')
        
#         return queryset

#     def get(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)
        
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

class BlogPostListView(generics.ListAPIView):
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = BlogPostPagination

    def get_queryset(self):
        queryset = BlogPost.objects.all().order_by('-created_at')
        search = self.request.query_params.get('search', None)
        if search:
            # Basic text search using icontains
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    

class LikeCreateView(generics.CreateAPIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        comment_id = self.request.data.get('comment')
        user = self.request.user
        print(user,"uesr")
        if Like.objects.filter(comment_id=comment_id, user=user).exists():
            raise ValidationError('You have already liked this comment.')
        serializer.save(user=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
class SendEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            subject = serializer.validated_data['subject']
            message = serializer.validated_data['message']
            send_mail(subject, message, 'your-email@example.com', [email])
            return Response({'status': 'Email sent successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
