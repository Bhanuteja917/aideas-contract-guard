import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

type ThemeName = 'light' | 'dark' | 'linear' | 'vercel' | 'minimalist';

interface ThemeContextType {
  themeName: ThemeName;
  setTheme: (themeName: ThemeName) => void;
  availableThemes: ThemeName[];
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [themeName, setThemeName] = useState<ThemeName>(() => {
    const saved = localStorage.getItem('theme') as ThemeName;
    return saved || 'light';
  });

  useEffect(() => {
    localStorage.setItem('theme', themeName);
    
    // Apply dark class to html element for shadcn dark mode
    const root = document.documentElement;
    if (themeName === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    
    // For now, all light themes use the same shadcn light mode
    // In the future, we can add custom CSS variable overrides for different themes
  }, [themeName]);

  const setTheme = (newThemeName: ThemeName) => {
    setThemeName(newThemeName);
  };

  const availableThemes: ThemeName[] = ['light', 'dark', 'linear', 'vercel', 'minimalist'];

  return (
    <ThemeContext.Provider value={{ themeName, setTheme, availableThemes }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}
