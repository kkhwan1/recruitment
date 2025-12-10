import axios from 'axios';

const API_Base = 'http://127.0.0.1:8000/api';

const api = axios.create({
    baseURL: API_Base,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const fetchJobs = async (limit = 50, skip = 0, riskLevel = null) => {
    const params = { limit, skip };
    if (riskLevel) params.risk_level = riskLevel;
    const response = await api.get('/jobs', { params });
    return response.data;
};

export const fetchDashboardStats = async () => {
    const response = await api.get('/dashboard/stats');
    return response.data;
};

export const triggerCrawl = async (site, keyword, maxJobs) => {
    const response = await api.post('/crawlers/crawl', { site, keyword, max_jobs: maxJobs });
    return response.data;
};

export default api;
