import { useState } from 'react';
import React from 'react';
import './App.css';
import './styles.css';
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";

import Home from "./pages/Home";
import Translate from "./pages/Translate";
import LegalChat from "./pages/LegalChat";
import Login from "./pages/Auth"
import Navbar from "./components/Navbar";

function App() {
  return (
    <Router>
      <Navbar />
      <div className="app-container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/Translate" element={<Translate />} />
          <Route path="/LegalChat" element={<LegalChat />} />
          <Route path="/Auth" element={<Login />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;


/*
function App() {
  return (
    <Router>
      <nav className="navbar">
        <ul>
          <li><Link to="/">Home</Link></li>
          <li><Link to="/Translate">Translate Document</Link></li>
          <li><Link to="/LegalChat">Legal Terms Chat</Link></li>
        </ul>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/Translate" element={<Translate />} />
        <Route path="/LegalChat" element={<LegalChat />} />
      </Routes>
    </Router>
  );
}

export default App;*/