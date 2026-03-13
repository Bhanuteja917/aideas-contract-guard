import { useState, useEffect } from 'react';
import { api } from '../services/api';

export interface Entity {
  text: string;
  type: string;
  score: number;
  beginOffset: number;
  endOffset: number;
}

export interface Clause {
  text: string;
  category: 'financial' | 'legal_liability' | 'intellectual_property' | 'termination';
  risk_score: number;
  concern: string;
  explanation_english?: string;
  explanation_hindi?: string;
}

export interface RiskCategories {
  financial: number;
  legal_liability: number;
  intellectual_property: number;
  termination: number;
}

export interface ComplianceIssue {
  clause: string;
  section?: string;
  severity: 'high' | 'medium' | 'low';
  issue: string;
  recommendation: string;
}

export interface Recommendation {
  clause: string;
  category: string;
  risk_score: number;
  recommendation: string;
  alternative_language: string;
  fallback: string;
}

export interface Analysis {
  analysisId: string;
  contractId: string;
  userId: string;
  analyzedAt: string;
  extractedText: string;
  entities: Entity[];
  clauses: Clause[];
  riskCategories: RiskCategories;
  overallRiskScore: number;
  complianceIssues: ComplianceIssue[];
  recommendations: Recommendation[];
  status: string;
}

export interface Contract {
  contractId: string;
  userId: string;
  fileName: string;
  fileSize: number;
  s3Bucket: string;
  s3Key: string;
  uploadedAt: string;
  status: 'pending_upload' | 'upload_completed' | 'analyzing' | 'completed' | 'failed';
}

interface UseAnalysisResult {
  contract: Contract | null;
  analysis: Analysis | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useAnalysis(contractId: string | undefined): UseAnalysisResult {
  const [contract, setContract] = useState<Contract | null>(null);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [pollInterval, setPollInterval] = useState<number | null>(null);

  const fetchAnalysis = async () => {
    if (!contractId) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await api.get(`/contracts/${contractId}`);
      const data = response.data;

      setContract(data.contract);
      setAnalysis(data.analysis);

      // If analysis is in progress, set up polling
      if (data.contract.status === 'analyzing' || data.contract.status === 'upload_completed') {
        setPollInterval(5000); // Poll every 5 seconds
      } else {
        setPollInterval(null); // Stop polling
      }

      setLoading(false);
    } catch (err: any) {
      console.error('Error fetching analysis:', err);
      setError(err.response?.data?.error || 'Failed to fetch analysis');
      setLoading(false);
      setPollInterval(null);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchAnalysis();
  }, [contractId]);

  // Polling for in-progress analyses
  useEffect(() => {
    if (pollInterval === null) return;

    const interval = setInterval(() => {
      fetchAnalysis();
    }, pollInterval);

    return () => clearInterval(interval);
  }, [pollInterval, contractId]);

  return {
    contract,
    analysis,
    loading,
    error,
    refetch: fetchAnalysis,
  };
}
