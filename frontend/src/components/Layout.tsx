import { ReactNode, useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useTheme } from '../contexts/ThemeContext'
import { Button } from './ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from './ui/dropdown-menu'

interface LayoutProps {
  children: ReactNode
}

export function Layout({ children }: LayoutProps) {
  const { user, signOut } = useAuth()
  const { themeName, setTheme, availableThemes } = useTheme()
  const [userEmail, setUserEmail] = useState<string>('')

  useEffect(() => {
    // Get user email from Cognito attributes
    if (user) {
      user.getUserAttributes((err, attributes) => {
        if (!err && attributes) {
          const emailAttr = attributes.find(attr => attr.getName() === 'email')
          if (emailAttr) {
            setUserEmail(emailAttr.getValue())
          }
        }
      })
    }
  }, [user])

  return (
    <div className="min-h-screen bg-[var(--background)] text-[var(--foreground)]">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b border-[var(--border)] bg-[var(--background)]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <Link to="/contracts" className="flex items-center space-x-2 group">
                <div className="w-8 h-8 rounded bg-[var(--primary)] flex items-center justify-center">
                  <span className="text-[var(--primary-foreground)] font-bold text-sm">CG</span>
                </div>
                <h1 className="text-xl font-semibold group-hover:opacity-80 transition-opacity">
                  ContractGuard
                </h1>
              </Link>
            </div>
            <div className="flex items-center space-x-3">
              {/* Theme Switcher */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm" className="border-[var(--border)] rounded-md">
                    <span className="flex items-center space-x-1">
                      <span>🎨</span>
                      <span className="hidden sm:inline">{themeName.charAt(0).toUpperCase() + themeName.slice(1)}</span>
                    </span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  {availableThemes.map((theme) => (
                    <DropdownMenuItem
                      key={theme}
                      onClick={() => setTheme(theme)}
                    >
                      {themeName === theme && '✓ '}
                      {theme.charAt(0).toUpperCase() + theme.slice(1)}
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>
              
              <span className="text-sm text-[var(--muted-foreground)] hidden sm:inline">
                {userEmail || 'Loading...'}
              </span>
              <Button
                onClick={signOut}
                variant="ghost"
                size="sm"
                className="text-[var(--foreground)] hover:bg-[var(--muted)] rounded-md"
              >
                Sign out
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="py-6">{children}</main>
    </div>
  )
}
