import { IconFilterDown } from '@tabler/icons-react';
import classes from './SaveFiltersButton.module.scss';
import { useApi } from '@/hooks/useApi';
import { Toast } from '@/components/common/ToastNotify/ToastNotify';
import { useState } from 'react';

type Props = {
  disabled?: boolean;
  loading?: boolean;
  filters: {
    category: string[];
    source: string[];
    search: string;
    start_date: string;
    end_date: string;
    sort: string;
  };
  userId: number | null;
  onSuccess?: (data: any) => void;
  onError?: (error: string) => void;
};

export function SaveFiltersButton({ disabled, loading: externalLoading, filters, userId, onSuccess, onError }: Props) {
  const { makeRequest, loading: apiLoading } = useApi();
  const [toast, setToast] = useState<{
    show: boolean;
    type: 'success' | 'error';
    title: string;
    message: string;
  }>({
    show: false,
    type: 'success',
    title: '',
    message: '',
  });

  const isLoading = externalLoading || apiLoading;

  const showToast = (type: 'success' | 'error', title: string, message: string) => {
    setToast({ show: true, type, title, message });
  };

  const hideToast = () => {
    setToast((prev) => ({ ...prev, show: false }));
  };

  const handleSaveFilters = async () => {
    const filterData = {
      category: filters.category,
      source: filters.source,
      search: filters.search,
      start_date: filters.start_date,
      end_date: filters.end_date,
      sort: filters.sort,
    };

    const result = await makeRequest('/users/filters/', {
      method: 'POST',
      data: filterData,
      headers: {
        'X-User-ID': userId,
      },
    });

    if (result.success) {
      showToast('success', 'Успех', 'Фильтры успешно сохранены');
      onSuccess?.(result.data);
    } else {
      showToast('error', 'Ошибка', 'Не удалось сохранить фильтры');
      onError?.(result.error || 'Неизвестная ошибка');
    }
  };

  return (
    <>
      <button
        onClick={handleSaveFilters}
        disabled={disabled || isLoading}
        className={`${classes.button} ${isLoading ? classes.loading : ''}`}
      >
        <IconFilterDown className={classes.icon} />
        Сохранить фильтры
      </button>

      <Toast
        show={toast.show}
        onClose={hideToast}
        title={toast.title}
        message={toast.message}
        type={toast.type}
        duration={3000}
      />
    </>
  );
}
