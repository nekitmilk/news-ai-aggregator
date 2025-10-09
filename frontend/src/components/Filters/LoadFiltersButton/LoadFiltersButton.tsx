import { IconFilterShare } from '@tabler/icons-react';
import classes from './LoadFiltersButton.module.scss';
import { useApi } from '@/hooks/useApi';
import { Toast } from '@/components/common/ToastNotify/ToastNotify';
import { useEffect, useState } from 'react';

type Props = {
  disabled?: boolean;
  loading?: boolean;
  userId: number | null;
  onFiltersLoad?: (filters: any) => void;
  onError?: (error: string) => void;
};

export function LoadFiltersButton({ disabled, loading: externalLoading, userId, onFiltersLoad, onError }: Props) {
  const { makeRequest, loading: apiLoading, error } = useApi();
  const [showToast, setShowToast] = useState(false);
  const isLoading = externalLoading || apiLoading;

  const handleLoadFilters = async () => {
    if (!userId) {
      onError?.('Пользователь не авторизован');
      return;
    }
    const result = await makeRequest<any[]>('/users/filters/', {
      method: 'GET',
      params: {
        user_id: userId,
      },
    });
    if (result.success && result.data) {
      const filters = result.data;
      console.log(filters[0]);
      onFiltersLoad?.(filters[0]);
    } else {
      console.error('Ошибка загрузки фильтров:', result.error);
      onError?.(result.error || 'Неизвестная ошибка');
      setShowToast(true);
    }
  };

  useEffect(() => {
    if (error) {
      setShowToast(true);
    }
  }, [error]);

  return (
    <>
      <button
        onClick={handleLoadFilters}
        disabled={disabled || isLoading}
        className={`${classes.button} ${isLoading ? classes.loading : ''}`}
      >
        <IconFilterShare className={classes.icon} />
        Загрузить фильтры
      </button>
      <Toast
        show={showToast}
        onClose={() => setShowToast(false)}
        title="Ошибка"
        message={'Не удалось загрузить фильтры'}
        type="error"
        duration={3000}
      />
    </>
  );
}
