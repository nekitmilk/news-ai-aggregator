import { useState, useCallback } from 'react';
import axios from 'axios';

export function useApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const makeRequest = useCallback(
    async <T>(
      url: string,
      options: {
        method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
        data?: any;
        params?: any;
        headers?: any;
      } = {},
    ): Promise<{ data: T | null; success: boolean; error: string | null }> => {
      const { method = 'GET', data, params, headers = {} } = options;

      try {
        setLoading(true);
        setError(null);

        const apiUrl = `/api/api/v1${url}`;
        console.log(data, headers, params);
        const response = await axios({
          url: apiUrl,
          method,
          data,
          params,
          headers: {
            'Content-Type': 'application/json',
            ...headers,
          },
        });

        const apiResponse = response.data as ApiResponse<T>;

        if (!apiResponse.success) {
          const errorMessage = apiResponse.message || 'Request failed';
          setError(errorMessage);
          return {
            data: null,
            success: false,
            error: errorMessage,
          };
        }

        if (apiResponse.errors) {
          console.warn('API warnings:', apiResponse.errors);
        }

        return {
          data: apiResponse.result,
          success: true,
          error: null,
        };
      } catch (err: any) {
        const errorMessage = axios.isAxiosError(err)
          ? err.response?.data?.message || err.message
          : 'Unknown error occurred';

        setError(errorMessage);
        return {
          data: null,
          success: false,
          error: errorMessage,
        };
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    makeRequest,
    loading,
    error,
    clearError,
  };
}
