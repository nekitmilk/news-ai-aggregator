import { useEffect, useState } from 'react';
import { TextInput, ActionIcon } from '@mantine/core';
import { IconSearch, IconX } from '@tabler/icons-react';
import classes from './KeywordSearch.module.scss';

type Props = {
  value?: string;
  onChange: (v: string) => void;
  disabled: boolean;
  savedValue?: string;
};

export function KeywordSearch({ value = '', onChange, disabled, savedValue }: Props) {
  const [localValue, setLocalValue] = useState(value);
  const [isChanged, setIsChanged] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (localValue !== value) {
        onChange(localValue);
      }
    }, 300); 

    return () => clearTimeout(timer);
  }, [localValue, onChange, value]);

  useEffect(() => {
    setIsChanged(localValue !== savedValue);
  }, [localValue, savedValue]);

  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  const handleClear = () => {
    setLocalValue('');
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLocalValue(e.currentTarget.value);
  };

  return (
    <TextInput
      label={
        <div className={classes.label}>
          <IconSearch style={{ width: 20, height: 20 }} />
          Поиск по ключевому слову
        </div>
      }
      placeholder="Введите ключевое слово..."
      value={localValue}
      disabled={disabled}
      onChange={handleChange}
      radius="md"
      withAsterisk={false}
      rightSection={
        localValue && !disabled ? (
          <ActionIcon size="sm" variant="subtle" onClick={handleClear} className={classes.clearButton}>
            <IconX size={16} />
          </ActionIcon>
        ) : null
      }
      classNames={{
        root: classes.root,
        input: `${classes.input} ${isChanged ? classes.changed : ''}`,
        section: classes.section,
      }}
    />
  );
}
