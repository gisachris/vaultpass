import { useEffect, useState, useCallback } from 'react';
import { AxiosError } from 'axios';
import {
  fetchFamilySummary,
  fetchFamilyMembers,
  fetchSentInvitations,
  fetchReceivedInvitations,
  sendInvitation,
  acceptInvitation,
  declineInvitation,
  removeRelationship
} from '../api/familyService';
import {
  FamilySummary,
  FamilyRelationship,
  FamilyInvitationCreate
} from '../types';

interface UseFamilyResult {
  summary: FamilySummary | null;
  members: FamilyRelationship[];
  sentInvitations: FamilyRelationship[];
  receivedInvitations: FamilyRelationship[];
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  inviteMember: (payload: FamilyInvitationCreate) => Promise<void>;
  acceptInvite: (id: string) => Promise<void>;
  declineInvite: (id: string) => Promise<void>;
  removeRelation: (id: string) => Promise<void>;
}

export function useFamily(): UseFamilyResult {
  const [summary, setSummary] = useState<FamilySummary | null>(null);
  const [members, setMembers] = useState<FamilyRelationship[]>([]);
  const [sentInvitations, setSentInvitations] = useState<FamilyRelationship[]>([]);
  const [receivedInvitations, setReceivedInvitations] = useState<FamilyRelationship[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadFamilyData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [summaryData, membersData, sentData, receivedData] = await Promise.all([
        fetchFamilySummary(),
        fetchFamilyMembers(),
        fetchSentInvitations(),
        fetchReceivedInvitations()
      ]);
      setSummary(summaryData);
      setMembers(membersData);
      setSentInvitations(sentData);
      setReceivedInvitations(receivedData);
    } catch (err) {
      if (err instanceof AxiosError) {
        setError(err.response?.data?.detail || err.message || 'Unable to load family hub data.');
      } else {
        setError('Unable to load family hub data.');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadFamilyData();
  }, [loadFamilyData]);

  const refresh = async () => {
    await loadFamilyData();
  };

  const inviteMember = async (payload: FamilyInvitationCreate) => {
    try {
      await sendInvitation(payload);
      await loadFamilyData();
    } catch (err) {
      if (err instanceof AxiosError) {
        throw new Error(err.response?.data?.detail || err.message || 'Failed to send invitation.');
      }
      throw err;
    }
  };

  const acceptInvite = async (id: string) => {
    try {
      await acceptInvitation(id);
      await loadFamilyData();
    } catch (err) {
      if (err instanceof AxiosError) {
        throw new Error(err.response?.data?.detail || err.message || 'Failed to accept invitation.');
      }
      throw err;
    }
  };

  const declineInvite = async (id: string) => {
    try {
      await declineInvitation(id);
      await loadFamilyData();
    } catch (err) {
      if (err instanceof AxiosError) {
        throw new Error(err.response?.data?.detail || err.message || 'Failed to decline invitation.');
      }
      throw err;
    }
  };

  const removeRelation = async (id: string) => {
    try {
      await removeRelationship(id);
      await loadFamilyData();
    } catch (err) {
      if (err instanceof AxiosError) {
        throw new Error(err.response?.data?.detail || err.message || 'Failed to remove relationship.');
      }
      throw err;
    }
  };

  return {
    summary,
    members,
    sentInvitations,
    receivedInvitations,
    loading,
    error,
    refresh,
    inviteMember,
    acceptInvite,
    declineInvite,
    removeRelation
  };
}
