import { useNavigate, Link } from 'react-router-dom';
import { authClient } from '../grpc';

function Navbar() {
  const navigate = useNavigate();
  const role = localStorage.getItem('user_role');

  const handleLogout = async () => {
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        await authClient.logout({ token: token });
      } catch (err) {
        console.error("Eroare logout:", err);
      }
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_role');
    navigate('/login');
  };

  if (!role) return null;

  return (
    <nav style={styles.nav}>
      <div style={styles.leftSection}>
        <div style={styles.logo}>EventManager</div>
        <Link to="/events" style={styles.link}>Evenimente</Link>
        
        {(role === 'admin' || role === 'owner') && (
          <Link to="/create-event" style={styles.createLink}>
            Adauga Eveniment
          </Link>
        )}
      </div>

      <div style={styles.rightSection}>
        <div style={styles.userBadge}>
          <span style={styles.roleText}>{role.toUpperCase()}</span>
        </div>
        <button onClick={handleLogout} style={styles.logoutBtn}>
          Deconectare
        </button>
      </div>
    </nav>
  );
}

const styles = {
  nav: {
    padding: '0 2rem',
    height: '64px',
    background: '#1a1a1a',
    color: 'white',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    boxShadow: '0 2px 10px rgba(0,0,0,0.3)',
    position: 'sticky',
    top: 0,
    zIndex: 1000
  },
  leftSection: {
    display: 'flex',
    alignItems: 'center',
    gap: '30px'
  },
  logo: {
    fontSize: '1.2rem',
    fontWeight: 'bold',
    marginRight: '10px',
    color: '#007bff'
  },
  rightSection: {
    display: 'flex',
    alignItems: 'center',
    gap: '20px'
  },
  link: {
    color: '#efefef',
    textDecoration: 'none',
    fontSize: '0.95rem',
    transition: 'color 0.2s'
  },
  createLink: {
    color: '#4CAF50',
    textDecoration: 'none',
    fontWeight: '600',
    fontSize: '0.95rem'
  },
  userBadge: {
    background: '#333',
    padding: '4px 12px',
    borderRadius: '15px',
    border: '1px solid #444'
  },
  roleText: {
    fontSize: '0.75rem',
    letterSpacing: '1px',
    fontWeight: 'bold',
    color: '#aaa'
  },
  logoutBtn: {
    cursor: 'pointer',
    background: 'transparent',
    color: '#ff4444',
    border: '1px solid #ff4444',
    padding: '6px 16px',
    borderRadius: '4px',
    fontSize: '0.9rem',
    fontWeight: '600',
    transition: 'all 0.2s',
  }
};

export default Navbar;