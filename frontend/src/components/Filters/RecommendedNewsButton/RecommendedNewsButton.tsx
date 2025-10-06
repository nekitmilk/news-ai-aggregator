// RecommendedNewsButton.tsx
import { IconSparkles } from '@tabler/icons-react'; // Иконка для рекомендаций
import classes from './RecommendedNewsButton.module.scss';

type Props = {
  onClick: () => void;
  disabled?: boolean;
  loading?: boolean;
  active?: boolean; // Показывает, активен ли сейчас режим рекомендаций
};

export function RecommendedNewsButton({ onClick, disabled, loading, active }: Props) {
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={`${classes.button} ${loading ? classes.loading : ''} ${active ? classes.active : ''}`}
    >
      {!loading && <IconSparkles className={classes.icon} />}
      {loading ? 'Загрузка...' : 'Показать рекомендуемые новости'}
    </button>
  );
}
