import React from "react";
import Download from "../components/Download";

function Translate() {
    return (
        <div className="translate-container">
            <h1>Translate your Document</h1>
            <p>Upload a legal document and we'll translate it to your preferred language</p>
            <Download />
        </div>
    );
}

export default Translate;