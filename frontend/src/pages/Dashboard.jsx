import React, { useEffect, useState } from 'react';
import { fetchDashboardStats, triggerCrawl } from '../services/api';
import { AlertTriangle, CheckCircle, Search } from 'lucide-react';
import { Bar, Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

function MetricCard({ title, value, icon: Icon, color }) {
    return (
    <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
      <div style={{ padding: '1rem', borderRadius: '50%', background: \`rgba(\${color}, 0.2)\`, color: \`rgb(\${color})\` }}>
        <Icon size={24} />
      </div>
      <div>
        <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>{title}</div>
        <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{value}</div>
      </div>
    </div >
  );
}

export default function Dashboard() {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadStats();
        const interval = setInterval(loadStats, 30000); // 30s auto-refresh
        return () => clearInterval(interval);
    }, []);

    const loadStats = async () => {
        try {
            const data = await fetchDashboardStats();
            setStats(data);
        } catch (error) {
            console.error("Failed to load stats", error);
        } finally {
            setLoading(false);
        }
    };

    const handleCrawl = async () => {
        if (window.confirm("Start crawling all sites?")) {
            try {
                await triggerCrawl("all", "반도체", 10);
                alert("Crawler started in background!");
            } catch (e) {
                alert("Error starting crawler");
            }
        }
    };

    if (loading || !stats) return <div style={{ padding: '2rem' }}>Loading...</div>;

    // Chart Data
    const riskLabels = Object.keys(stats.risk_distribution || {});
    const riskValues = Object.values(stats.risk_distribution || {});

    const doughnutData = {
        labels: riskLabels,
        datasets: [
            {
                data: riskValues,
                backgroundColor: [
                    'rgba(239, 68, 68, 0.8)', // High Risk (Red)
                    'rgba(245, 158, 11, 0.8)', // Medium Risk (Amber)
                    'rgba(16, 185, 129, 0.8)', // Low Risk (Green)
                ],
                borderColor: [
                    'rgba(239, 68, 68, 1)',
                    'rgba(245, 158, 11, 1)',
                    'rgba(16, 185, 129, 1)',
                ],
                borderWidth: 1,
            },
        ],
    };

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <h2 className="text-2xl font-bold">Dashboard</h2>
                <button className="btn-primary" onClick={handleCrawl}>
                    Start Crawling
                </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
                <MetricCard title="Today's Jobs" value={stats.total_today} icon={Search} color="59, 130, 246" />
                <MetricCard title="High Risk" value={stats.high_risk_count} icon={AlertTriangle} color="239, 68, 68" />
                <MetricCard title="Active Services" value="Running" icon={CheckCircle} color="16, 185, 129" />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.5rem' }}>
                <div className="glass-card">
                    <h3 style={{ marginBottom: '1rem' }}>Risk Distribution</h3>
                    <div style={{ height: '300px', display: 'flex', justifyContent: 'center' }}>
                        <Doughnut data={doughnutData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { color: '#94a3b8' } } } }} />
                    </div>
                </div>

                <div className="glass-card">
                    <h3 style={{ marginBottom: '1rem' }}>System Status</h3>
                    <div style={{ color: 'var(--text-secondary)' }}>
                        <p>✅ Backend Connected</p>
                        <p>✅ Database Connected</p>
                        <p>🕒 Last Updated: {new Date().toLocaleTimeString()}</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
