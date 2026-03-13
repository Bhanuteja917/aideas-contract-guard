import { CognitoUserSession } from 'amazon-cognito-identity-js'

const API_URL = import.meta.env.VITE_API_URL

export interface UploadResponse {
  uploadUrl: string
  contractId: string
}

export async function getUploadUrl(
  fileName: string,
  fileSize: number,
  session: CognitoUserSession
): Promise<UploadResponse> {
  const idToken = session.getIdToken().getJwtToken()

  const response = await fetch(`${API_URL}/contracts/upload`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${idToken}`,
    },
    body: JSON.stringify({
      fileName,
      fileSize,
      contentType: 'application/pdf',
    }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Upload failed' }))
    throw new Error(error.message || 'Failed to get upload URL')
  }

  return response.json()
}

export async function uploadToS3(
  file: File,
  uploadUrl: string,
  onProgress?: (progress: number) => void
): Promise<void> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()

    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable && onProgress) {
        const progress = Math.round((e.loaded / e.total) * 100)
        onProgress(progress)
      }
    })

    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve()
      } else {
        reject(new Error(`Upload failed with status ${xhr.status}`))
      }
    })

    xhr.addEventListener('error', () => {
      reject(new Error('Network error during upload'))
    })

    xhr.addEventListener('abort', () => {
      reject(new Error('Upload aborted'))
    })

    xhr.open('PUT', uploadUrl)
    xhr.setRequestHeader('Content-Type', 'application/pdf')
    xhr.send(file)
  })
}

// API client for making authenticated requests
export const api = {
  get: async (endpoint: string) => {
    // Get the current session from localStorage or context
    const idToken = localStorage.getItem('idToken')
    
    if (!idToken) {
      throw new Error('Not authenticated')
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${idToken}`,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Request failed' }))
      throw new Error(error.error || `Request failed with status ${response.status}`)
    }

    const data = await response.json()
    return { data }
  },

  post: async (endpoint: string, body: any) => {
    const idToken = localStorage.getItem('idToken')
    
    if (!idToken) {
      throw new Error('Not authenticated')
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${idToken}`,
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Request failed' }))
      throw new Error(error.error || `Request failed with status ${response.status}`)
    }

    const data = await response.json()
    return { data }
  },
}
