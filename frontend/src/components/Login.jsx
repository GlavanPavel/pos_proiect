import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authClient } from '../grpc';

function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const response = await authClient.login({
                username: username,
                password: password
            });

            console.log("Raspuns gRPC primit:", response);

            const token = response.tokenValue;

            if (response.tokenValue) {
                const token = response.tokenValue;
                localStorage.setItem('access_token', token);

                try {
                    const payloadBase64 = token.split('.')[1];
                    const decodedPayload = JSON.parse(atob(payloadBase64));
                    
                    console.log("Payload decodat:", decodedPayload);
                    
                    const userRole = decodedPayload.role; 
                    localStorage.setItem('user_role', userRole);
                    const userEmail = decodedPayload.sub;
                    localStorage.setItem('user_email', userEmail);
                    
                    navigate('/events');
                } catch (e) {
                    console.error("Eroare la decodarea token-ului:", e);
                }
            }
        } catch (err) {
            console.error("Eroare gRPC:", err);
            setError(`Eroare login: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ maxWidth: '400px', margin: '50px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
            <h2>Autentificare gRPC-Web</h2>
            {error && <p style={{ color: 'red', fontSize: '0.9rem' }}>{error}</p>}
            
            <form onSubmit={handleSubmit}>
                <div style={{ marginBottom: '15px' }}>
                    <label style={{ display: 'block', marginBottom: '5px' }}>Email (Username):</label>
                    <input 
                        type="email" 
                        value={username} 
                        onChange={(e) => setUsername(e.target.value)} 
                        required 
                        style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
                    />
                </div>
                <div style={{ marginBottom: '15px' }}>
                    <label style={{ display: 'block', marginBottom: '5px' }}>Parolă:</label>
                    <input 
                        type="password" 
                        value={password} 
                        onChange={(e) => setPassword(e.target.value)} 
                        required 
                        style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
                    />
                </div>
                <button 
                    type="submit" 
                    disabled={loading}
                    style={{ 
                        width: '100%', 
                        padding: '10px', 
                        backgroundColor: loading ? '#ccc' : '#007bff', 
                        color: 'white', 
                        border: 'none',
                        cursor: loading ? 'not-allowed' : 'pointer'
                    }}
                >
                    {loading ? "Se verifica" : "Logheaza-te"}
                </button>
            </form>
        </div>
    );
}

export default Login;