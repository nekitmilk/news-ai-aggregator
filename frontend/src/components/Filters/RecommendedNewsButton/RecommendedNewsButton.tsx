// RecommendedNewsButton.tsx
import { IconSparkles } from '@tabler/icons-react'; // Иконка для рекомендаций
import classes from './RecommendedNewsButton.module.scss';

type Props = {
  onClick: () => void;
  disabled?: boolean;
  loading?: boolean;
  active?: boolean;
};

export function RecommendedNewsButton({ onClick, disabled, loading, active }: Props) {
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={`${classes.button} ${loading ? classes.loading : ''} ${active ? classes.active : ''}`}
    >
      <IconSparkles className={classes.icon} />
      Показать рекомендуемые новости
    </button>
  );
}
