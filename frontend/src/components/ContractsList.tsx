import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { Layout } from './Layout';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Skeleton } from './ui/skeleton';
import { Alert, AlertDescription } from './ui/alert';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from './ui/table';

interface Contract {
  contractId: string;
  fileName: string;
  fileSize: number;
  uploadedAt: string;
  status: string;
}

export function ContractsList() {
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadContracts();
  }, []);

  const loadContracts = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/contracts');
      setContracts(response.data.contracts || []);
    } catch (err: any) {
      console.error('Error loading contracts:', err);
      setError(err.message || 'Failed to load contracts');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const getStatusBadge = (status: string) => {
    const statusConfig: Record<string, { label: string; variant: "default" | "secondary" | "destructive" | "outline" }> = {
      pending_upload: { label: 'Pending Upload', variant: 'outline' },
      upload_completed: { label: 'Uploaded', variant: 'secondary' },
      analyzing: { label: 'Analyzing', variant: 'default' },
      completed: { label: 'Completed', variant: 'secondary' },
      failed: { label: 'Failed', variant: 'destructive' }
    };

    const config = statusConfig[status] || { label: status, variant: 'outline' as const };

    return (
      <Badge variant={config.variant}>
        {config.label}
      </Badge>
    );
  };

  const handleViewContract = (contractId: string, status: string) => {
    if (status === 'completed') {
      navigate(`/dashboard/${contractId}`);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center space-y-4">
            <Skeleton className="h-12 w-12 rounded-full mx-auto" />
            <p className="text-[var(--muted-foreground)]">Loading contracts...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="py-2">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-8 flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold">My Contracts</h1>
              <p className="mt-2 text-[var(--muted-foreground)]">
                View and manage your uploaded contracts
              </p>
            </div>
            
            <div className="flex gap-3">
              <Button variant="outline" onClick={loadContracts} className="border-[var(--border)]">
                <svg
                  className="h-4 w-4 mr-2"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
                Refresh
              </Button>
              
              <Button onClick={() => navigate('/upload')} className="bg-[var(--primary)] text-[var(--primary-foreground)] hover:bg-[var(--primary)]/90">
                <svg
                  className="h-4 w-4 mr-2"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 4v16m8-8H4"
                  />
                </svg>
                Upload Contract
              </Button>
            </div>
          </div>

          {error && (
            <Alert variant="destructive" className="mb-6 border-[var(--destructive)]">
              <AlertDescription>
                {error}
                <button
                  onClick={loadContracts}
                  className="ml-2 underline hover:no-underline"
                >
                  Try again
                </button>
              </AlertDescription>
            </Alert>
          )}

          {contracts.length === 0 ? (
            <Card className="border border-[var(--border)]">
              <CardContent className="text-center py-12">
                <svg
                  className="mx-auto h-12 w-12 text-[var(--muted-foreground)]"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                <h3 className="mt-2 text-sm font-medium">No contracts</h3>
                <p className="mt-1 text-sm text-[var(--muted-foreground)]">Get started by uploading a contract.</p>
                <div className="mt-6">
                  <Button onClick={() => navigate('/upload')} className="bg-[var(--primary)] text-[var(--primary-foreground)] hover:bg-[var(--primary)]/90">
                    Upload Contract
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card className="border border-[var(--border)] rounded-md overflow-hidden p-0">
              <Table>
                <TableHeader>
                  <TableRow className="border-b border-[var(--border)] hover:bg-transparent">
                    <TableHead className="px-6 py-3 font-semibold">File Name</TableHead>
                    <TableHead className="px-6 py-3 font-semibold">Size</TableHead>
                    <TableHead className="px-6 py-3 font-semibold">Uploaded</TableHead>
                    <TableHead className="px-6 py-3 font-semibold">Status</TableHead>
                    <TableHead className="px-6 py-3 text-right font-semibold">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {contracts.map((contract) => (
                    <TableRow key={contract.contractId} className="border-b border-[var(--border)]">
                      <TableCell className="px-6 py-4">
                        <div className="flex items-center">
                          <svg
                            className="h-5 w-5 mr-2 text-[var(--destructive)]"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path
                              fillRule="evenodd"
                              d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"
                              clipRule="evenodd"
                            />
                          </svg>
                          <span className="text-sm font-medium">
                            {contract.fileName}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell className="px-6 py-4 text-[var(--muted-foreground)]">
                        {formatFileSize(contract.fileSize)}
                      </TableCell>
                      <TableCell className="px-6 py-4 text-[var(--muted-foreground)]">
                        {formatDate(contract.uploadedAt)}
                      </TableCell>
                      <TableCell className="px-6 py-4">
                        {getStatusBadge(contract.status)}
                      </TableCell>
                      <TableCell className="px-6 py-4 text-right">
                        {contract.status === 'completed' ? (
                          <button
                            onClick={() => handleViewContract(contract.contractId, contract.status)}
                            className="text-[var(--primary)] hover:underline"
                          >
                            View Analysis →
                          </button>
                        ) : contract.status === 'analyzing' ? (
                          <span className="text-[var(--muted-foreground)]">Processing...</span>
                        ) : contract.status === 'failed' ? (
                          <span className="text-[var(--destructive)]">Failed</span>
                        ) : (
                          <span className="text-[var(--muted-foreground)]">Pending</span>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Card>
          )}
        </div>
      </div>
    </Layout>
  );
}
