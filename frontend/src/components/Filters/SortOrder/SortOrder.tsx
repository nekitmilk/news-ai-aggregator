import { Group } from '@mantine/core';
import { IconSortAscending, IconSortDescending } from '@tabler/icons-react';
import classes from './SortOrder.module.scss';

type Props = { value: string | undefined; onChange: (v: string) => void };

export function SortOrder({ value, onChange }: Props) {
  return (
    <Group gap="xs" wrap="nowrap" className={classes.container}>
      <button
        type="button"
        onClick={() => onChange('desc')}
        className={`${classes.button} ${value === 'desc' ? classes.buttonActive : ''}`}
      >
        <IconSortDescending style={{ width: 20, height: 20 }} />
        Сначала новые
      </button>

      <button
        type="button"
        onClick={() => onChange('asc')}
        className={`${classes.button} ${value === 'asc' ? classes.buttonActive : ''}`}
      >
        <IconSortAscending style={{ width: 20, height: 20 }} />
        Сначала старые
      </button>
    </Group>
  );
}
