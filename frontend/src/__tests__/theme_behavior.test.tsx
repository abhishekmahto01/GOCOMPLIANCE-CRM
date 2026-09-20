import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import {
  ThemeProvider,
  useTheme,
  getStoredTheme,
  THEME_STORAGE_KEY,
} from '../context/ThemeContext';
import { ThemeToggle } from '../components/dashboard/ThemeToggle';

// Test consumer component
const ThemeTestConsumer: React.FC = () => {
  const { theme, toggleTheme, setTheme, isDark } = useTheme();

  return (
    <div>
      <span data-testid="theme-value">{theme}</span>
      <span data-testid="is-dark-value">{isDark ? 'true' : 'false'}</span>
      <ThemeToggle />
      <button onClick={() => setTheme('dark')} data-testid="set-dark-btn">
        Set Dark
      </button>
      <button onClick={() => setTheme('light')} data-testid="set-light-btn">
        Set Light
      </button>
      <button onClick={toggleTheme} data-testid="toggle-btn">
        Toggle
      </button>
    </div>
  );
};

describe('GOCOMPLIANCE CRM Theme Behavior & Persistence', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.classList.remove('dark');
    vi.clearAllMocks();
  });

  it('defaults to Light mode when no preference is saved in localStorage', () => {
    expect(localStorage.getItem(THEME_STORAGE_KEY)).toBeNull();
    expect(getStoredTheme()).toBe('light');

    render(
      <ThemeProvider>
        <ThemeTestConsumer />
      </ThemeProvider>
    );

    expect(screen.getByTestId('theme-value')).toHaveTextContent('light');
    expect(screen.getByTestId('is-dark-value')).toHaveTextContent('false');
    expect(document.documentElement.classList.contains('dark')).toBe(false);
    expect(screen.getByRole('button', { name: /Switch to Dark Mode/i })).toBeInTheDocument();
  });

  it('ignores operating system prefers-color-scheme dark preference and strictly defaults to Light', () => {
    // Mock window.matchMedia to simulate OS dark mode preference
    window.matchMedia = vi.fn().mockImplementation((query) => ({
      matches: query === '(prefers-color-scheme: dark)',
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }));

    expect(getStoredTheme()).toBe('light');

    render(
      <ThemeProvider>
        <ThemeTestConsumer />
      </ThemeProvider>
    );

    expect(screen.getByTestId('theme-value')).toHaveTextContent('light');
    expect(document.documentElement.classList.contains('dark')).toBe(false);
  });

  it('falls back to Light mode when localStorage contains invalid or corrupted values', () => {
    const corruptedValues = ['invalid_theme', 'auto', 'SYSTEM', '12345', '{"theme":"dark"}', ''];

    for (const val of corruptedValues) {
      localStorage.setItem(THEME_STORAGE_KEY, val);
      expect(getStoredTheme()).toBe('light');
    }
  });

  it('applies Dark mode and persists preference to localStorage when switched to Dark', async () => {
    const user = userEvent.setup();

    render(
      <ThemeProvider>
        <ThemeTestConsumer />
      </ThemeProvider>
    );

    const toggleBtn = screen.getByRole('button', { name: /Switch to Dark Mode/i });
    await user.click(toggleBtn);

    expect(screen.getByTestId('theme-value')).toHaveTextContent('dark');
    expect(screen.getByTestId('is-dark-value')).toHaveTextContent('true');
    expect(document.documentElement.classList.contains('dark')).toBe(true);
    expect(localStorage.getItem(THEME_STORAGE_KEY)).toBe('dark');
    expect(screen.getByRole('button', { name: /Switch to Light Mode/i })).toBeInTheDocument();
  });

  it('honours and restores saved Dark preference on initial load', () => {
    localStorage.setItem(THEME_STORAGE_KEY, 'dark');
    expect(getStoredTheme()).toBe('dark');

    render(
      <ThemeProvider>
        <ThemeTestConsumer />
      </ThemeProvider>
    );

    expect(screen.getByTestId('theme-value')).toHaveTextContent('dark');
    expect(screen.getByTestId('is-dark-value')).toHaveTextContent('true');
    expect(document.documentElement.classList.contains('dark')).toBe(true);
    expect(screen.getByRole('button', { name: /Switch to Light Mode/i })).toBeInTheDocument();
  });

  it('honours and restores saved Light preference on initial load', () => {
    localStorage.setItem(THEME_STORAGE_KEY, 'light');
    expect(getStoredTheme()).toBe('light');

    render(
      <ThemeProvider>
        <ThemeTestConsumer />
      </ThemeProvider>
    );

    expect(screen.getByTestId('theme-value')).toHaveTextContent('light');
    expect(screen.getByTestId('is-dark-value')).toHaveTextContent('false');
    expect(document.documentElement.classList.contains('dark')).toBe(false);
    expect(screen.getByRole('button', { name: /Switch to Dark Mode/i })).toBeInTheDocument();
  });

  it('allows toggling between Dark and Light mode repeatedly with accurate state', async () => {
    const user = userEvent.setup();

    render(
      <ThemeProvider>
        <ThemeTestConsumer />
      </ThemeProvider>
    );

    // Initial: Light
    expect(screen.getByTestId('theme-value')).toHaveTextContent('light');

    // Switch to Dark
    await user.click(screen.getByTestId('toggle-btn'));
    expect(screen.getByTestId('theme-value')).toHaveTextContent('dark');
    expect(document.documentElement.classList.contains('dark')).toBe(true);
    expect(localStorage.getItem(THEME_STORAGE_KEY)).toBe('dark');

    // Switch back to Light
    await user.click(screen.getByTestId('toggle-btn'));
    expect(screen.getByTestId('theme-value')).toHaveTextContent('light');
    expect(document.documentElement.classList.contains('dark')).toBe(false);
    expect(localStorage.getItem(THEME_STORAGE_KEY)).toBe('light');
  });

  it('supports explicit setTheme programmatic calls', () => {
    render(
      <ThemeProvider>
        <ThemeTestConsumer />
      </ThemeProvider>
    );

    act(() => {
      screen.getByTestId('set-dark-btn').click();
    });
    expect(document.documentElement.classList.contains('dark')).toBe(true);
    expect(localStorage.getItem(THEME_STORAGE_KEY)).toBe('dark');

    act(() => {
      screen.getByTestId('set-light-btn').click();
    });
    expect(document.documentElement.classList.contains('dark')).toBe(false);
    expect(localStorage.getItem(THEME_STORAGE_KEY)).toBe('light');
  });
});
