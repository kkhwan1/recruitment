import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { LayoutDashboard, List, Settings } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import JobList from './pages/JobList';

function Layout({ children }) {
  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <nav style={{ width: '250px', borderRight: '1px solid rgba(255,255,255,0.1)', padding: '2rem' }}>
        <h1 className="text-2xl font-bold mb-8 gradient-text" style={{ fontSize: '1.5rem', marginBottom: '2rem' }}>
          Recruit<br />Guardian
        </h1>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)', textDecoration: 'none', padding: '0.5rem', borderRadius: '0.5rem', transition: 'background 0.2s' }} className="nav-link">
            <LayoutDashboard size={20} /> Dashboard
          </Link>
          <Link to="/jobs" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)', textDecoration: 'none', padding: '0.5rem', borderRadius: '0.5rem' }} className="nav-link">
            <List size={20} /> Jobs Monitor
          </Link>
        </div>
      </nav>

      {/* Main Content */}
      <main style={{ flex: 1, padding: '2rem' }}>
        {children}
      </main>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/jobs" element={<JobList />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
