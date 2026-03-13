import { useParams } from 'react-router-dom';
import { useState } from 'react';
import { useAnalysis } from '../hooks/useAnalysis';
import { api } from '../services/api';
import { Layout } from './Layout';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Skeleton } from './ui/skeleton';
import { Alert, AlertDescription } from './ui/alert';

export function Dashboard() {
  const { contractId } = useParams<{ contractId: string }>();
  const { contract, analysis, loading, error } = useAnalysis(contractId);
  const [downloadingReport, setDownloadingReport] = useState(false);
  const [reportError, setReportError] = useState<string | null>(null);

  const handleDownloadReport = async () => {
    if (!contractId) return;

    setDownloadingReport(true);
    setReportError(null);

    try {
      const response = await api.get(`/contracts/${contractId}/report`);
      const { downloadUrl } = response.data;

      // Trigger download
      window.open(downloadUrl, '_blank');
    } catch (err: any) {
      console.error('Error downloading report:', err);
      setReportError(err.message || 'Failed to download report');
    } finally {
      setDownloadingReport(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center space-y-4">
            <Skeleton className="h-12 w-12 rounded-full mx-auto" />
            <p className="font-medium">Loading analysis...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center p-4">
          <Card className="max-w-md border border-[var(--border)]">
            <CardHeader>
              <CardTitle className="text-[var(--destructive)]">Error</CardTitle>
            </CardHeader>
            <CardContent>
              <p>{error}</p>
            </CardContent>
          </Card>
        </div>
      </Layout>
    );
  }

  if (!contract) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center p-4">
          <Card className="max-w-md border border-[var(--border)]">
            <CardHeader>
              <CardTitle>Contract Not Found</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-[var(--muted-foreground)]">
                The requested contract could not be found.
              </p>
            </CardContent>
          </Card>
        </div>
      </Layout>
    );
  }

  // Show analyzing state
  if (contract.status === 'analyzing' || contract.status === 'upload_completed') {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center p-4">
          <Card className="max-w-md text-center border border-[var(--border)]">
            <CardContent className="pt-6 space-y-4">
              <Skeleton className="h-16 w-16 rounded-full mx-auto" />
              <CardTitle>Analyzing Contract</CardTitle>
              <p className="text-[var(--muted-foreground)]">
                Your contract is being analyzed. This may take a few moments...
              </p>
              <Badge variant="secondary">Status: {contract.status}</Badge>
            </CardContent>
          </Card>
        </div>
      </Layout>
    );
  }

  if (contract.status === 'failed') {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center p-4">
          <Card className="max-w-md border border-[var(--border)]">
            <CardHeader>
              <CardTitle className="text-[var(--destructive)]">Analysis Failed</CardTitle>
            </CardHeader>
            <CardContent>
              <p>
                There was an error analyzing your contract. Please try uploading again.
              </p>
            </CardContent>
          </Card>
        </div>
      </Layout>
    );
  }

  if (!analysis) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center p-4">
          <Card className="max-w-md border border-[var(--border)]">
            <CardHeader>
              <CardTitle>No Analysis Available</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-[var(--muted-foreground)]">
                Analysis results are not yet available for this contract.
              </p>
            </CardContent>
          </Card>
        </div>
      </Layout>
    );
  }

  // Helper function to get risk color
  const getRiskVariant = (score: number): "default" | "secondary" | "destructive" => {
    if (score <= 3) return "secondary";
    if (score <= 6) return "default";
    return "destructive";
  };

  const getRiskLabel = (score: number) => {
    if (score <= 3) return 'Low Risk';
    if (score <= 6) return 'Medium Risk';
    return 'High Risk';
  };

  return (
    <Layout>
      <div className="py-2">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="space-y-6">
          {/* Header */}
          <Card className="border border-[var(--border)]">
            <CardHeader>
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div className="space-y-1.5">
                  <CardTitle className="text-2xl">Contract Analysis</CardTitle>
                  <p className="text-base font-medium">{contract.fileName}</p>
                  <p className="text-sm text-[var(--muted-foreground)]">
                    Analyzed: {new Date(analysis.analyzedAt).toLocaleString()}
                  </p>
                </div>
                <div className="flex flex-col gap-2">
                  <Button
                    onClick={handleDownloadReport}
                    disabled={downloadingReport}
                    className="bg-[var(--primary)] text-[var(--primary-foreground)] hover:bg-[var(--primary)]/90"
                  >
                    {downloadingReport ? (
                      <>
                        <svg className="mr-2 h-4 w-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Generating...
                      </>
                    ) : (
                      <>
                        <svg className="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        Download Report
                      </>
                    )}
                  </Button>
                  {reportError && (
                    <p className="text-sm text-[var(--destructive)]">{reportError}</p>
                  )}
                </div>
              </div>
            </CardHeader>
          </Card>

          {/* Overall Risk Score */}
          <Card className="border border-[var(--border)]">
            <CardHeader>
              <CardTitle>Overall Risk Score</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center justify-center gap-6 sm:flex-row sm:gap-8">
                <div className="flex h-32 w-32 items-center justify-center rounded-full border-4 text-6xl font-bold border-[var(--border)]">
                  {analysis.overallRiskScore.toFixed(1)}
                </div>
                <div className="flex flex-col items-center gap-2 sm:items-start">
                  <Badge variant={getRiskVariant(analysis.overallRiskScore)} className="px-4 py-2 text-lg">
                    {getRiskLabel(analysis.overallRiskScore)}
                  </Badge>
                  <p className="text-sm text-[var(--muted-foreground)]">Out of 10</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Risk Categories */}
          <Card className="border border-[var(--border)]">
            <CardHeader>
              <CardTitle>Risk by Category</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                {Object.entries(analysis.riskCategories).map(([category, score]) => (
                  <div key={category} className="space-y-2 rounded-lg border border-[var(--border)] p-4">
                    <h3 className="text-sm font-medium capitalize text-[var(--muted-foreground)]">
                      {category.replace('_', ' ')}
                    </h3>
                    <div className="text-3xl font-bold">
                      {score.toFixed(1)}
                    </div>
                    <div className="h-2 w-full rounded-full bg-[var(--secondary)]">
                      <div
                        className="h-2 rounded-full bg-[var(--primary)]"
                        style={{ width: `${(score / 10) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Clauses */}
          {analysis.clauses && analysis.clauses.length > 0 && (
            <Card className="border border-[var(--border)]">
              <CardHeader>
                <CardTitle>Identified Risks</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analysis.clauses.map((clause, index) => (
                    <div key={index} className="space-y-3 border-l-4 border-[var(--muted)] py-2 pl-4">
                      <div className="flex items-center gap-2">
                        <Badge variant={getRiskVariant(clause.risk_score)}>
                          Risk: {clause.risk_score}/10
                        </Badge>
                        <span className="text-sm capitalize text-[var(--muted-foreground)]">
                          {clause.category.replace('_', ' ')}
                        </span>
                      </div>
                      <p className="text-sm italic">
                        "{clause.text.substring(0, 200)}..."
                      </p>
                      <Alert variant="destructive" className="border-[var(--destructive)]">
                        <AlertDescription>
                          ⚠️ {clause.concern}
                        </AlertDescription>
                      </Alert>
                      
                      {clause.explanation_english && (
                        <div className="space-y-1 rounded-lg bg-[var(--muted)] p-3">
                          <p className="text-sm font-medium">Explanation:</p>
                          <p className="text-sm">{clause.explanation_english}</p>
                        </div>
                      )}
                      
                      {clause.explanation_hindi && (
                        <div className="space-y-1 rounded-lg bg-[var(--muted)] p-3">
                          <p className="text-sm font-medium">व्याख्या:</p>
                          <p className="text-sm">{clause.explanation_hindi}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Compliance Issues */}
          {analysis.complianceIssues && analysis.complianceIssues.length > 0 && (
            <Card className="border border-[var(--border)]">
              <CardHeader>
                <CardTitle>Compliance Issues</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analysis.complianceIssues.map((issue, index) => (
                    <div key={index} className="space-y-2 border-l-4 border-[var(--destructive)] py-2 pl-4">
                      <div className="flex items-center gap-2">
                        <Badge variant={issue.severity === 'high' ? 'destructive' : 'default'}>
                          {issue.severity.toUpperCase()}
                        </Badge>
                        {issue.section && (
                          <span className="text-sm text-[var(--muted-foreground)]">{issue.section}</span>
                        )}
                      </div>
                      <p className="text-sm italic">
                        "{issue.clause.substring(0, 150)}..."
                      </p>
                      <p className="font-medium text-[var(--destructive)]">{issue.issue}</p>
                      <p className="text-sm">
                        <span className="font-medium">Recommendation:</span> {issue.recommendation}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Recommendations */}
          {analysis.recommendations && analysis.recommendations.length > 0 && (
            <Card className="border border-[var(--border)]">
              <CardHeader>
                <CardTitle>Negotiation Recommendations</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analysis.recommendations.map((rec, index) => (
                    <div key={index} className="space-y-3 rounded-lg bg-[var(--muted)] p-4">
                      <div className="flex items-center gap-2">
                        <Badge variant="destructive">
                          High Risk: {rec.risk_score}/10
                        </Badge>
                        <span className="text-sm capitalize text-[var(--muted-foreground)]">
                          {rec.category.replace('_', ' ')}
                        </span>
                      </div>
                      <p className="text-sm italic">
                        "{rec.clause.substring(0, 150)}..."
                      </p>
                      
                      <div className="space-y-3">
                        <div className="space-y-1">
                          <p className="text-sm font-semibold">💡 Recommendation:</p>
                          <p className="text-sm">{rec.recommendation}</p>
                        </div>
                        
                        {rec.alternative_language && (
                          <div className="space-y-1">
                            <p className="text-sm font-semibold">✏️ Suggested Language:</p>
                            <p className="text-sm italic">"{rec.alternative_language}"</p>
                          </div>
                        )}
                        
                        {rec.fallback && (
                          <div className="space-y-1">
                            <p className="text-sm font-semibold">🔄 Fallback Position:</p>
                            <p className="text-sm">{rec.fallback}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Entities Summary */}
          {analysis.entities && analysis.entities.length > 0 && (
            <Card className="border border-[var(--border)]">
              <CardHeader>
                <CardTitle>Key Entities Detected</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {analysis.entities.slice(0, 20).map((entity, index) => (
                    <Badge key={index} variant="secondary" className="bg-[var(--secondary)] text-[var(--secondary-foreground)]">
                      {entity.text} <span className="text-[var(--muted-foreground)]">({entity.type})</span>
                    </Badge>
                  ))}
                  {analysis.entities.length > 20 && (
                    <Badge variant="outline" className="border-[var(--border)]">
                      +{analysis.entities.length - 20} more
                    </Badge>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
      </div>
    </Layout>
  );
}
