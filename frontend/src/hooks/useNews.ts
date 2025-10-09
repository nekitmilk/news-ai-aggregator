import { useCallback } from 'react';
import { useApi } from './useApi';

export interface NewsFilters {
  category: string[] | null;
  source: string[] | null;
  search: string | null;
  start_date: string | null;
  end_date: string | null;
  page: number | null;
  limit: number | null;
  sort: string | null;
}

interface NewsItem {
  id: string;
  title: string;
  summary: string;
  category: string;
  source: string;
  url: string;
  date: string;
}

export function useNews() {
  const { makeRequest, loading, error, clearError } = useApi();

  const fetchNews = useCallback(
    async (filters: NewsFilters) => {
      const params = {
        ...filters,
        sort: filters.sort ?? undefined,
      };

      const result = await makeRequest<NewsItem[]>('/news', {
        method: 'GET',
        params,
      });

      return result.success ? result.data || [] : [];
    },
    [makeRequest],
  );

  return {
    fetchNews,
    loading,
    error,
    clearError,
  };
}
