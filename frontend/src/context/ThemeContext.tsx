import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';

export type Theme = 'light' | 'dark';

export const THEME_STORAGE_KEY = 'gocompliances-theme';

/**
 * Retrieve saved theme from localStorage with safe fallback.
 * Strictly defaults to 'light' for any new user, missing value, or corrupted/unsupported string.
 * Never defaults to dark mode based on OS preferences or media queries.
 */
export function getStoredTheme(): Theme {
  try {
    const saved = localStorage.getItem(THEME_STORAGE_KEY);
    if (saved === 'dark') return 'dark';
    if (saved === 'light') return 'light';
    return 'light';
  } catch {
    return 'light';
  }
}

/**
 * Synchronize the document root class and localStorage state.
 */
export function applyThemeToDocument(theme: Theme): void {
  try {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
      localStorage.setItem(THEME_STORAGE_KEY, 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem(THEME_STORAGE_KEY, 'light');
    }
  } catch (err) {
    console.error('Failed to apply or persist theme:', err);
  }
}

export interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  isDark: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setThemeState] = useState<Theme>(() => getStoredTheme());

  useEffect(() => {
    applyThemeToDocument(theme);
  }, [theme]);

  const setTheme = useCallback((newTheme: Theme) => {
    const resolvedTheme: Theme = newTheme === 'dark' ? 'dark' : 'light';
    setThemeState(resolvedTheme);
    applyThemeToDocument(resolvedTheme);
  }, []);

  const toggleTheme = useCallback(() => {
    setThemeState((prev) => {
      const nextTheme: Theme = prev === 'dark' ? 'light' : 'dark';
      applyThemeToDocument(nextTheme);
      return nextTheme;
    });
  }, []);

  const value: ThemeContextType = {
    theme,
    setTheme,
    toggleTheme,
    isDark: theme === 'dark',
  };

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    const fallbackTheme = getStoredTheme();
    return {
      theme: fallbackTheme,
      setTheme: (newTheme: Theme) => applyThemeToDocument(newTheme),
      toggleTheme: () => applyThemeToDocument(fallbackTheme === 'dark' ? 'light' : 'dark'),
      isDark: fallbackTheme === 'dark',
    };
  }
  return context;
};
