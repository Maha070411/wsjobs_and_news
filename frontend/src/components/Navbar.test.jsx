import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Navbar from './Navbar';
import { AuthContext } from '../context/AuthContext';

const renderNavbar = (userValue) => {
    return render(
        <AuthContext.Provider value={userValue}>
            <MemoryRouter>
                <Navbar />
            </MemoryRouter>
        </AuthContext.Provider>
    );
};

describe('Navbar Component', () => {

    it('renders login and register links when not authenticated', () => {
        renderNavbar({ user: null, logout: jest.fn() });
        
        expect(screen.getByText('Log in')).toBeInTheDocument();
        expect(screen.getByText('Sign up')).toBeInTheDocument();
        expect(screen.getByText('JobHub')).toBeInTheDocument();
        
        expect(screen.queryByText('Logout')).not.toBeInTheDocument();
    });

    it('renders dashboard and logout links when authenticated as user', () => {
        renderNavbar({ user: { role: 'user', name: 'John User' }, logout: jest.fn() });
        
        expect(screen.getByText('Dashboard')).toBeInTheDocument();
        expect(screen.getByText('Logout')).toBeInTheDocument();
        expect(screen.getByText('Hi, John User')).toBeInTheDocument(); // Profile dropdown / name
        
        expect(screen.queryByText('Log in')).not.toBeInTheDocument();
        expect(screen.queryByText('Admin')).not.toBeInTheDocument();
    });

    it('renders admin link when authenticated as admin', () => {
        renderNavbar({ user: { role: 'admin', name: 'Admin Boss' }, logout: jest.fn() });
        
        // Mobile and Desktop may both render the link, use getAllBy or similar if duplicates
        const adminLinks = screen.getAllByText('Admin');
        expect(adminLinks.length).toBeGreaterThan(0);
        
        expect(screen.getByText('Logout')).toBeInTheDocument();
        expect(screen.getByText('Hi, Admin Boss')).toBeInTheDocument();
    });

    it('calls logout when logout button is clicked', () => {
        const mockLogout = jest.fn();
        renderNavbar({ user: { role: 'user', name: 'Test' }, logout: mockLogout });
        
        const logoutBtn = screen.getByText('Logout');
        logoutBtn.click();
        
        expect(mockLogout).toHaveBeenCalledTimes(1);
    });

});
