import React, { useState } from "react";

const Login = () => {
    // Login states
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [loginMessage, setLoginMessage] = useState("");

    // Register states
    const [registerUsername, setRegisterUsername] = useState("");
    const [registerPassword, setRegisterPassword] = useState("");
    const [registerMessage, setRegisterMessage] = useState("");

    const handleLogin = async (e) => {
        e.preventDefault();
        const response = await fetch("http://127.0.0.1:5000/api/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ username, password }),
        });

        const data = await response.json();
        if (response.ok) {
            localStorage.setItem("token", data.token);
            setLoginMessage("Welcome back!");
        } else {
            setLoginMessage("Invalid login information");
        }
    };

    const handleRegister = async (e) => {
        e.preventDefault();
        const response = await fetch("http://127.0.0.1:5000/api/register", { // FIXED URL
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ username: registerUsername, password: registerPassword }),
        });

        const data = await response.json();
        if (response.ok) {
            setRegisterMessage("Registered successfully, log in to start!");
        } else {
            setRegisterMessage(data.error || "Registration failed");
        }
    };

    return (

        <div style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            height: "100vh",
            width: "100vw",
            textAlign: "center"
        }}>
            <div style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: "20px",
                padding: "20px",
                border: "1px solid #ccc",
                borderRadius: "10px",
                boxShadow: "0px 0px 10px rgba(0, 0, 0, 0.1)"
            }}>
                {/* LOGIN FORM */}
                <div>
                    <h2>Welcome Back!</h2>
                    <form onSubmit={handleLogin} style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                        <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
                        <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
                        <button type="submit">Login</button>
                    </form>
                    <p>{loginMessage}</p>
                </div>

                {/* REGISTER FORM */}
                <div>
                    <h2>New to JarGone?</h2>
                    <form onSubmit={handleRegister} style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                        <input type="text" placeholder="New Username" value={registerUsername} onChange={(e) => setRegisterUsername(e.target.value)} />
                        <input type="password" placeholder="New Password" value={registerPassword} onChange={(e) => setRegisterPassword(e.target.value)} />
                        <button type="submit">Create</button>
                    </form>
                    <p>{registerMessage}</p>
                </div>
            </div>
        </div>

    );


};

export default Login;
