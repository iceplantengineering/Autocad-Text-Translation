import React, { useState } from 'react';
import ReactDOM from 'react-dom/client';

const App = () => {
    const [file, setFile] = useState(null);
    const [jobId, setJobId] = useState(null);
    const [status, setStatus] = useState('idle');
    const [progress, setProgress] = useState(0);
    const [error, setError] = useState(null);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile && selectedFile.name.toLowerCase().endsWith('.dwg')) {
            setFile(selectedFile);
            setError(null);
        } else {
            setError('Please select a valid DWG file');
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setStatus('uploading');
        setProgress(0);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:8000/upload', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                setJobId(data.job_id);
                setStatus('processing');
                pollJobStatus(data.job_id);
            } else {
                const errorData = await response.json();
                setError(errorData.detail || 'Upload failed');
                setStatus('idle');
            }
        } catch (err) {
            setError('Network error: ' + err.message);
            setStatus('idle');
        }
    };

    const pollJobStatus = async (id) => {
        const interval = setInterval(async () => {
            try {
                const response = await fetch(`http://localhost:8000/jobs/${id}`);
                if (response.ok) {
                    const job = await response.json();
                    setProgress(job.progress);

                    if (job.status === 'completed') {
                        setStatus('completed');
                        clearInterval(interval);
                    } else if (job.status === 'failed') {
                        setError(job.error_message || 'Processing failed');
                        setStatus('idle');
                        clearInterval(interval);
                    }
                }
            } catch (err) {
                setError('Error checking status: ' + err.message);
                clearInterval(interval);
            }
        }, 2000);
    };

    const handleDownload = async () => {
        if (!jobId) return;

        try {
            const response = await fetch(`http://localhost:8000/download/${jobId}`);
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `translated_${file.name}`;
                a.click();
                window.URL.revokeObjectURL(url);
            }
        } catch (err) {
            setError('Download failed: ' + err.message);
        }
    };

    return (
        <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
            <h1>AutoCAD DWG Chinese to Japanese Translator</h1>

            <div style={{ marginBottom: '20px' }}>
                <input type="file" accept=".dwg" onChange={handleFileChange} />
            </div>

            {file && (
                <div>
                    <p>Selected file: {file.name}</p>
                    <button
                        onClick={handleUpload}
                        disabled={status !== 'idle'}
                        style={{ padding: '10px 20px', marginRight: '10px' }}
                    >
                        {status === 'uploading' ? 'Uploading...' : 'Upload and Translate'}
                    </button>
                </div>
            )}

            {status === 'processing' && (
                <div>
                    <p>Processing... {progress}%</p>
                    <div style={{
                        width: '100%',
                        height: '20px',
                        backgroundColor: '#e0e0e0',
                        borderRadius: '10px',
                        overflow: 'hidden'
                    }}>
                        <div style={{
                            width: `${progress}%`,
                            height: '100%',
                            backgroundColor: '#4CAF50',
                            transition: 'width 0.3s ease'
                        }}></div>
                    </div>
                </div>
            )}

            {status === 'completed' && (
                <div>
                    <p>Translation completed!</p>
                    <button
                        onClick={handleDownload}
                        style={{ padding: '10px 20px', backgroundColor: '#2196F3', color: 'white' }}
                    >
                        Download Translated File
                    </button>
                </div>
            )}

            {error && (
                <div style={{ color: 'red', marginTop: '20px' }}>
                    <p>Error: {error}</p>
                </div>
            )}

            <div style={{ marginTop: '40px', padding: '20px', backgroundColor: '#f5f5f5', borderRadius: '5px' }}>
                <h3>Features:</h3>
                <ul>
                    <li>Supports AutoCAD DWG files (2012 and later)</li>
                    <li>Extracts Chinese text from various entities (MTEXT, TEXT, ATTRIB, DIMTEXT)</li>
                    <li>Translates to Japanese using professional translation services</li>
                    <li>Preserves original formatting and layout</li>
                    <li>Downloads translated DWG file</li>
                </ul>
            </div>
        </div>
    );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);