from django.shortcuts import render
from classifier import sameSpeaker
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

    #In the future, update this so that we store all the embeddings for the artists. Then, when set the reference artist we just directly refer to their embedding in the database.
    #This will remove the need for these silly if statements
    reference_artist = request.query_params.get('artist', None)

    directory_path = 'media/audio_files'
    files = os.listdir(directory_path)
    first_file = files[0] if files else None
    print("First file:", first_file)

    response = JsonResponse({"result" : sameSpeaker(reference_artist, os.path.join(directory_path, first_file) )})

    os.remove(os.path.join(directory_path, first_file))
    print("File deleted:", first_file)

    return response
    # return render(request, 'hello.html', {'name': 'Adith'})

class AudioFileUpload(APIView):
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        serializer = AudioFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
