import { IconFilterShare } from '@tabler/icons-react';
import classes from './LoadFiltersButton.module.scss';
import { useApi } from '@/hooks/useApi';

type Props = {
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
  userId: number | null;
  onFiltersLoad?: (filters: any) => void;
  onError?: (error: string) => void;
};

export function LoadFiltersButton({
  onClick,
  disabled,
  loading: externalLoading,
  userId,
  //   onFiltersLoad,
  onError,
}: Props) {
  const { makeRequest, loading: apiLoading, error } = useApi();

  const isLoading = externalLoading || apiLoading;

  const handleLoadFilters = async () => {
    // Если передан внешний обработчик, вызываем его
    if (onClick) {
      onClick();
      return;
    }

    if (!userId) {
      onError?.('Пользователь не авторизован');
      return;
    }

    try {
      const result = await makeRequest('/users/filters/', {
        method: 'GET',
        headers: {
          user_id: userId,
        },
      });

      if (result.success) {
        // if (result.data && result.data.length > 0) {
        //   // Берем последний сохраненный фильтр
        //   //   const latestFilter = result.data[result.data.length - 1];
        //   //   const loadedFilters = {
        //   //     category: latestFilter.category || [],
        //   //     source: latestFilter.source || [],
        //   //     keyword: latestFilter.search || '',
        //   //     startDate: latestFilter.start_date || '',
        //   //     endDate: latestFilter.end_date || '',
        //   //     sort: latestFilter.sort || 'desc',
        //   //   };
        //   //   onFiltersLoad?.(loadedFilters);
        //   //   // Сохраняем в localStorage для быстрого доступа
        //   //   localStorage.setItem('saved_filters', JSON.stringify(loadedFilters));
        // } else {
        //   onError?.('Нет сохраненных фильтров');
        // }
      } else {
        console.error('Ошибка загрузки фильтров:', result.error);
        onError?.(result.error || 'Неизвестная ошибка');
      }
    } catch (err) {
      console.error('Исключение при загрузке фильтров:', err);
      onError?.(err instanceof Error ? err.message : 'Неизвестная ошибка');
    }
  };

  return (
    <button
      onClick={handleLoadFilters}
      disabled={disabled || isLoading || !userId}
      className={`${classes.button} ${isLoading ? classes.loading : ''}`}
      title={error ? `Ошибка: ${error}` : !userId ? 'Требуется авторизация' : undefined}
    >
      {!isLoading && <IconFilterShare className={classes.icon} />}
      {isLoading ? 'Загрузка...' : 'Загрузить фильтры'}
    </button>
  );
}
