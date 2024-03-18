import nemo.collections.asr as nemo_asr
import pandas as pd
import os
import torch.nn as nn
import torch


'''
-TODO featured artists? comparing stems to songs instead of other stems? averaging embeddings? Add reference artist to compareAll function outut
-front end stores one representative drake embedding
-compare acapella to acapella
'''
speaker_model = nemo_asr.models.EncDecSpeakerLabelModel.from_pretrained("nvidia/speakerverification_en_titanet_large")

# Compares one song to the reference (output new row in df)
def compareOne(reference_artist, reference_song, curr_artist, curr_song):
    verify = speaker_model.verify_speakers(f"songs/{reference_artist}/stems/{reference_song}/vocals.wav",f"songs/{curr_artist}/{curr_song}.mp3")
    new_row = {f'Reference Artist': f'{reference_artist}', 'Reference Song Name': f'{reference_song}', 'Compared Artist': f'{curr_artist}', 'Compared Song Name': f'{curr_song}', 'Result': verify}

    return new_row

# Compares every song in the directories to the reference (outputs excel sheet)
def compareAll(reference_artist, reference_song):
    # Set the directory path
    ref_file_path = f'songs/{reference_artist}/stems/{reference_song}/vocals.wav'
    # Set the root directory path
    root_directory_path = 'songs'
    # Name of the folder you want to skip
    folder_to_skip = 'stems'

    df = pd.DataFrame(columns=[f'Reference Song Name', 'Compared Artist', 'Compared Song Name', 'Result'])

    # Loop through each directory in the root directory
    for root, dirs, files in os.walk(root_directory_path):
        # Split the root directory path and check if the folder to skip is part of the current path
        if folder_to_skip in root.split(os.sep):
            continue  # Skip this folder and its subdirectories
        
        for file in files:
            # Check if the file ends with .mp3 or .wav
            if file.endswith('.mp3') or file.endswith('.wav'):
                curr_artist = root.split('/')[1]
                verify = speaker_model.verify_speakers(f"songs/{reference_artist}/stems/{reference_song}/vocals.wav", os.path.join(root, file))
                new_row = {f'{reference_artist} Song Name': f'{reference_song}', 'Compared Artist': f'{curr_artist}', 'Compared Song Name': f'{file}', 'Result': verify}
                df = df.append(new_row, ignore_index=True)
                print(df)
    df.to_excel("output.xlsx")

#Check if two speakers are the same by getting their respective embeddings and running cosine similarity
def sameSpeaker(reference_artist, path_to_upload):
    print("REF: " + reference_artist)
    print("NEW: " + path_to_upload)

    # ref_emb = speaker_model.get_embedding(f"songs/{reference_artist}/stems/{reference_song}/vocals.wav")
    ref_emb = torch.load('embeddings.pt')[reference_artist]
    new_emb = speaker_model.get_embedding(path_to_upload)
    # torch.save({'Drake': ref_emb, 'Taylor Swift': new_emb}, 'embeddings.pt')

    cos = nn.CosineSimilarity(dim=1, eps=1e-6)
    return (cos(ref_emb, new_emb) > 0.5).item()

