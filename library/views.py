from django.shortcuts import render
from rest_framework import viewsets
from .models import Book, User, Transaction
from .serializers import BookSerializer, UserSerializer, TransactionSerializer
from django.urls import path, include 
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView  # Import token views
from rest_framework.permissions import IsAuthenticated 
from rest_framework.decorators import action
from rest_framework.response import Response  # Import Response for custom actions
from rest_framework import status  # Import status for response status codes
from django.utils import timezone  # Import timezone for setting the return date
from rest_framework import generics
from rest_framework.permissions import AllowAny

# Import Swagger tools for manual parameter specification
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]


    # Define query parameters for Swagger documentation
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('title', openapi.IN_QUERY, description="Filter by title (case-insensitive partial match)", type=openapi.TYPE_STRING),
            openapi.Parameter('author', openapi.IN_QUERY, description="Filter by author (case-insensitive partial match)", type=openapi.TYPE_STRING),
            openapi.Parameter('isbn', openapi.IN_QUERY, description="Filter by exact ISBN", type=openapi.TYPE_STRING)
        ]
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def available(self, request):
        available_books = self.queryset.filter(copies_available__gt=0)

        # Optional query filters: title, author, isbn
        title = request.query_params.get('title', None)
        author = request.query_params.get('author', None)
        isbn = request.query_params.get('isbn', None)

        if title:
            available_books = available_books.filter(title__icontains=title)  # Case-insensitive partial match
        if author:
            available_books = available_books.filter(author__icontains=author)  # Case-insensitive partial match
        if isbn:
            available_books = available_books.filter(isbn__iexact=isbn)  # Exact match

        serializer = self.get_serializer(available_books, many=True)
        return Response(serializer.data)

    # Custom action to check out a book
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def checkout(self, request, pk=None):
        book = self.get_object()
        user = request.user.libraryuser  # Assuming the user is linked to LibraryUser via OneToOneField

        # Check if the user has already checked out this book
        if Transaction.objects.filter(user=user, book=book, return_date__isnull=True).exists():
            return Response({"message": "You have already checked out this book."}, status=status.HTTP_400_BAD_REQUEST)

        if book.copies_available > 0:
            # Decrease available copies and create a transaction
            book.copies_available -= 1
            book.save()
            transaction = Transaction.objects.create(user=user, book=book)
            return Response({"message": "Book checked out successfully!"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "No copies available."}, status=status.HTTP_400_BAD_REQUEST)

    # Custom action to return a book
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def return_book(self, request, pk=None):
        book = self.get_object()
        user = request.user.libraryuser

        # Check if the user has checked out the book and not yet returned it  
        try:
            transaction = Transaction.objects.get(user=user, book=book, return_date__isnull=True)
            transaction.return_date = timezone.now()
            transaction.save()

            # Increase the number of available copies
            book.copies_available += 1
            book.save()

            return Response({"message": "Book returned successfully!"}, status=status.HTTP_200_OK)
        except Transaction.DoesNotExist:
            return Response({"message": "You have not checked out this book."}, status=status.HTTP_400_BAD_REQUEST)



class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "username": user.username,
            "email": user.email
        }, status=status.HTTP_201_CREATED)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

