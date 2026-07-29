import { api } from '../lib/api';
import {
  TrustedContactCreatePayload,
  TrustedContactListResponse,
  TrustedContactModel,
} from '../types/trustedContact';

const BASE_PATH = '/v1/trusted-contacts';

export async function fetchTrustedContacts(
  page: number,
  pageSize: number,
): Promise<TrustedContactListResponse> {
  const response = await api.get<TrustedContactListResponse>(BASE_PATH, {
    params: {
      page,
      page_size: pageSize,
    },
  });
  return response.data;
}

export async function searchTrustedContacts(
  query: string,
  page: number,
  pageSize: number,
): Promise<TrustedContactListResponse> {
  const response = await api.get<TrustedContactListResponse>(`${BASE_PATH}/search`, {
    params: {
      q: query.trim(),
      page,
      page_size: pageSize,
    },
  });
  return response.data;
}

export async function createTrustedContact(
  payload: TrustedContactCreatePayload,
): Promise<{ message: string; data: TrustedContactModel }> {
  const response = await api.post<{ message: string; data: TrustedContactModel }>(BASE_PATH, payload);
  return response.data;
}

export async function deleteTrustedContact(contactId: string): Promise<void> {
  await api.delete(`${BASE_PATH}/${contactId}`);
}

export async function updateTrustedContact(
  contactId: string,
  payload: Partial<TrustedContactCreatePayload>,
): Promise<TrustedContactModel> {
  const response = await api.patch<TrustedContactModel>(`${BASE_PATH}/${contactId}`, payload);
  return response.data;
}
