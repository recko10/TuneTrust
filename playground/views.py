from django.shortcuts import render
from classifier import sameSpeaker
from classifier import topProbSpeakers
from django.http import JsonResponse

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import AudioFile
from .serializers import AudioFileSerializer

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import os
from rest_framework.decorators import api_view


# Create your views here.
@api_view(['GET'])
def demo(request):
    directory_path = 'media/audio_files'
    files = os.listdir(directory_path)
    first_file = files[0] if files else None
    print("First file:", first_file)

    response = JsonResponse({"result" : topProbSpeakers(os.path.join(directory_path, first_file))})

    os.remove(os.path.join(directory_path, first_file))
    print("File deleted:", first_file)  

    return response



class AudioFileUpload(APIView):
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        serializer = AudioFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
