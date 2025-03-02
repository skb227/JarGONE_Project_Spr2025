import React from "react";
import { Link } from "react-router-dom";
import "../styles.css"; // Ensure navbar styles are applied

function Navbar() {
    return (
        <nav className="navbar">
            <div className="navbar__container">
                <Link to="/" id="navbar__logo">JarGONE</Link>
                <div className="navbar__toggle" id="mobile-menu">
                    <span className="bar"></span>
                    <span className="bar"></span>
                    <span className="bar"></span>
                </div>
                <ul className="navbar__menu">
                    <li className="navbar__item">
                        <Link to="/" className="navbar__links">Home</Link>
                    </li>
                    <li className="navbar__item">
                        <Link to="/Translate" className="navbar__links">Translate Legal Doc</Link>
                    </li>
                    <li className="navbar__item">
                        <Link to="/LegalChat" className="navbar__links">Legal Chat Bot</Link>
                    </li>
                    <li className="navbar__btn">
                        <Link to="/Auth" className="button">Login</Link>
                    </li>
                </ul>
            </div>
        </nav>
    );
}

export default Navbar;
