import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

import Navbar from './components/Navbar';
import Login from './components/Login';
import EventList from './components/EventList';
import CreateEvent from './components/CreateEvent';
import './App.css'

function App() {
  return (
    <Router>
      <Navbar />
      <div style={{ padding: '20px' }}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/events" element={<EventList />} />
          <Route path="/create-event" element={<CreateEvent />} />
          <Route path="/" element={<Navigate to="/events" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App
