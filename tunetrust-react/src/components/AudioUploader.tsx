import React, { useState } from 'react';
import ArtistProbabilitiesTable from './ArtistProbabilitiesTable.tsx';

const AudioUploader = () => {
    const [audioFile, setAudioFile] = useState<File | null>(null);
    const [selectedArtist, _setSelectedArtist] = useState<string>('');
    const [submissionResult, _setSubmissionResult] = useState('');
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [artistProbs, setArtistProbs] = useState(null);

    const handleAudioUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files && event.target.files[0]) {
            const file = event.target.files[0];
            if (file.type.startsWith('audio/')) {
                setAudioFile(file);
            } else {
                alert('Please select an audio file.');
            }
        }
    };

    async function callApiDemo(selectedArtist: string) {
        setIsLoading(true);
        // Construct the query string with the selected artist
        const queryString = new URLSearchParams({ artist: selectedArtist }).toString();
    
        // Append the query string to the API endpoint URL
        const url = `http://184.23.21.112:8000/playground/demo/?${queryString}`; //TODO change from localhost
        
        try {
            // Make a GET request to the API with the selected artist as a parameter
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });
    
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
    
            // Parse the JSON response
            const data = await response.json();
            
            const resultObject = data["result"]; // Assuming this is your object
            setArtistProbs(resultObject)
            
            return data["result"];
        } catch (error) {
            console.error('Error calling the API:', error);
        } finally {
            setIsLoading(false);
        }
    }
    
    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        if (!audioFile) {
            alert('Please upload an audio file.');
            return;
        }
        setIsLoading(true);

        if (audioFile) {
            const formData = new FormData();
            formData.append('file', audioFile);
            formData.append('artist', selectedArtist); // Include the selected artist in the form data

            try {
                const response = await fetch('http://184.23.21.112:8000/playground/upload/', { //TODO change from localhost
                    method: 'POST',
                    body: formData,
                });

                if (response.ok) {
                    console.log('File successfully uploaded');
                    const data = await response.json();
                    console.log(data);
                } else {
                    console.error('Upload failed');
                    setIsLoading(false);
                }
            } catch (error) {
                console.error('Error:', error);
            }

            try {
                console.log(await callApiDemo(selectedArtist));
            } catch (error) {
                console.error('Error:', error);
                setIsLoading(false);
            }
        }
    };

    return (
        <div className="fixed-top">
        <div className="container d-flex justify-content-center align-items-center" style={{ minHeight: '100vh' }}>
            <form onSubmit={handleSubmit} style={{ width: '100%', maxWidth: '500px' }}>
                <div className="mb-3 text-center">
                    <label htmlFor="audioFile" className="form-label">
                    Upload a Song to Inspect
                    </label>
                    <input
                        type="file"
                        className="form-control"
                        id="audioFile"
                        onChange={handleAudioUpload}
                        accept="audio/*"
                    />
                    
                </div>
                <div className="d-grid gap-2">
                    <button type="submit" className="btn btn-primary">Submit</button>
                </div>
                {isLoading && (
                    <div className="mt-3 d-flex justify-content-center">
                        <div className="spinner-border" role="status">
                            <span className="visually-hidden">Loading...</span>
                        </div>
                    </div>
                )}
                {!isLoading && submissionResult && (
                    <div className="alert alert-success mt-3 text-center">{submissionResult}</div>
                )}
                <div className="mt-3">
                {artistProbs && <ArtistProbabilitiesTable data={artistProbs} />}
                </div>
            </form>
        </div>
        </div>
    );
    
};

export default AudioUploader;
