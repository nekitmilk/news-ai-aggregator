import { IconFilterOff } from '@tabler/icons-react';
import classes from './ClearFiltersButton.module.scss';

type Props = {
  disabled?: boolean;
  onClear: () => void;
};

export function ClearFiltersButton({ disabled, onClear }: Props) {
  return (
    <>
      <button onClick={onClear} disabled={disabled} className={classes.button}>
        <IconFilterOff className={classes.icon} />
        Очистить фильтры
      </button>
    </>
  );
}
