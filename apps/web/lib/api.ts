// API client utilities for backend communication

import { InterviewPackResponse } from '@/types/interview';
import { 
  Application, 
  ApplicationStatus, 
  PrefillIntentResponse,
  PrefillLog 
} from '@/types/application';
import { CVDocument, CVListResponse } from '@/types/profile';

const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface SaveProfileResponse {
  profile_id: string;
  message: string;
}

export async function saveProfile(profile: any): Promise<SaveProfileResponse> {
  const response = await fetch(`${apiUrl}/profile/save`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(profile),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Failed to save profile');
  }

  return response.json();
}

export async function savePreferences(email: string, preferences: any): Promise<SaveProfileResponse> {
  const response = await fetch(`${apiUrl}/profile/preferences/save?email=${encodeURIComponent(email)}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(preferences),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Failed to save preferences');
  }

  return response.json();
}

// CV Document API methods
export async function listCVs(userEmail: string): Promise<CVListResponse> {
  const response = await fetch(`${apiUrl}/cvs?user_email=${encodeURIComponent(userEmail)}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Failed to fetch CVs');
  }

  return response.json();
}

export async function setActiveCV(cvId: string, userEmail: string): Promise<any> {
  const response = await fetch(`${apiUrl}/cvs/set-active`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      cv_id: cvId,
      user_email: userEmail,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Failed to set active CV');
  }

  return response.json();
}

export async function deleteCV(cvId: string, userEmail: string): Promise<any> {
  const response = await fetch(`${apiUrl}/cvs/${cvId}?user_email=${encodeURIComponent(userEmail)}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Failed to delete CV');
  }

  return response.json();
}

// Interview API methods
export async function generateInterviewMaterials(packetId: string): Promise<InterviewPackResponse> {
  const response = await fetch(`${apiUrl}/interview/generate?packet_id=${packetId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to generate interview materials');
  }

  return response.json();
}

export async function getInterviewMaterials(packetId: string): Promise<InterviewPackResponse> {
  const response = await fetch(`${apiUrl}/interview/${packetId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch interview materials');
  }

  return response.json();
}

// Application API methods
export async function createApplication(packetId: string, jobId: string, notes?: string): Promise<Application> {
  const response = await fetch(`${apiUrl}/applications/create`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      packet_id: packetId,
      job_id: jobId,
      notes: notes || '',
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create application');
  }

  return response.json();
}

export async function getApplications(status?: ApplicationStatus): Promise<Application[]> {
  const url = status 
    ? `${apiUrl}/applications?status=${status}`
    : `${apiUrl}/applications`;

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch applications');
  }

  return response.json();
}

export async function getApplication(applicationId: string): Promise<Application> {
  const response = await fetch(`${apiUrl}/applications/${applicationId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch application');
  }

  return response.json();
}

export async function updateApplicationStatus(
  applicationId: string, 
  status: ApplicationStatus, 
  note?: string
): Promise<Application> {
  const response = await fetch(`${apiUrl}/applications/${applicationId}/status`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      status,
      note: note || '',
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update application status');
  }

  return response.json();
}

// Prefill API methods
export async function createPrefillIntent(applicationId: string): Promise<PrefillIntentResponse> {
  const response = await fetch(`${apiUrl}/prefill/create-intent`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      application_id: applicationId,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create prefill intent');
  }

  return response.json();
}

export async function getPrefillLog(logId: string): Promise<PrefillLog> {
  const response = await fetch(`${apiUrl}/prefill/logs/${logId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch prefill log');
  }

  return response.json();
}
