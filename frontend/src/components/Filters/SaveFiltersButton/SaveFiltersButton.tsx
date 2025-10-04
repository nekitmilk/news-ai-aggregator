import { IconFilterDown } from '@tabler/icons-react';
import classes from './SaveFiltersButton.module.scss';

type Props = { onClick: () => void; disabled?: boolean; loading?: boolean };

export function SaveFiltersButton({ onClick, disabled, loading }: Props) {
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={`${classes.button} ${loading ? classes.loading : ''}`}
    >
      {!loading && <IconFilterDown className={classes.icon} />}
      {loading ? 'Загрузка...' : 'Сохранить фильтры'}
    </button>
  );
}
