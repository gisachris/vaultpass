import { api } from '../lib/api';
import { UserProfile, UpdateProfilePayload } from '../types/settings';

export async function getProfile(): Promise<UserProfile> {
  const response = await api.get<UserProfile>('/settings/profile');
  return response.data;
}

export async function updateProfile(payload: UpdateProfilePayload): Promise<UserProfile> {
  const response = await api.put<UserProfile>('/settings/profile', payload);
  return response.data;
}
