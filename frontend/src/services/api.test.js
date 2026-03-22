import api from './api';
import axios from 'axios';

jest.mock('axios', () => {
    const mockAxios = {
        create: jest.fn(() => mockAxios),
        interceptors: {
            request: { use: jest.fn(), eject: jest.fn() },
            response: { use: jest.fn(), eject: jest.fn() }
        },
        get: jest.fn(),
        post: jest.fn(),
        put: jest.fn(),
        delete: jest.fn()
    };
    return mockAxios;
});

describe('API Service', () => {

    beforeEach(() => {
        localStorage.clear();
    });

    it('creates an axios instance', () => {
        expect(axios.create).toHaveBeenCalled();
    });

    it('sets the authorization header if token exists in localStorage', () => {
        localStorage.setItem('token', 'test_token_123');
        
        // Ensure interceptor was registered
        expect(api.interceptors.request.use).toHaveBeenCalled();
        
        // Extract the interceptor function
        const requestInterceptor = api.interceptors.request.use.mock.calls[0][0];
        
        // Run a fake request through it
        const config = { headers: {} };
        const resultConfig = requestInterceptor(config);
        
        expect(resultConfig.headers.Authorization).toBe('Bearer test_token_123');
    });

    it('does not set authorization header if no token in localStorage', () => {
        // Extract the interceptor function
        const requestInterceptor = api.interceptors.request.use.mock.calls[0][0];
        
        // Run a fake request through it
        const config = { headers: {} };
        const resultConfig = requestInterceptor(config);
        
        expect(resultConfig.headers.Authorization).toBeUndefined();
    });
});
