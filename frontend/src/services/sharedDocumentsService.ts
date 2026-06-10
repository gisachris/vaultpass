import { api } from '../lib/api';
import { ReceivedShare, ReceivedShareDetail } from '../types/receivedDocuments';

export async function fetchReceivedShares(): Promise<ReceivedShare[]> {
  const response = await api.get<ReceivedShare[]>('/v1/shares/shared-with-me');
  return response.data;
}

export async function fetchReceivedShareDetail(shareId: string): Promise<ReceivedShareDetail> {
  const response = await api.get<ReceivedShareDetail>(`/v1/shares/shared-with-me/${shareId}`);
  return response.data;
}
