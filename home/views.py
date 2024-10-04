import os
import fitz
import requests
from django.views.decorators.csrf import csrf_exempt
from docx import Document
import ollama
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.conf import settings

from home.models import Message

SUPPORTED_MODELS = ['llama3.1-7b', 'qwen2.5:7b', 'llama3.1-72b', 'qwen2.5:72b']

import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def generate_audio(request):
    try:
        message_text = request.data.get('text')

        if not message_text:
            return JsonResponse({'error': 'Текст сообщения не передан'}, status=400)

        # Генерация аудио с помощью TTS сервера
        session_response = requests.post('http://localhost:8020/session/new')
        if session_response.status_code != 200:
            return JsonResponse({'error': 'Ошибка при создании сессии TTS'}, status=500)

        session_data = session_response.json()
        session_id = session_data['session_id']

        tts_payload = {
            'sessionId': session_id,
            'text': message_text
        }
        tts_response = requests.post('http://localhost:8020/tts', json=tts_payload)

        if tts_response.status_code == 200:
            audio_filename = f"audio_{hash(message_text)}.wav"
            audio_file_path = os.path.join(settings.MEDIA_ROOT, 'audio', audio_filename)
            os.makedirs(os.path.dirname(audio_file_path), exist_ok=True)

            with open(audio_file_path, 'wb') as f:
                f.write(tts_response.content)

            audio_url = request.build_absolute_uri(os.path.join(settings.MEDIA_URL, 'audio', audio_filename))
            return JsonResponse({'audio_url': audio_url})

        else:
            return JsonResponse({'error': 'Ошибка при генерации аудио'}, status=500)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def split_text(text, max_length=4096):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def ollama_chat(request):
    try:
        message_text = request.data.get('message')
        model = request.data.get('model', 'qwen2.5:7b')
        ollama_url = 'http://localhost:11434/api/chat'
        attached_file = request.FILES.get('file', None)
        catalog_file_name = request.data.get('catalogFileName', None)
        print()
        if not attached_file and not catalog_file_name:
            # Обрабатываем случай только с текстом
            prompt = f"Вы — ИИ-помощник в геологии, общающийся исключительно на русском языке. Вопрос: {message_text}"
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "stream": False
            }

            response = requests.post(ollama_url, json=payload)
            if response.status_code == 200:
                response_data = response.json()
                response_text = response_data.get('message', {}).get('content', '')

                return JsonResponse({"response": response_text})

            return JsonResponse({'error': 'Ошибка при обращении к Ollama-серверу'}, status=response.status_code)

        # Если файл прикреплен
        if attached_file:
            file_text = handle_file_upload(attached_file)
        elif catalog_file_name:
            file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', catalog_file_name)
            if os.path.exists(file_path):
                file_text = extract_text_from_file(file_path)
            else:
                return JsonResponse({'error': 'Файл не найден'}, status=404)

        # Логика для обработки текстов документа и вопросов
        text_parts = split_text(file_text)
        responses = []

        for part in text_parts:
            prompt = f"""
                Вы — ИИ-помощник, общающийся исключительно на русском языке.

                Вопрос:
                {message_text}

                Текст документа:
                {part}

                Ответ:
                """
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "stream": False
            }

            response = requests.post(ollama_url, json=payload)
            if response.status_code == 200:
                response_data = response.json()
                responses.append(response_data.get('message', {}).get('content', ''))
            else:
                return JsonResponse({'error': 'Ошибка при обращении к Ollama-серверу'}, status=response.status_code)

        # Итоговое резюме
        summary_prompt = f"""
            Пишите на русском. Вот несколько фрагментов ответов на вопрос: {message_text}. Кратко Составьте общий итоге не повторяясь! ответьте четко на конечный вопрос: {message_text}:

            Ответы:
            {" ".join(responses)}

            Финальный вывод:
        """

        summary_payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": summary_prompt
                }
            ],
            "stream": False
        }

        summary_response = requests.post(ollama_url, json=summary_payload)
        if summary_response.status_code == 200:
            summary_data = summary_response.json()
            final_summary = summary_data.get('message', {}).get('content', '')

            return JsonResponse({"response": final_summary})
        else:
            return JsonResponse({'error': 'Ошибка при генерации итогового резюме'}, status=summary_response.status_code)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def handle_file_upload(attached_file):
    file_path = default_storage.save(os.path.join('uploads', attached_file.name), ContentFile(attached_file.read()))
    file_full_path = os.path.join(settings.MEDIA_ROOT, file_path)
    return extract_text_from_file(file_full_path)


def extract_text_from_file(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == ".pdf":
        return extract_text_from_pdf(file_path)
    elif file_extension == ".docx":
        return extract_text_from_docx(file_path)
    else:
        raise ValueError('Unsupported file format')


def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    full_text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        page_text = page.get_text("text")
        full_text += page_text.replace("\n", " ").strip()
    print(f"Всего страниц: {doc.page_count}")
    print(f"Длина полного текста: {len(full_text)} символов")
    doc.close()
    return full_text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text.replace("\n", " ").strip() + " "
    return text

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def list_files(request):
    files_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
    if not os.path.exists(files_dir):
        os.makedirs(files_dir)
    files = os.listdir(files_dir)
    file_list = [{'name': file} for file in files]
    return JsonResponse({'files': file_list})

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def upload_file(request):
    if request.method == 'POST':
        if request.FILES:
            uploaded_files = request.FILES.getlist('files')
            saved_files = []
            for uploaded_file in uploaded_files:
                file_path = default_storage.save(os.path.join('uploads', uploaded_file.name),
                                                 ContentFile(uploaded_file.read()))
                saved_files.append({'name': uploaded_file.name})
            return JsonResponse({'message': 'Files uploaded successfully', 'files': saved_files}, status=200)
        else:
            return JsonResponse({'error': 'No files uploaded'}, status=400)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def delete_file(request):
    file_name = request.data.get('fileName')
    file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
        return JsonResponse({'message': 'Файл удален успешно'})
    return JsonResponse({'error': 'Файл не найден'}, status=404)
