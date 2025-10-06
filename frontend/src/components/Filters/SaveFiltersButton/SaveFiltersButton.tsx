import { IconFilterDown } from '@tabler/icons-react';
import classes from './SaveFiltersButton.module.scss';
import { useApi } from '@/hooks/useApi';
import { Toast } from '@/components/common/ToastNotify/ToastNotify';
import { useState } from 'react';

type Props = {
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
  filters: {
    category: string[];
    source: string[];
    keyword: string;
    startDate: string;
    endDate: string;
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
    if (!userId) {
      showToast('error', 'Ошибка', 'Пользователь не авторизован');
      onError?.('Пользователь не авторизован');
      return;
    }

    try {
      const filterData = {
        category: filters.category,
        source: filters.source,
        search: filters.keyword,
        start_date: filters.startDate,
        end_date: filters.endDate,
        sort: filters.sort,
      };

      const result = await makeRequest('/users/filters/', {
        method: 'POST',
        data: filterData,
        headers: {
          'X-User-ID': userId.toString(),
        },
      });

      if (result.success) {
        showToast('success', 'Успех', 'Фильтры успешно сохранены');
        onSuccess?.(result.data);
        localStorage.setItem('saved_filters', JSON.stringify(filters));
      } else {
        showToast('error', 'Ошибка', 'Не удалось сохранить фильтры');
        onError?.(result.error || 'Неизвестная ошибка');
      }
    } catch (err) {
      const errorMessage = 'Неизвестная ошибка';
      showToast('error', 'Ошибка', 'Не удалось сохранить фильтры');
      onError?.(errorMessage);
    }
  };

  return (
    <>
      <button
        onClick={handleSaveFilters}
        disabled={disabled || isLoading || !userId}
        className={`${classes.button} ${isLoading ? classes.loading : ''}`}
        title={!userId ? 'Требуется авторизация' : undefined}
      >
        {!isLoading && <IconFilterDown className={classes.icon} />}
        {isLoading ? 'Сохранение...' : 'Сохранить фильтры'}
      </button>

      <Toast
        show={toast.show}
        onClose={hideToast}
        title={toast.title}
        message={toast.message}
        type={toast.type}
        duration={5000}
      />
    </>
  );
}
