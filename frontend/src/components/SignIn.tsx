import { Link } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Separator } from './ui/separator'
import LoginForm from './LoginForm'
import AuthBackgroundShape from '../assets/svg/auth-background-shape'

export default function SignIn() {
  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background Shape */}
      <AuthBackgroundShape className="absolute -top-1/2 -right-1/4 w-[800px] h-auto opacity-50 pointer-events-none" />
      
      <div className="w-full max-w-md relative z-10">
        <Card className="border-[var(--border)]">
          <CardHeader className="text-center">
            <div className="mb-2 flex justify-center">
              <div className="inline-flex items-center justify-center rounded-lg bg-[var(--accent)] px-3 py-1.5">
                <span className="text-sm font-semibold text-[var(--accent-foreground)]">ContractGuard</span>
              </div>
            </div>
            <CardTitle className="text-2xl">Sign in to your account</CardTitle>
            <CardDescription>
              Enter your credentials to access your account
            </CardDescription>
          </CardHeader>
          <CardContent>
            <LoginForm />
            
            <Separator className="my-6 bg-[var(--border)]" />
            
            <p className="text-center text-sm text-[var(--muted-foreground)]">
              New on our platform?{' '}
              <Link to="/signup" className="font-medium text-[var(--foreground)] hover:underline">
                Create an account
              </Link>
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
