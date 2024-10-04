from django.conf import settings
from django.shortcuts import render, redirect
from django.template.loader import get_template

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("Получен запрос на регистрацию:", request.data)  # Логирование
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": "Пользователь успешно зарегистрирован"}, status=status.HTTP_201_CREATED)
        print("Ошибки валидации:", serializer.errors)  # Логирование ошибок
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



def login_page(request):
    return render(request, 'authentication/Login.html')


# Представление для HTML-страницы регистрации
def register_page(request):
    if request.method == 'POST':
        serializer = RegisterSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return redirect('login')
    #     else:
    #         return render(request, 'authentication/Register.html', {'errors': serializer.errors})
    # else:
    #     return render(request, 'authentication/Register.html')


def test_static_dir(request):
    # Выводим значение STATICFILES_DIRS
    return HttpResponse(f"STATICFILES_DIRS: {settings.STATICFILES_DIRS, settings.STATIC_ROOT}")
