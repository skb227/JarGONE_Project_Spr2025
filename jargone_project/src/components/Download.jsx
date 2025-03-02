import React, { useState } from "react";
import Upload from "./Upload";

const Download = () => {
    const [file, setFile] = useState(null);
    const [processingResult, setProcessingResult] = useState(null);
    const [message, setMessage] = useState("");
    const [activeTab, setActiveTab] = useState("document"); // "document" or "analysis"

    const handleFileUpload = (uploadedFile, result) => {
        if (!uploadedFile || !result) {
            setMessage("File upload failed or no analysis result available");
            return;
        }

        setFile(uploadedFile);
        setProcessingResult(result);
        setMessage("Document processed successfully");

        console.log("Processing result:", result);
    };

    const handleDownload = async () => {
        if (!processingResult || !processingResult.result_file) {
            setMessage("No processed file available for download");
            return;
        }

        try {
            // Trigger download
            const response = await fetch(`http://127.0.0.1:5000/download/${processingResult.result_file}`);

            if (!response.ok) {
                throw new Error(`Download failed: ${response.status} ${response.statusText}`);
            }

            // Create and trigger download link
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = processingResult.result_file;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            setMessage("File downloaded successfully");
        } catch (error) {
            console.error("Download error:", error);
            setMessage(`Error downloading file: ${error.message}`);
        }
    };

    // Determine which texts to display
    const displayDocumentText = processingResult?.translated_document || processingResult?.original_text;
    const displayAnalysisText = processingResult?.translated_analysis || processingResult?.ai_analysis;

    // Check if we have translations
    const isTranslated = processingResult?.is_translated && processingResult?.target_language !== 'en';

    // Tab selection style
    const tabStyle = {
        padding: "8px 16px",
        marginRight: "5px",
        cursor: "pointer",
        border: "1px solid #ddd",
        borderRadius: "4px 4px 0 0",
        backgroundColor: "#f5f5f5"
    };

    const activeTabStyle = {
        ...tabStyle,
        backgroundColor: "white",
        borderBottom: "none",
        fontWeight: "bold"
    };

    return (
        <div className="upload-container">
            <h2>Upload and Process Your Document</h2>
            <Upload onUploadComplete={handleFileUpload} />

            {processingResult && (
                <div className="result-container">
                    <h3>
                        {isTranslated
                            ? `Translated Document (to ${processingResult.target_language})`
                            : "Document Content"}
                    </h3>

                    <div className="tabs">
                        <span
                            style={activeTab === "document" ? activeTabStyle : tabStyle}
                            onClick={() => setActiveTab("document")}
                        >
                            Document Content
                        </span>
                        <span
                            style={activeTab === "analysis" ? activeTabStyle : tabStyle}
                            onClick={() => setActiveTab("analysis")}
                        >
                            Legal Analysis
                        </span>
                    </div>

                    <div className="analysis-text">
                        {activeTab === "document" ? (
                            <p>{displayDocumentText}</p>
                        ) : (
                            <p>{displayAnalysisText}</p>
                        )}
                    </div>

                    <button onClick={handleDownload}>
                        Download {isTranslated ? "Translated " : ""}Document
                    </button>
                </div>
            )}

            {message && <p className="message">{message}</p>}
        </div>
    );
};

export default Download;