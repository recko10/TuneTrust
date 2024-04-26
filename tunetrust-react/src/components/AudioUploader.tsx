import React, { useState } from 'react';
import ArtistProbabilitiesTable from './ArtistProbabilitiesTable.tsx';

const AudioUploader = () => {
    const [audioUrl, setAudioUrl] = useState('');
    const [selectedArtist] = useState('');
    const [submissionResult] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [artistProbs, setArtistProbs] = useState(null);

    async function callApiDemo(selectedArtist: string) {
        setIsLoading(true);
        const queryString = new URLSearchParams({ artist: selectedArtist }).toString();
        const url = `https://tunetrust-cloud-ipynws4cra-wl.a.run.app/playground/demo/?${queryString}`;

        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            const resultObject = data["result"];
            setArtistProbs(resultObject);

            return data["result"];
        } catch (error) {
            console.error('Error calling the API:', error);
        } finally {
            setIsLoading(false);
        }
    }

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        if (!audioUrl) {
            alert('Please provide a URL for an audio file.');
            return;
        }

        setIsLoading(true);

        try {
            // const response = await fetch('https://tunetrust-cloud-ipynws4cra-wl.a.run.app/playground/upload/', {
            //     method: 'POST',
            //     body: formData,
            // });

            const response = await fetch('https://tunetrust-cloud-ipynws4cra-wl.a.run.app/playground/upload/', {
                method: 'POST',
                body: JSON.stringify({ audioUrl }),
                headers: {
                    'Content-Type': 'application/json',
                },
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

        // Here you could validate the URL or fetch the audio data from the URL
        try {
            console.log(await callApiDemo(selectedArtist));
        } catch (error) {
            console.error('Error:', error);
            setIsLoading(false);
        }
    };

    return (
        <div className="fixed-top">
            <div className="container d-flex justify-content-center align-items-center" style={{ minHeight: '100vh' }}>
                <form onSubmit={handleSubmit} style={{ width: '100%', maxWidth: '500px' }}>
                    <div className="mb-3 text-center">
                        <label htmlFor="audioUrl" className="form-label">
                            Enter URL of the Audio File
                        </label>
                        <input
                            type="text"
                            className="form-control"
                            id="audioUrl"
                            value={audioUrl}
                            onChange={e => setAudioUrl(e.target.value)}
                            placeholder="http://example.com/audio.mp3"
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
