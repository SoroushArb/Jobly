// API client utilities for backend communication

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
