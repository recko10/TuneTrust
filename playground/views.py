from django.shortcuts import render
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
from classifier import upload_blob, safe_delete_blob
from pytube import YouTube


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "tunetrust-b19e33e4ecec.json"

# Create your views here.
@api_view(['GET'])
def demo(request):
    directory_path = 'media/audio_files'
    files = os.listdir(directory_path)
    first_file = files[0] if files else None
    first_file = first_file.replace(" ", "_")
    upload_blob("bucket-quickstart_tunetrust", str(os.path.join(directory_path, first_file)), first_file)
    print("First file:", first_file)
    
    response = JsonResponse({"result" : topProbSpeakers(os.path.join(directory_path, first_file))})

    os.remove(os.path.join(directory_path, first_file))
    safe_delete_blob("bucket-quickstart_tunetrust", first_file)
    print("File deleted:", first_file)  

    return response



class AudioFileUpload(APIView):
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        print(request.data)
        link = request.data['audioUrl'] 
        # url input from user 
        yt = YouTube( 
            str(link))

        try:
            # extract only audio 
            video = yt.streams.filter(only_audio=True).first()
        except KeyError:
            print("Something went wrong! Skipping song")
            return None

        # check for destination to save file 
        print("Enter the destination (leave blank for current directory)") 
        destination = str(f"media/audio_files")

        # download the file 
        out_file = video.download(output_path=destination) 

        # save the file 
        base, ext = os.path.splitext(out_file) 
        new_file = base + '.mp3'
        os.rename(out_file, new_file.replace(" ", "_")) 

        # result of success 
        print(yt.title + " has been successfully downloaded.")

        audio_file = AudioFile.objects.create(file=new_file)
        serializer = AudioFileSerializer(audio_file)
        return Response(serializer.data, status=status.HTTP_201_CREATED)