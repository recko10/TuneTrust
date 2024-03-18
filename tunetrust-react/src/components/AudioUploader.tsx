import React, { useState } from 'react';

const AudioUploader = () => {
    const [audioFile, setAudioFile] = useState<File | null>(null);
    const [selectedArtist, setSelectedArtist] = useState<string>('');
    const [submissionResult, setSubmissionResult] = useState('');
    const [isLoading, setIsLoading] = useState<boolean>(false);

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

    const handleArtistChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        setSelectedArtist(event.target.value);
    };


    async function callApiDemo(selectedArtist: string) {
        setIsLoading(true);
        // Construct the query string with the selected artist
        const queryString = new URLSearchParams({ artist: selectedArtist }).toString();
    
        // Append the query string to the API endpoint URL
        const url = `http://127.0.0.1:8000/playground/demo/?${queryString}`;
        
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
            
            // Use the data from the response
            if (data["result"]) {
                setSubmissionResult("Same artist!"); //Update the state
            } else {
                setSubmissionResult("Different artist!"); //Update the state
            }
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
                const response = await fetch('http://localhost:8000/playground/upload/', {
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
        <div className="container mt-5">
            <form onSubmit={handleSubmit}>
                <div className="mb-3">
                    <label htmlFor="audioFile" className="form-label">Upload Audio File</label>
                    <input
                        type="file"
                        className="form-control"
                        id="audioFile"
                        onChange={handleAudioUpload}
                        accept="audio/*"
                    />
                </div>
                <div className="mb-3">
                    <label htmlFor="artistSelect" className="form-label">Select Artist</label>
                    <select
                        id="artistSelect"
                        className="form-select"
                        value={selectedArtist}
                        onChange={handleArtistChange}
                    >
                        <option value="">Select an artist</option>
                        <option value="Taylor Swift">Taylor Swift</option>
                        <option value="Drake">Drake</option>
                    </select>
                </div>
                <button type="submit" className="btn btn-primary">Submit</button>
                {isLoading && (
                    <div className="mt-3 d-flex justify-content-center">
                        <div className="spinner-border" role="status">
                            <span className="visually-hidden">Loading...</span>
                        </div>
                    </div>
                )}
                {!isLoading && submissionResult && <div className="mt-3">{submissionResult}</div>}
            </form>
        </div>
    );
};

export default AudioUploader;
