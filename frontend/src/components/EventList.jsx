import React, { useState, useEffect } from 'react';

function EventList() {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const token = localStorage.getItem('access_token');
        const reqHeaders = new Headers();
        reqHeaders.append('Accept', 'application/json');
        
        if (token) {
            reqHeaders.append('Authorization', `Bearer ${token}`);
        }

        fetch('http://localhost:8000/event-manager/events/', {
            method: 'GET',
            headers: reqHeaders,
        }) 
        .then((response) => {
            if (!response.ok) {
                if (response.status === 401) throw new Error("Neautorizat - Login necesar");
                throw new Error("Eroare la preluarea datelor");
            }
            return response.json();
        })
        .then((data) => {
            setEvents(data.items || data); 
            setLoading(false);
        })
        .catch((err) => {
            setError(err.message);
            setLoading(false);
        });
    }, []);

    const handleBuy = async (eventId, eventName) => {
        const token = localStorage.getItem('access_token');
        const email = localStorage.getItem('user_email');

        try {
            const clientsRes = await fetch('http://localhost:8001/clienti/', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const clientsData = await clientsRes.json();
            const currentClient = clientsData.clienti?.find(c => c.email === email);

            if (!currentClient) {
                alert("Profilul de client nu a fost gasit în MongoDB!");
                return;
            }

            const mongoId = currentClient._id || currentClient.id;

            const ticketPayload = {
                evenimentID: parseInt(eventId),
                numarLocuri: 1
            };

            console.log("Trimitere payload către 8001:", ticketPayload);

            const buyRes = await fetch(`http://localhost:8001/clienti/${mongoId}/bilete`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                    'Accept': 'application/json'
                },
                body: JSON.stringify(ticketPayload)
            });

            if (buyRes.status === 201) {
                const result = await buyRes.json();
                alert(`Succes! Bilet cumparat pentru ${eventName}.`);
            } else {
                const errorData = await buyRes.json();
                alert(`Eroare: ${errorData.detail || "Cerere invalidă"}`);
            }
        } catch (err) {
            console.error("Eroare la cumparare:", err);
        }
    };

    if (loading) return <p>Se incarca evenimentele...</p>;
    if (error) return <p style={{ color: 'red' }}>{error}</p>;

    return (
        <div style={{ padding: '20px' }}>
            <h3>Lista Evenimente</h3>
            <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px' }}>
                <thead>
                    <tr style={{ backgroundColor: '#f4f4f4', textAlign: 'left' }}>
                        <th style={styles.th}>Nume</th>
                        <th style={styles.th}>Locatie</th>
                        <th style={styles.th}>Descriere</th>
                        <th style={styles.th}>Locuri</th>
                        <th style={styles.th}>Actiuni</th>
                    </tr>
                </thead>
                <tbody>
                    {events.map((item, index) => {
                        const eventData = item.event; 
                        return (
                            <tr key={eventData.id || index} style={{ borderBottom: '1px solid #ddd' }}>
                                <td style={styles.td}>{eventData.nume}</td>
                                <td style={styles.td}>{eventData.locatie}</td>
                                <td style={styles.td}>{eventData.descriere}</td>
                                <td style={styles.td}>{eventData.numarLocuri}</td>
                                <td style={styles.td}>
                                    <button 
                                        onClick={() => handleBuy(eventData.id, eventData.nume)} 
                                        style={styles.buyBtn}
                                    >
                                        Cumpara
                                    </button>
                                </td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );
}

const styles = {
    th: { padding: '12px', borderBottom: '2px solid #333' },
    td: { padding: '10px' },
    buyBtn: { backgroundColor: '#28a745', color: 'white', border: 'none', padding: '5px 10px', borderRadius: '4px', cursor: 'pointer' }
};

export default EventList;