import React from "react";
import Download from "../components/Download";

function LegalChat() {
    return (
        <div className="legalchat-container">
            <h1>Legal Chat Bot</h1>
            <p>Upload a document to our AI-powered chat bot and allow us to help you understand
                your legal document and any questions you may have.</p>
            <Download />
        </div>
    );
}

export default LegalChat;