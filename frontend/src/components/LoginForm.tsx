'use client'

import { useState } from 'react'
import { EyeIcon, EyeOffIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'

const LoginForm = () => {
  const [isVisible, setIsVisible] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { signIn } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await signIn(email, password)
      navigate('/dashboard')
    } catch (err: any) {
      setError(err.message || 'Failed to sign in')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form className='space-y-4' onSubmit={handleSubmit}>
      {error && (
        <div className='rounded-lg bg-[var(--destructive)]/10 p-3 text-sm text-[var(--destructive)]'>
          {error}
        </div>
      )}

      {/* Email */}
      <div className='space-y-1'>
        <Label htmlFor='userEmail' className='leading-5'>
          Email address*
        </Label>
        <Input
          type='email'
          id='userEmail'
          placeholder='Enter your email address'
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className='border-[var(--border)]'
        />
      </div>

      {/* Password */}
      <div className='w-full space-y-1'>
        <Label htmlFor='password' className='leading-5'>
          Password*
        </Label>
        <div className='relative'>
          <Input
            id='password'
            type={isVisible ? 'text' : 'password'}
            placeholder='••••••••••••••••'
            className='pr-9 border-[var(--border)]'
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <Button
            type='button'
            variant='ghost'
            size='icon-sm'
            onClick={() => setIsVisible(prevState => !prevState)}
            className='text-[var(--muted-foreground)] focus-visible:ring-ring/50 absolute inset-y-0 right-0 rounded-l-none hover:bg-transparent'
          >
            {isVisible ? <EyeOffIcon className='size-4' /> : <EyeIcon className='size-4' />}
            <span className='sr-only'>{isVisible ? 'Hide password' : 'Show password'}</span>
          </Button>
        </div>
      </div>

      {/* Remember Me and Forgot Password */}
      <div className='flex items-center justify-between gap-y-2'>
        <div className='flex items-center gap-3'>
          <Checkbox id='rememberMe' className='size-4 border-[var(--border)]' />
          <Label htmlFor='rememberMe' className='text-sm text-[var(--muted-foreground)] cursor-pointer'>
            Remember Me
          </Label>
        </div>
        <a href='/forgot-password' className='text-sm hover:underline text-[var(--primary)]'>
          Forgot Password?
        </a>
      </div>

      <Button className='w-full bg-[var(--primary)] text-[var(--primary-foreground)] hover:bg-[var(--primary)]/90' type='submit' disabled={loading}>
        {loading ? 'Signing in...' : 'Sign in to ContractGuard'}
      </Button>
    </form>
  )
}

export default LoginForm
