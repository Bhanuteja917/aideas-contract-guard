import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate, Link } from 'react-router-dom'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { Card, CardContent } from './ui/card'
import { Alert } from './ui/alert'

export default function SignUp() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [needsConfirmation, setNeedsConfirmation] = useState(false)
  const [confirmationCode, setConfirmationCode] = useState('')
  const { signUp, confirmSignUp } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }

    setLoading(true)

    try {
      await signUp(email, password)
      setNeedsConfirmation(true)
    } catch (err: any) {
      setError(err.message || 'Failed to sign up')
    } finally {
      setLoading(false)
    }
  }

  const handleConfirmation = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await confirmSignUp(email, confirmationCode)
      navigate('/signin')
    } catch (err: any) {
      setError(err.message || 'Failed to confirm account')
    } finally {
      setLoading(false)
    }
  }

  if (needsConfirmation) {
    return (
      <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-6">
          <div className="text-center">
            <h2 className="text-4xl font-bold mb-2">Confirm your email</h2>
            <p className="text-lg text-[var(--muted-foreground)]">
              We sent a confirmation code to {email}
            </p>
          </div>

          <Card className="border-[var(--border)]">
            <CardContent className="pt-6">
              <form className="space-y-4" onSubmit={handleConfirmation}>
                {error && (
                  <Alert variant="destructive" className="border-[var(--destructive)]">
                    <p className="text-sm font-medium">{error}</p>
                  </Alert>
                )}

                <div className="space-y-2">
                  <Label htmlFor="code">Confirmation code</Label>
                  <Input
                    id="code"
                    name="code"
                    type="text"
                    required
                    value={confirmationCode}
                    onChange={(e) => setConfirmationCode(e.target.value)}
                    placeholder="Enter confirmation code"
                    className="border-[var(--border)]"
                  />
                </div>

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-[var(--primary)] text-[var(--primary-foreground)] hover:bg-[var(--primary)]/90"
                >
                  {loading ? 'Confirming...' : 'Confirm'}
                </Button>

                <div className="flex items-center justify-between text-sm">
                  <button
                    type="button"
                    onClick={() => setNeedsConfirmation(false)}
                    className="text-[var(--primary)] hover:underline font-medium"
                  >
                    Back to sign up
                  </button>
                  <Link
                    to="/signin"
                    className="text-[var(--primary)] hover:underline font-medium"
                  >
                    Back to sign in
                  </Link>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-6">
        <div className="text-center">
          <h2 className="text-4xl font-bold mb-2">Create your account</h2>
          <p className="text-lg text-[var(--muted-foreground)]">
            Start analyzing contracts with AI
          </p>
        </div>

        <Card className="border-[var(--border)]">
          <CardContent className="pt-6">
            <form className="space-y-4" onSubmit={handleSubmit}>
              {error && (
                <Alert variant="destructive" className="border-[var(--destructive)]">
                  <p className="text-sm font-medium">{error}</p>
                </Alert>
              )}

              <div className="space-y-2">
                <Label htmlFor="email">Email address</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com"
                  className="border-[var(--border)]"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="new-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Min 8 characters"
                  className="border-[var(--border)]"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirm-password">Confirm password</Label>
                <Input
                  id="confirm-password"
                  name="confirm-password"
                  type="password"
                  autoComplete="new-password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirm password"
                  className="border-[var(--border)]"
                />
              </div>

              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-[var(--primary)] text-[var(--primary-foreground)] hover:bg-[var(--primary)]/90"
              >
                {loading ? 'Creating account...' : 'Sign up'}
              </Button>

              <div className="flex items-center justify-between text-sm">
                <Link
                  to="/forgot-password"
                  className="text-[var(--primary)] hover:underline font-medium"
                >
                  Forgot password?
                </Link>
                <Link
                  to="/signin"
                  className="text-[var(--primary)] hover:underline font-medium"
                >
                  Already have an account? Sign in
                </Link>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
