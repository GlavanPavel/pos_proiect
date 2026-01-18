import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function CreateEvent() {
    const [event, setEvent] = useState({ nume: '', locatie: '', descriere: '', numarLocuri: 10 });
    const navigate = useNavigate();
    const role = localStorage.getItem('user_role');

    if (role !== 'admin' && role !== 'owner') {
        return <div className="error">Doar adminii sau ownerii pot crea evenimente.</div>;
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem('access_token');

        const payload = {
            ...event,
            id_owner: 0
        };

        try {
            const res = await fetch('http://localhost:8000/event-manager/events/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                navigate('/events');
            } else {
                const errorData = await res.json();
                console.error("Eroare server:", errorData);
                alert("Eroare la crearea evenimentului. Verifică consola.");
            }
        } catch (error) {
            console.error("Network error:", error);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="create-form">
            <h2>Adauga Eveniment</h2>
            <input type="text" placeholder="Nume Eveniment" onChange={e => setEvent({...event, nume: e.target.value})} required />
            <input type="text" placeholder="Locatie" onChange={e => setEvent({...event, locatie: e.target.value})} required />
            <input type="number" placeholder="Locuri" onChange={e => setEvent({...event, numarLocuri: parseInt(e.target.value)})} required />
            <button type="submit">Creeaza</button>
        </form>
    );
}

export default CreateEvent;