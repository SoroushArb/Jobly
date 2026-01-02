/**
 * API client for communicating with Jobly backend
 */
import axios, { AxiosInstance } from 'axios';

export interface PrefillIntent {
  _id?: string;
  packet_id: string;
  job_url: string;
  user_fields: Record<string, any>;
  attachments: Record<string, string>;
  common_answers: Record<string, any>;
  auth_token?: string;
  token_expires_at?: string;
  status: string;
}

export interface PrefillLog {
  intent_id: string;
  detected_ats?: string;
  detection_confidence: number;
  filled_fields: Array<{
    field_name: string;
    value: string;
    success: boolean;
    error?: string;
  }>;
  missing_fields: string[];
  errors: Array<{ field: string; error_message: string }>;
  resume_attached: boolean;
  attachment_errors: string[];
  screenshot_paths: string[];
  timestamp: string;
  duration_seconds: number;
  stopped_before_submit: boolean;
  field_mappings: Record<string, any>;
}

export class ApiClient {
  private client: AxiosInstance;
  private apiUrl: string;

  constructor(apiUrl: string) {
    this.apiUrl = apiUrl;
    this.client = axios.create({
      baseURL: apiUrl,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Fetch a prefill intent by ID with auth token
   */
  async fetchIntent(intentId: string, authToken: string): Promise<PrefillIntent> {
    const response = await this.client.get<PrefillIntent>(`/prefill/intent/${intentId}`, {
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    });
    return response.data;
  }

  /**
   * Report prefill result back to API
   */
  async reportResult(intentId: string, authToken: string, log: PrefillLog): Promise<void> {
    await this.client.post('/prefill/report-result', {
      intent_id: intentId,
      auth_token: authToken,
      log,
    });
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.client.get('/health');
      return response.data.status === 'healthy';
    } catch {
      return false;
    }
  }
}
