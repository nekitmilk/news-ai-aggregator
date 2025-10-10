import { IconBolt } from '@tabler/icons-react';
import classes from './ApplyFiltersButton.module.scss';
import { useEffect, useState } from 'react';

type Props = { onClick: () => void; disabled?: boolean; loading?: boolean };

export function ApplyFiltersButton({ onClick, disabled, loading }: Props) {
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
    <button onClick={onClick} disabled={isActuallyDisabled || loading} className={`${classes.button}`}>
      {<IconBolt className={classes.icon} />}
      Применить фильтры
    </button>
  );
}
