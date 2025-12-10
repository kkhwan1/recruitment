import React, { useEffect, useState } from 'react';
import { fetchJobs } from '../services/api';

export default function JobList() {
    const [jobs, setJobs] = useState([]);

    useEffect(() => {
        loadJobs();
    }, []);

    const loadJobs = async () => {
        const data = await fetchJobs(50);
        setJobs(data);
    };

    const getRiskColor = (level) => {
        if (level === '고위험') return '#ef4444';
        if (level === '중위험') return '#f59e0b';
        return '#10b981';
    };

    return (
        <div>
            <h2 className="text-2xl font-bold" style={{ marginBottom: '2rem' }}>Job Monitor</h2>
            <div className="glass-card" style={{ padding: '0', overflow: 'hidden' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', color: 'var(--text-primary)' }}>
                    <thead style={{ background: 'rgba(0,0,0,0.2)', textAlign: 'left' }}>
                        <tr>
                            <th style={{ padding: '1rem' }}>Risk</th>
                            <th style={{ padding: '1rem' }}>Title</th>
                            <th style={{ padding: '1rem' }}>Company</th>
                            <th style={{ padding: '1rem' }}>Date</th>
                            <th style={{ padding: '1rem' }}>Source</th>
                        </tr>
                    </thead>
                    <tbody>
                        {jobs.map((job) => (
                            <tr key={job.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                <td style={{ padding: '1rem' }}>
                                    <span style={{ 
                                        padding: '0.25rem 0.75rem', 
                                        borderRadius: '999px', 
                                        fontSize: '0.75rem', 
                                        backgroundColor: \`\${getRiskColor(job.risk_analysis?.risk_level)}20\`,
                                        color: getRiskColor(job.risk_analysis?.risk_level),
                                        border: \`1px solid \${getRiskColor(job.risk_analysis?.risk_level)}\`
                                    }}>
                                        {job.risk_analysis?.risk_level || 'N/A'}
                                    </span>
                                </td>
                                <td style={{ padding: '1rem', fontWeight: '500' }}>
                                    <a href={job.url} target="_blank" rel="noopener noreferrer" style={{ color: 'inherit', textDecoration: 'none' }}>
                                        {job.title}
                                    </a>
                                </td>
                                <td style={{ padding: '1rem', color: 'var(--text-secondary)' }}>{job.company}</td>
                                <td style={{ padding: '1rem', color: 'var(--text-secondary)' }}>{job.crawled_date}</td>
                                <td style={{ padding: '1rem' }}>{job.source_site}</td>
                            </tr>
                        ))}
                </tbody>
            </table>
        </div>
        </div >
    );
}
