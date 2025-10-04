import axios from 'axios';

export interface NewsFilters {
  category: string[] | null;
  source: string[] | null;
  search: string;
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

interface NewsResponse {
  errors: null;
  message: string;
  requestId: string;
  result: NewsItem[];
  success: boolean;
}

export async function fetchNews(filters: NewsFilters) {
  const params = {
    ...filters,
    sort: filters.sort ?? undefined,
  };
  const res = await axios.get<NewsResponse>('http://localhost:8000/api/v1/news', { params });
  return res.data.result;
}
