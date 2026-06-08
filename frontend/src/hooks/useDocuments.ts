import { useEffect, useMemo, useState } from 'react';
import { AxiosError } from 'axios';
import { fetchDocuments } from '../services/documentService';
import {
  DocumentCategoryFilter,
  DocumentModel,
  DocumentType,
  DOCUMENT_CATEGORY_TYPE_MAP,
} from '../types/document';

interface UseDocumentsResult {
  documents: DocumentModel[];
  visibleDocuments: DocumentModel[];
  page: number;
  limit: number;
  total: number;
  searchInput: string;
  category: DocumentCategoryFilter;
  sortNewestFirst: boolean;
  loading: boolean;
  error: string | null;
  errorStatus: number | null;
  pageCount: number;
  setPage: (value: number) => void;
  setSearchInput: (value: string) => void;
  setCategory: (value: DocumentCategoryFilter) => void;
  toggleSortDirection: () => void;
  refresh: () => Promise<void>;
}

export function useDocuments(): UseDocumentsResult {
  const [documents, setDocuments] = useState<DocumentModel[]>([]);
  const [visibleDocuments, setVisibleDocuments] = useState<DocumentModel[]>([]);
  const [page, setPage] = useState(1);
  const [limit] = useState(10);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [category, setCategory] = useState<DocumentCategoryFilter>('ALL');
  const [sortNewestFirst, setSortNewestFirst] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errorStatus, setErrorStatus] = useState<number | null>(null);

  const loadDocuments = async () => {
    setLoading(true);
    setError(null);
    setErrorStatus(null);

    try {
      const data = await fetchDocuments(page, limit, search || undefined);
      setDocuments(data.items);
      setTotal(data.total);
    } catch (err) {
      if (err instanceof AxiosError) {
        setError(err.response?.data?.detail || err.message || 'Unable to load documents.');
        setErrorStatus(err.response?.status ?? null);
      } else {
        setError('Unable to load documents.');
        setErrorStatus(null);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setPage(1);
      setSearch(searchInput.trim());
    }, 350);

    return () => window.clearTimeout(timer);
  }, [searchInput]);

  useEffect(() => {
    loadDocuments();
  }, [page, limit, search]);

  useEffect(() => {
    const filtered = documents.filter((document) => {
      if (category === 'ALL') {
        return true;
      }
      return DOCUMENT_CATEGORY_TYPE_MAP[category].includes(document.document_type);
    });

    const sorted = [...filtered].sort((a, b) => {
      const aTime = new Date(a.uploaded_at).getTime();
      const bTime = new Date(b.uploaded_at).getTime();
      return sortNewestFirst ? bTime - aTime : aTime - bTime;
    });

    setVisibleDocuments(sorted);
  }, [category, documents, sortNewestFirst]);

  const toggleSortDirection = () => {
    setSortNewestFirst((current) => !current);
  };

  const refresh = async () => {
    await loadDocuments();
  };

  const pageCount = Math.max(1, Math.ceil(total / limit));

  return {
    documents,
    visibleDocuments,
    page,
    limit,
    total,
    searchInput,
    category,
    sortNewestFirst,
    loading,
    error,
    errorStatus,
    pageCount,
    setPage,
    setSearchInput,
    setCategory,
    toggleSortDirection,
    refresh,
  };
}
