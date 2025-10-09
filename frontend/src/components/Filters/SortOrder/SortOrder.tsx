import { Group } from '@mantine/core';
import { IconSortAscending, IconSortDescending, IconReorder } from '@tabler/icons-react';
import classes from './SortOrder.module.scss';

type Props = { value: string | undefined; onChange: (v: string) => void; disabled: boolean };

export function SortOrder({ value, onChange, disabled }: Props) {
  return (
    <div className={classes.wrapper}>
      <label className={classes.label}>
        <IconReorder style={{ width: 20, height: 20 }} />
        Сортировать по
      </label>
      <Group gap="xs" wrap="nowrap" className={classes.container}>
        <button
          type="button"
          onClick={() => onChange('desc')}
          className={`${classes.button} ${value === 'desc' ? classes.buttonActive : ''}`}
          disabled={disabled}
        >
          <IconSortDescending style={{ width: 20, height: 20 }} />
          Сначала новые
        </button>

        <button
          type="button"
          onClick={() => onChange('asc')}
          className={`${classes.button} ${value === 'asc' ? classes.buttonActive : ''}`}
          disabled={disabled}
        >
          <IconSortAscending style={{ width: 20, height: 20 }} />
          Сначала старые
        </button>
      </Group>
    </div>
  );
}
