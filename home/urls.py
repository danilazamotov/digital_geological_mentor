from django.urls import path
from .views import ollama_chat, upload_file, list_files, delete_file, generate_audio
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('ollama_chat/', ollama_chat, name='ollama_chat'),
    path('upload/', upload_file, name='file_upload'),
    path('files/', list_files),
    path('audio/<int:message_id>/', generate_audio, name='get_audio'),
    path('delete/', delete_file, name='delete_file'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

