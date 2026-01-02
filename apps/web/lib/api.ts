// API client utilities for backend communication

import { InterviewPackResponse } from '@/types/interview';

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
    throw new Error('Failed to save profile');
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

