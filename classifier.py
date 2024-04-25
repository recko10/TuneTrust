import nemo.collections.asr as nemo_asr
import os
import torch.nn as nn
import torch
from pydub import AudioSegment
import glob
from google.cloud import storage
import requests
import base64


speaker_model = nemo_asr.models.EncDecSpeakerLabelModel.from_pretrained("nvidia/speakerverification_en_titanet_large")

#TODO write function to remove all spaces from song file names when they are uploaded (replace with underscore)

def topProbSpeakers(path_to_upload):
    print("UPLOADED: " + path_to_upload)

    # speakerDR(path_to_upload) #TODO replace with parallelized version

    artist_to_probs = {}
    passes = 1
    for i in range(1, passes + 1):
        chunkify(path_to_upload, 10 * i)

        cos = nn.CosineSimilarity(dim=1, eps=1e-6)
        threshold = 0.58 #0.5 originally
        ref_embs = torch.load('embeddings.pt')

        directory = 'diarization_temp/'
        for filename in os.listdir(directory):
            if filename.endswith(".mp3"):
                new_emb = speaker_model.get_embedding(os.path.join(directory, filename))
                sorted_embs = map(lambda item: (item[0], cos(item[1], new_emb).item()), ref_embs.items())
                sorted_embs = filter(lambda x: x[1] > threshold, sorted_embs)
                temp = dict(sorted_embs)
                # Add new artists to running list of potentially featured artists
                for key, value in temp.items():
                    if key not in artist_to_probs:
                        artist_to_probs[key] = [value, 1]  # Store value and count
                    else:
                        # Increment artist score and count
                        artist_to_probs[key][0] += value
                        artist_to_probs[key][1] += 1

        deleteChunks()

    # Average the values based on the count and update a new dictionary
    averaged_probs = {}
    for key, (total_prob, count) in artist_to_probs.items():
        averaged_probs[key] = total_prob / count

    # Now, use averaged_probs for further processing if needed
    artist_to_probs = averaged_probs


    return dict(sorted(artist_to_probs.items(), key=lambda item: item[1], reverse=True))

#Splits audio into chunks of length n seconds and then stores them in the 'diarization_temp' directory
def chunkify(path_to_upload, n):
    audio = AudioSegment.from_file(path_to_upload)
    chunk_length_ms = n * 1000
    chunks = audio[::chunk_length_ms]
    for i, chunk in enumerate(chunks):
        output_path = f"diarization_temp/chunk_{i}.mp3"
        chunk.export(output_path, format="mp3")
        print(f"Exported {output_path}")

#Function to delete all files in the diarization_temp directory
def deleteChunks():
    directory = 'diarization_temp/'
    for filename in os.listdir(directory):
        if filename.endswith(".mp3"):
            os.remove(os.path.join(directory, filename))

#Cache all the speaker embeddings to a serialized file. To setup for this function, put all songs you want to convert in the songs folder (follow the structure that is outlined).
def saveAllSpeakers():

    artist_to_emb = {}
    # Path to the "songs" directory
    songs_dir = 'songs/'
    print("here")
    # Iterate through each folder in the directory
    for folder_name in os.listdir(songs_dir):
        folder_path = os.path.join(songs_dir, folder_name)
        
        # Check if the current item is indeed a folder
        if os.path.isdir(folder_path):
            # Path to the "stems" folder within the current folder
            stems_folder_path = os.path.join(folder_path, 'stems')
            
            # Check if the "stems" folder exists
            if os.path.isdir(stems_folder_path):
                print(f'Processing folder: {folder_name}')
                print(f'Entering "stems" folder within: {folder_name}')
                
                stems_sub_folders = [f for f in os.listdir(stems_folder_path) if os.path.isdir(os.path.join(stems_folder_path, f))]
                if stems_sub_folders:
                    artist_to_emb[folder_name] = []
                    for i in range(len(stems_sub_folders)):
                        inner_folder_name = stems_sub_folders[i]
                        inner_folder_path = os.path.join(stems_folder_path, inner_folder_name)
                        
                        # Process the inner folder here
                        print(f'Entering folder within "stems": {inner_folder_name}')
                        
                        file_path = os.path.join(inner_folder_path, "vocals.wav")
                        # Process each file within the inner folder here

                        print(f'Found file in inner folder: {file_path}')
                        curr_emb = speaker_model.get_embedding(file_path)
                        artist_to_emb[folder_name] += [curr_emb]

                else:
                    print(f'No folder found within "stems" folder in: {folder_name}')
            else:
                print(f'No "stems" folder found in: {folder_name}')

    torch.save({key: torch.mean(torch.stack(value), dim=0) for key, value in artist_to_emb.items()}, 'embeddings.pt')
    
#Take an audio file as input and diarize it (ensure that no paths have spaces in them)
def speakerDR(path_to_upload):

    songName = os.path.basename(path_to_upload)
    print("SONG NAME: " + songName)

    # Define the URL and the headers
    url = 'http://129.159.43.141:5001/predictions'
    headers = {'Content-Type': 'application/json; charset=utf-8'}

    # Define the payload data
    data = {
        "input": {
            "path_to_upload": f"https://storage.googleapis.com/bucket-quickstart_tunetrust/{songName}"
        }
    }

    # Send the POST request
    response = requests.post(url, json=data, headers=headers)

    # Your base64 URL
    data_url = response.json()['output']

    # Strip the prefix to get only the base64 part
    _, base64_data = data_url.split(',', 1)

    # Decode the base64 data to get the original content
    decoded_data = base64.b64decode(base64_data).decode('utf-8')

    # Save the decoded data to a file
    with open('audio.rttm', 'w') as file:
        file.write(decoded_data)
    print("File downloaded and saved successfully.")


    segments = parse_rttm("audio.rttm")
    extract_segments(path_to_upload, segments)
    concatenate_speaker_segments(path_to_upload, segments)
    os.remove('audio.rttm')

#Load an rttm file into a format we can process
def parse_rttm(rttm_file_path):
    segments = []
    with open(rttm_file_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if parts[0] == 'SPEAKER':
                file_id, start, duration, speaker_id = parts[1], float(parts[3]), float(parts[4]), parts[7]
                segments.append((file_id, start, duration, speaker_id))
    return segments

#Extract the segments of the audio file and annotate the speakers 
def extract_segments(audio_path, segments):
    audio = AudioSegment.from_file(audio_path)
    for i, (file_id, start, duration, speaker_id) in enumerate(segments):
        start_ms = start * 1000
        end_ms = start_ms + (duration * 1000)
        segment_audio = audio[start_ms:end_ms]
        output_path = f"diarization_temp/speaker_{speaker_id}_segment_{i}.mp3"
        segment_audio.export(output_path, format="mp3")
        print(f"Exported {output_path}")

#Combine all the extracted segments to create separate tracks for each speaker
def concatenate_speaker_segments(audio_path, segments):
    audio = AudioSegment.from_file(audio_path)
    speakers_audio = {}

    # Group segments by speaker and concatenate them
    for file_id, start, duration, speaker_id in segments:
        start_ms = start * 1000
        end_ms = start_ms + (duration * 1000)
        segment_audio = audio[start_ms:end_ms]

        if speaker_id not in speakers_audio:
            speakers_audio[speaker_id] = segment_audio
        else:
            speakers_audio[speaker_id] += segment_audio

    # Export each speaker's concatenated segments and then clean up
    speaker_ids = []
    for speaker_id, speaker_audio in speakers_audio.items():
        output_path = f"diarization_temp/speaker_{speaker_id}_full.mp3"
        speaker_audio.export(output_path, format="mp3")
        print(f"Exported {output_path}")
        speaker_ids.append(speaker_id)

    cleanup_segment_files(speaker_ids)

#Cleanup segments directory to save space
def cleanup_segment_files(speaker_ids, directory="diarization_temp"):
    # Delete individual segment files for each speaker
    for speaker_id in speaker_ids:
        segment_files = glob.glob(f"{directory}/speaker_{speaker_id}_segment_*.mp3")
        for file_path in segment_files:
            os.remove(file_path)
            print(f"Deleted {file_path}")

#Cleanup the full speaker files from the directory--use to reset everything to the original state
def cleanup_full_files(directory="diarization_temp"):
    full_speaker_files = glob.glob(f'{directory}/speaker_*_full.mp3')

    for file_path in full_speaker_files:
        os.remove(file_path)
        print(f"Deleted {file_path}")

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # The path to your file to upload
    # The ID to give your file in GCS

    # Initializes a client
    storage_client = storage.Client()

    # The name of the bucket
    bucket = storage_client.bucket(bucket_name)

    # Creates a new blob and uploads the file's content.
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

from google.cloud import storage

def delete_blob(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    # The ID of your GCS bucket
    # The ID of the GCS object to delete

    # Initialize a client
    storage_client = storage.Client()

    # Get the bucket
    bucket = storage_client.bucket(bucket_name)

    # Get the blob
    blob = bucket.blob(blob_name)

    # Delete the blob
    blob.delete()

    print(f"Blob {blob_name} deleted.")

def safe_delete_blob(bucket_name, blob_name):
    try:
        delete_blob(bucket_name, blob_name)
    except storage.exceptions.NotFound:
        print(f"The blob {blob_name} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

