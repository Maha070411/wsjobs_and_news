import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import ProtectedRoute from './ProtectedRoute';
import { AuthContext } from '../context/AuthContext';

const MockProtectedRoute = ({ user, loading, adminOnly = false }) => {
    return (
        <AuthContext.Provider value={{ user, loading }}>
            <MemoryRouter initialEntries={['/protected']}>
                <Routes>
                    <Route path="/login" element={<div>Login Page</div>} />
                    <Route path="/" element={<div>Home Page</div>} />
                    <Route element={<ProtectedRoute adminOnly={adminOnly} />}>
                        <Route path="/protected" element={<div>Protected Content</div>} />
                    </Route>
                </Routes>
            </MemoryRouter>
        </AuthContext.Provider>
    );
};

describe('ProtectedRoute', () => {

    it('shows loading when context is loading', () => {
        render(<MockProtectedRoute user={null} loading={true} />);
        expect(screen.getByText('Loading...')).toBeInTheDocument();
        expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
    });

    it('redirects to login if user is not authenticated', () => {
        render(<MockProtectedRoute user={null} loading={false} />);
        // Redirects to /login
        expect(screen.getByText('Login Page')).toBeInTheDocument();
        expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
    });

    it('renders outlet if user is authenticated', () => {
        render(<MockProtectedRoute user={{ id: 1, role: 'user' }} loading={false} />);
        expect(screen.getByText('Protected Content')).toBeInTheDocument();
    });

    it('renders outlet if user is admin and route is adminOnly', () => {
        render(<MockProtectedRoute user={{ id: 1, role: 'admin' }} loading={false} adminOnly={true} />);
        expect(screen.getByText('Protected Content')).toBeInTheDocument();
    });

    it('redirects to home if user is not admin and route is adminOnly', () => {
        render(<MockProtectedRoute user={{ id: 1, role: 'user' }} loading={false} adminOnly={true} />);
        // Redirects to /
        expect(screen.getByText('Home Page')).toBeInTheDocument();
        expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
    });
});
