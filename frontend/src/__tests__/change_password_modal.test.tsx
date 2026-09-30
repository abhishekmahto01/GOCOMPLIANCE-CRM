import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { ChangePasswordModal } from '../components/dashboard/ChangePasswordModal';
import * as authApi from '../api/auth';
import { AuthProvider } from '../context/AuthContext';

describe('ChangePasswordModal Component', () => {
  const mockOnClose = vi.fn();
  const mockOnSuccessToast = vi.fn();

  beforeEach(() => {
    vi.restoreAllMocks();
    mockOnClose.mockClear();
    mockOnSuccessToast.mockClear();
  });

  it('renders modal with form inputs and password criteria checklist when open', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <ChangePasswordModal
            isOpen={true}
            onClose={mockOnClose}
            onSuccessToast={mockOnSuccessToast}
          />
        </AuthProvider>
      </BrowserRouter>
    );

    expect(screen.getByText('Change Security Password')).toBeInTheDocument();
    expect(screen.getByLabelText('Current Password')).toBeInTheDocument();
    expect(screen.getByLabelText('New Password')).toBeInTheDocument();
    expect(screen.getByLabelText('Confirm New Password')).toBeInTheDocument();
    expect(screen.getByText('Password Requirements:')).toBeInTheDocument();
    expect(screen.getByText('At least 10 characters')).toBeInTheDocument();
    expect(screen.getByText('Uppercase letter (A-Z)')).toBeInTheDocument();
    expect(screen.getByText('Special character (!@#$%)')).toBeInTheDocument();
  });

  it('does not render anything when isOpen is false', () => {
    const { container } = render(
      <BrowserRouter>
        <AuthProvider>
          <ChangePasswordModal
            isOpen={false}
            onClose={mockOnClose}
            onSuccessToast={mockOnSuccessToast}
          />
        </AuthProvider>
      </BrowserRouter>
    );

    expect(container).toBeEmptyDOMElement();
  });

  it('submits valid password change and calls changePasswordApi', async () => {
    const changePasswordSpy = vi.spyOn(authApi, 'changePasswordApi').mockResolvedValue({
      message: 'Password changed successfully. All active sessions have been terminated. Please log in with your new password.',
    });

    const user = userEvent.setup();

    render(
      <BrowserRouter>
        <AuthProvider>
          <ChangePasswordModal
            isOpen={true}
            onClose={mockOnClose}
            onSuccessToast={mockOnSuccessToast}
          />
        </AuthProvider>
      </BrowserRouter>
    );

    const currentInput = screen.getByLabelText('Current Password');
    const newInput = screen.getByLabelText('New Password');
    const confirmInput = screen.getByLabelText('Confirm New Password');

    await user.type(currentInput, 'Admin@12345');
    await user.type(newInput, 'NewSecurePass@2026');
    await user.type(confirmInput, 'NewSecurePass@2026');

    const submitBtn = screen.getByRole('button', { name: /update password/i });
    expect(submitBtn).not.toBeDisabled();

    await user.click(submitBtn);

    await waitFor(() => {
      expect(changePasswordSpy).toHaveBeenCalledWith({
        current_password: 'Admin@12345',
        new_password: 'NewSecurePass@2026',
      });
      expect(mockOnSuccessToast).toHaveBeenCalledWith(
        'Password Updated',
        'Your security password has been changed successfully. Please log in with your new password.'
      );
    });
  });

  it('displays API error message when password update fails on backend', async () => {
    vi.spyOn(authApi, 'changePasswordApi').mockRejectedValue({
      response: {
        status: 400,
        data: {
          detail: 'Current password is incorrect',
        },
      },
    });

    const user = userEvent.setup();

    render(
      <BrowserRouter>
        <AuthProvider>
          <ChangePasswordModal
            isOpen={true}
            onClose={mockOnClose}
            onSuccessToast={mockOnSuccessToast}
          />
        </AuthProvider>
      </BrowserRouter>
    );

    const currentInput = screen.getByLabelText('Current Password');
    const newInput = screen.getByLabelText('New Password');
    const confirmInput = screen.getByLabelText('Confirm New Password');

    await user.type(currentInput, 'WrongPass123!');
    await user.type(newInput, 'NewSecurePass@2026');
    await user.type(confirmInput, 'NewSecurePass@2026');

    const submitBtn = screen.getByRole('button', { name: /update password/i });
    await user.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText('Current password is incorrect')).toBeInTheDocument();
    });
  });
});
