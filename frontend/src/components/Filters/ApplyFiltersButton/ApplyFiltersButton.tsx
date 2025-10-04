import { IconBolt } from '@tabler/icons-react';
import classes from './ApplyFiltersButton.module.scss';

type Props = { onClick: () => void; disabled?: boolean; loading?: boolean };

export function ApplyFiltersButton({ onClick, disabled, loading }: Props) {
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={`${classes.button} ${loading ? classes.loading : ''}`}
    >
      {!loading && <IconBolt className={classes.icon} />}
      {loading ? 'Загрузка...' : 'Применить фильтры'}
    </button>
  );
}
