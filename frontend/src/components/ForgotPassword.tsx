import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate, Link } from 'react-router-dom'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { Card, CardContent } from './ui/card'
import { Alert } from './ui/alert'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)
  const [step, setStep] = useState<'email' | 'reset'>('email')
  const { forgotPassword, confirmPassword: confirmPasswordReset } = useAuth()
  const navigate = useNavigate()

  const handleRequestCode = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)

    try {
      await forgotPassword(email)
      setSuccess('Verification code sent to your email')
      setStep('reset')
    } catch (err: any) {
      setError(err.message || 'Failed to send verification code')
    } finally {
      setLoading(false)
    }
  }

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters long')
      return
    }

    setLoading(true)

    try {
      await confirmPasswordReset(email, code, newPassword)
      setSuccess('Password reset successful! Redirecting to sign in...')
      setTimeout(() => {
        navigate('/signin')
      }, 2000)
    } catch (err: any) {
      setError(err.message || 'Failed to reset password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-6">
        <div className="text-center">
          <h2 className="text-4xl font-bold mb-2">Reset your password</h2>
          <p className="text-lg text-muted-foreground">
            {step === 'email'
              ? 'Enter your email to receive a verification code'
              : 'Enter the code sent to your email and your new password'}
          </p>
        </div>

        {step === 'email' ? (
          <Card>
            <CardContent className="pt-6">
              <form className="space-y-4" onSubmit={handleRequestCode}>
                {error && (
                  <Alert variant="destructive">
                    <p className="text-sm font-medium">{error}</p>
                  </Alert>
                )}
                {success && (
                  <Alert>
                    <p className="text-sm font-medium">{success}</p>
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
                  />
                </div>

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full"
                >
                  {loading ? 'Sending...' : 'Send verification code'}
                </Button>

                <div className="flex justify-between text-sm">
                  <Link
                    to="/signin"
                    className="text-primary hover:underline font-medium"
                  >
                    Back to sign in
                  </Link>
                  <Link
                    to="/signup"
                    className="text-primary hover:underline font-medium"
                  >
                    Don't have an account? Sign up
                  </Link>
                </div>
              </form>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent className="pt-6">
              <form className="space-y-4" onSubmit={handleResetPassword}>
                {error && (
                  <Alert variant="destructive">
                    <p className="text-sm font-medium">{error}</p>
                  </Alert>
                )}
                {success && (
                  <Alert>
                    <p className="text-sm font-medium">{success}</p>
                  </Alert>
                )}

                <div className="space-y-2">
                  <Label htmlFor="code">Verification code</Label>
                  <Input
                    id="code"
                    name="code"
                    type="text"
                    required
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    placeholder="Enter code from email"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="newPassword">New password</Label>
                  <Input
                    id="newPassword"
                    name="newPassword"
                    type="password"
                    autoComplete="new-password"
                    required
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="Min 8 characters"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Confirm new password</Label>
                  <Input
                    id="confirmPassword"
                    name="confirmPassword"
                    type="password"
                    autoComplete="new-password"
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Confirm password"
                  />
                </div>

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full"
                >
                  {loading ? 'Resetting...' : 'Reset password'}
                </Button>

                <div className="text-center space-y-2 text-sm">
                  <button
                    type="button"
                    onClick={() => setStep('email')}
                    className="text-primary hover:underline block w-full font-medium"
                  >
                    Resend verification code
                  </button>
                  <Link
                    to="/signup"
                    className="text-primary hover:underline block font-medium"
                  >
                    Don't have an account? Sign up
                  </Link>
                  <Link
                    to="/signin"
                    className="text-primary hover:underline block font-medium"
                  >
                    Back to sign in
                  </Link>
                </div>
              </form>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
