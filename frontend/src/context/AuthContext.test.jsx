import { render, screen, act, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useContext } from 'react';
import { AuthContext, AuthProvider } from './AuthContext';
import api from '../services/api';

jest.mock('../services/api');

const TestComponent = () => {
    const { user, loading, login, register, logout } = useContext(AuthContext);

    if (loading) return <div>Loading Auth...</div>;

    return (
        <div>
            <div data-testid="user-info">{user ? user.email : 'No User'}</div>
            <button onClick={() => login('test@example.com', 'password')}>Login</button>
            <button onClick={() => register('Test User', 'test@example.com', 'password')}>Register</button>
            <button onClick={logout}>Logout</button>
        </div>
    );
};

describe('AuthContext', () => {

    beforeEach(() => {
        jest.clearAllMocks();
        localStorage.clear();
    });

    it('initializes with loading true and checks token', async () => {
        api.get.mockResolvedValueOnce({ data: { id: 1, email: 'user@example.com', role: 'user' } });
        localStorage.setItem('token', 'fake-token');

        render(
            <AuthProvider>
                <TestComponent />
            </AuthProvider>
        );

        // Should initially show loading
        expect(screen.getByText('Loading Auth...')).toBeInTheDocument();

        // After loading finishes
        await waitFor(() => {
            expect(screen.queryByText('Loading Auth...')).not.toBeInTheDocument();
            expect(screen.getByTestId('user-info')).toHaveTextContent('user@example.com');
        });

        // Ensure api was called
        expect(api.get).toHaveBeenCalledWith('/auth/me');
    });

    it('removes token and sets no user if api /me fails', async () => {
        api.get.mockRejectedValueOnce(new Error('Invalid token'));
        localStorage.setItem('token', 'bad-token');

        render(
            <AuthProvider>
                <TestComponent />
            </AuthProvider>
        );

        await waitFor(() => {
            expect(screen.getByTestId('user-info')).toHaveTextContent('No User');
        });
        
        expect(localStorage.getItem('token')).toBeNull();
    });

    it('handles login successfully', async () => {
        api.post.mockResolvedValueOnce({
            data: {
                access_token: 'new-token',
                user: { email: 'login@example.com' }
            }
        });

        render(
            <AuthProvider>
                <TestComponent />
            </AuthProvider>
        );

        await waitFor(() => expect(screen.getByTestId('user-info')).toBeInTheDocument());

        await act(async () => {
            screen.getByText('Login').click();
        });

        expect(api.post).toHaveBeenCalledWith('/auth/login', {
            email: 'test@example.com',
            password: 'password'
        });

        expect(localStorage.getItem('token')).toBe('new-token');
        await waitFor(() => {
            expect(screen.getByTestId('user-info')).toHaveTextContent('login@example.com');
        });
    });

    it('handles logout successfully', async () => {
        localStorage.setItem('token', 'old-token');
        // Start without checking /me for simplicity
        api.get.mockRejectedValueOnce(new Error());

        render(
            <AuthProvider>
                <TestComponent />
            </AuthProvider>
        );

        await waitFor(() => expect(screen.getByTestId('user-info')).toBeInTheDocument());

        act(() => {
            screen.getByText('Logout').click();
        });

        expect(localStorage.getItem('token')).toBeNull();
        expect(screen.getByTestId('user-info')).toHaveTextContent('No User');
    });

    it('handles register successfully', async () => {
        // First mock the register call
        api.post.mockResolvedValueOnce({});
        // Then mock the login call that happens inside register
        api.post.mockResolvedValueOnce({
            data: {
                access_token: 'reg-token',
                user: { email: 'test@example.com' }
            }
        });

        render(
            <AuthProvider>
                <TestComponent />
            </AuthProvider>
        );

        await waitFor(() => expect(screen.getByTestId('user-info')).toBeInTheDocument());

        await act(async () => {
            screen.getByText('Register').click();
        });

        expect(api.post).toHaveBeenNthCalledWith(1, '/auth/register', {
            name: 'Test User',
            email: 'test@example.com',
            password: 'password'
        });

        expect(api.post).toHaveBeenNthCalledWith(2, '/auth/login', {
            email: 'test@example.com',
            password: 'password'
        });

        expect(localStorage.getItem('token')).toBe('reg-token');
        await waitFor(() => {
            expect(screen.getByTestId('user-info')).toHaveTextContent('test@example.com');
        });
    });
});
