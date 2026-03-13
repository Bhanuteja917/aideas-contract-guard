import { useState, useRef } from 'react'
import { validateFile, formatFileSize } from '../utils/fileValidation'
import { Button } from './ui/button'
import { cn } from '@/lib/utils'

interface UploadContractProps {
  onFileSelect: (file: File) => void
  onValidationError: (error: string) => void
}

export default function UploadContract({ onFileSelect, onValidationError }: UploadContractProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const files = e.dataTransfer.files
    if (files && files.length > 0) {
      const file = files[0]
      handleFileSelection(file)
    }
  }

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      const file = files[0]
      handleFileSelection(file)
    }
  }

  const handleFileSelection = (file: File) => {
    // Validate file
    const validation = validateFile(file)
    
    if (!validation.valid) {
      onValidationError(validation.error || 'Invalid file')
      setSelectedFile(null)
      return
    }

    setSelectedFile(file)
    onFileSelect(file)
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  const handleRemove = (e: React.MouseEvent) => {
    e.stopPropagation()
    setSelectedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="w-full">
      <div
        className={cn(
          "relative rounded-lg border-2 border-dashed p-8 text-center cursor-pointer transition-colors",
          isDragging ? "border-[var(--primary)] bg-[var(--accent)]" : "border-[var(--border)] bg-[var(--background)] hover:bg-[var(--secondary)]"
        )}
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,application/pdf"
          onChange={handleFileInputChange}
          className="hidden"
        />

        <div className="space-y-4">
          <div className="flex justify-center">
            <svg
              className={cn(
                "w-16 h-16 transition-colors",
                isDragging ? "text-[var(--primary)]" : "text-[var(--muted-foreground)]"
              )}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
          </div>

          <div>
            <p className="text-lg font-medium">
              {isDragging ? 'Drop your contract here' : 'Upload a contract'}
            </p>
            <p className="mt-1 text-sm text-[var(--muted-foreground)]">
              Drag and drop your PDF file here, or click to browse
            </p>
            <p className="mt-1 text-xs text-[var(--muted-foreground)]">
              PDF files only, max 10MB
            </p>
          </div>

          {selectedFile && (
            <div className="mt-4 p-4 rounded-md bg-[var(--secondary)] border border-[var(--border)]">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <svg
                    className="w-8 h-8 text-[var(--destructive)]"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <div className="text-left">
                    <p className="text-sm font-medium">
                      {selectedFile.name}
                    </p>
                    <p className="text-xs text-[var(--muted-foreground)]">
                      {formatFileSize(selectedFile.size)}
                    </p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon-sm"
                  onClick={handleRemove}
                  className="hover:bg-[var(--muted)]"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                      clipRule="evenodd"
                    />
                  </svg>
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
