import { useEffect, useState } from 'react';
import { AxiosError } from 'axios';
import { fetchTrustedContacts, searchTrustedContacts } from '../services/trustedContactsService';
import { TrustedContactListResponse, TrustedContactModel } from '../types/trustedContact';

interface UseTrustedContactsResult {
  contacts: TrustedContactModel[];
  page: number;
  pageSize: number;
  total: number;
  searchInput: string;
  loading: boolean;
  error: string | null;
  pageCount: number;
  setPage: (value: number) => void;
  setSearchInput: (value: string) => void;
  refresh: () => Promise<void>;
}

export function useTrustedContacts(): UseTrustedContactsResult {
  const [contacts, setContacts] = useState<TrustedContactModel[]>([]);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [total, setTotal] = useState(0);
  const [searchInput, setSearchInput] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadContacts = async () => {
    setLoading(true);
    setError(null);

    try {
      const data: TrustedContactListResponse = searchQuery
        ? await searchTrustedContacts(searchQuery, page, pageSize)
        : await fetchTrustedContacts(page, pageSize);

      setContacts(data.items);
      setTotal(data.total);
    } catch (err) {
      if (err instanceof AxiosError) {
        setError(err.response?.data?.detail || err.message || 'Unable to load trusted contacts.');
      } else {
        setError('Unable to load trusted contacts.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setPage(1);
      setSearchQuery(searchInput.trim());
    }, 350);

    return () => window.clearTimeout(timer);
  }, [searchInput]);

  useEffect(() => {
    loadContacts();
  }, [page, pageSize, searchQuery]);

  const refresh = async () => {
    await loadContacts();
  };

  const pageCount = Math.max(1, Math.ceil(total / pageSize));

  return {
    contacts,
    page,
    pageSize,
    total,
    searchInput,
    loading,
    error,
    pageCount,
    setPage,
    setSearchInput,
    refresh,
  };
}
