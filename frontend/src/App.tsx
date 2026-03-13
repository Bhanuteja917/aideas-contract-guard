import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'
import SignIn from './components/SignIn'
import SignUp from './components/SignUp'
import ForgotPassword from './components/ForgotPassword'
import ProtectedRoute from './components/ProtectedRoute'
import UploadContract from './components/UploadContract'
import { Dashboard } from './components/Dashboard'
import { ContractsList } from './components/ContractsList'
import { Layout } from './components/Layout'
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card'
import { Alert, AlertDescription } from './components/ui/alert'
import { useState } from 'react'
import { getUploadUrl, uploadToS3 } from './services/api'

function Home() {
  const { session } = useAuth()
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const handleFileSelect = async (file: File) => {
    if (!session) {
      setError('Not authenticated')
      return
    }

    setError('')
    setSuccess('')
    setUploading(true)
    setUploadProgress(0)

    try {
      // Get pre-signed upload URL
      const { uploadUrl, contractId } = await getUploadUrl(file.name, file.size, session)

      // Upload to S3 with progress tracking
      await uploadToS3(file, uploadUrl, (progress) => {
        setUploadProgress(progress)
      })

      setSuccess(`Contract uploaded successfully! Redirecting to analysis...`)
      setUploadProgress(100)
      
      // Redirect to dashboard after 2 seconds
      setTimeout(() => {
        window.location.href = `/dashboard/${contractId}`
      }, 2000)
    } catch (err: any) {
      setError(err.message || 'Upload failed. Please try again.')
    } finally {
      setTimeout(() => {
        setUploading(false)
        setUploadProgress(0)
      }, 2000)
    }
  }

  const handleValidationError = (errorMessage: string) => {
    setError(errorMessage)
    setTimeout(() => setError(''), 5000)
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0 space-y-6">
          <div>
            <h2 className="text-3xl font-bold">Upload Contract</h2>
            <p className="mt-2 text-muted-foreground">
              Upload your contract PDF for AI-powered risk analysis
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Success Message */}
          {success && (
            <Alert>
              <AlertDescription>{success}</AlertDescription>
            </Alert>
          )}

          {/* Upload Component */}
          <UploadContract
            onFileSelect={handleFileSelect}
            onValidationError={handleValidationError}
          />

          {/* Upload Progress */}
          {uploading && (
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Uploading...</span>
                  <span className="text-sm font-medium">{uploadProgress}%</span>
                </div>
                <div className="w-full bg-secondary rounded-full h-2">
                  <div
                    className="h-2 bg-primary rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Info Section */}
          <Card>
            <CardHeader>
              <CardTitle>How it works</CardTitle>
            </CardHeader>
            <CardContent>
              <ol className="list-decimal list-inside space-y-2 text-muted-foreground">
                <li>Upload your contract PDF (max 10MB)</li>
                <li>Our AI analyzes the contract for risks and compliance issues</li>
                <li>Get a detailed risk report with plain-language explanations</li>
                <li>Download a PDF report with negotiation recommendations</li>
              </ol>
            </CardContent>
          </Card>
        </div>
      </div>
    </Layout>
  )
}

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/" element={<Navigate to="/contracts" replace />} />
            <Route path="/dashboard" element={<Navigate to="/contracts" replace />} />
            <Route path="/signin" element={<SignIn />} />
            <Route path="/signup" element={<SignUp />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route
              path="/contracts"
              element={
                <ProtectedRoute>
                  <ContractsList />
                </ProtectedRoute>
              }
            />
            <Route
              path="/upload"
              element={
                <ProtectedRoute>
                  <Home />
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/:contractId"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
