const API_BASE_URL = 'http://localhost:8000/api/v1';

// Helper function for making API calls
async function makeRequest(method, endpoint, data = null, token = null) {
    const headers = {
        'Content-Type': 'application/json',
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
        method,
        headers,
    };

    if (data) {
        config.body = JSON.stringify(data);
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Request failed');
    }

    return response.json();
}

// Auth API
export const authAPI = {
    login: async (email, password) => {
        return makeRequest('POST', '/auth/login', { email, password });
    },
    register: async (userData) => {
        return makeRequest('POST', '/auth/register', userData);
    },
    getCurrentUser: async (token) => {
        return makeRequest('GET', '/users/me', null, token);
    }
};

// User API
export const userAPI = {
    getAllUsers: async (token) => {
        return makeRequest('GET', '/users', null, token);
    },
    getUserById: async (id, token) => {
        return makeRequest('GET', `/users/${id}`, null, token);
    },
    updateUser: async (id, userData, token) => {
        return makeRequest('PUT', `/users/${id}`, userData, token);
    },
    deleteUser: async (id, token) => {
        return makeRequest('DELETE', `/users/${id}`, null, token);
    }
};