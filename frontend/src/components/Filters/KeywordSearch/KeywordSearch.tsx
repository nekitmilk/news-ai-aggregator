import { TextInput } from '@mantine/core';
import { IconSearch } from '@tabler/icons-react';
import classes from './KeywordSearch.module.scss';

type Props = { value?: string; onChange: (v: string) => void };

export function KeywordSearch({ value, onChange }: Props) {
  return (
    <TextInput
      label={
        <div className={classes.label}>
          <IconSearch style={{ width: 20, height: 20 }} />
          Поиск по ключевым словам
        </div>
      }
      placeholder="Введите ключевое слово..."
      value={value ?? ''}
      onChange={(e) => onChange(e.currentTarget.value)}
      radius="md"
      withAsterisk={false}
      classNames={{
        root: classes.root,
        input: classes.input,
        section: classes.section,
      }}
    />
  );
}
