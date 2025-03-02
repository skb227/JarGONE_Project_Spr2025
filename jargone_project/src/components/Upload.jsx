import React, { useState } from "react";

const Upload = ({ onUploadComplete }) => {
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [message, setMessage] = useState("");
    const [targetLanguage, setTargetLanguage] = useState("en");

    const commonLanguages = [
        { code: "en", name: "English" },
        { code: "es", name: "Spanish" },
        { code: "fr", name: "French" },
        { code: "de", name: "German" },
        { code: "zh", name: "Chinese" }
    ];

    const handleUpload = async () => {
        if (!file) {
            setMessage("Please select a file first");
            return;
        }

        setUploading(true);
        setMessage("Uploading and processing file...");

        // Create form data for file upload
        const formData = new FormData();
        formData.append("file", file);
        formData.append("language", targetLanguage);

        try {
            console.log("Uploading file, target language:", targetLanguage);

            // Upload file to Flask backend
            const response = await fetch("http://127.0.0.1:5000/upload", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            console.log("Response from backend:", data);

            // Check for translation status
            if (targetLanguage !== 'en' && data.translated_analysis) {
                const langName = commonLanguages.find(l => l.code === targetLanguage)?.name || targetLanguage;
                setMessage(`File processed and translated to ${langName}!`);
            } else {
                setMessage("File processed successfully!");
            }

            // Pass the result back to parent component
            if (onUploadComplete) {
                onUploadComplete(file, data);
            }
        } catch (error) {
            console.error("Upload error:", error);
            setMessage(`Error uploading file: ${error.message}`);
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="upload-form">
            <h3>Upload Legal Document</h3>

            <div className="file-input-container">
                <input
                    type="file"
                    accept="application/pdf"
                    onChange={(e) => setFile(e.target.files[0])}
                    className="file-input"
                />
            </div>

            <div className="language-selector">
                <label>
                    Translate to:
                    <select
                        value={targetLanguage}
                        onChange={(e) => setTargetLanguage(e.target.value)}
                        className="language-dropdown"
                    >
                        {commonLanguages.map(lang => (
                            <option key={lang.code} value={lang.code}>
                                {lang.name}
                            </option>
                        ))}
                    </select>
                </label>
            </div>

            <button
                onClick={handleUpload}
                disabled={uploading || !file}
                className={uploading ? "upload-button uploading" : "upload-button"}
            >
                {uploading ? "Processing..." : "Upload"}
            </button>

            {message && <p className="message">{message}</p>}
        </div>
    );
};

export default Upload;