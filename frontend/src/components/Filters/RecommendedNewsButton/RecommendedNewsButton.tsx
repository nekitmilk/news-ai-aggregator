import { IconSparkles } from '@tabler/icons-react';
import { useState, useEffect } from 'react';
import classes from './RecommendedNewsButton.module.scss';

type Props = {
  onClick: () => void;
  disabled?: boolean;
  loading?: boolean;
  active?: boolean;
};

export function RecommendedNewsButton({ onClick, disabled, loading, active }: Props) {
  const [isActuallyDisabled, setIsActuallyDisabled] = useState(disabled);

  useEffect(() => {
    if (disabled) {
      setIsActuallyDisabled(true);
      return;
    }

    const timer = setTimeout(() => {
      setIsActuallyDisabled(false);
    }, 300);

    return () => clearTimeout(timer);
  }, [disabled]);

  return (
    <button
      onClick={onClick}
      disabled={isActuallyDisabled || loading}
      className={`${classes.button} ${loading ? classes.loading : ''} ${active ? classes.active : ''}`}
    >
      <IconSparkles className={classes.icon} />
      {active ? 'Скрыть рекомендации' : 'Показать рекомендуемые новости'}
    </button>
  );
}
