import { useEffect, useState } from 'react';
import { MultiSelect } from '@mantine/core';
import { IconWorld, IconChevronDown } from '@tabler/icons-react';
import classes from './SourcePicker.module.scss';
import { useApi } from '@/hooks/useApi';
import { Toast } from '@/components/common/ToastNotify/ToastNotify';

type Props = { value: string[]; onChange: (v: string[]) => void; disabled: boolean };

export function SourcePicker({ value = [], onChange, disabled }: Props) {
  const [sources, setSources] = useState<{ label: string; value: string }[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const { makeRequest, loading, error } = useApi();

  useEffect(() => {
    const loadSources = async () => {
      const result = await makeRequest<Source[]>('/sources/');

      if (result.success && result.data) {
        const formattedSources = result.data.map((src) => ({
          label: src.name,
          value: src.id,
        }));
        setSources(formattedSources);
      } else {
        console.error('Error fetching sources:', result.error);
        setSources([]);
        setShowToast(true);
      }
    };

    loadSources();
  }, [makeRequest]);

  useEffect(() => {
    if (error) {
      setShowToast(true);
    }
  }, [error]);

  const iconStyle = {
    width: 18,
    height: 18,
    transition: 'transform 0.2s ease',
    transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
  };

  const placeholder = loading ? 'Загрузка источников...' : value?.length > 0 ? '' : 'Выберите источники...';

  return (
    <>
      <MultiSelect
        label={
          <div className={classes.label}>
            <IconWorld style={{ width: 20, height: 20 }} />
            Источники новостей
          </div>
        }
        placeholder={placeholder}
        data={sources}
        value={value || []}
        onChange={(newValue) => onChange(newValue || [])}
        searchable
        disabled={disabled}
        clearable={false}
        nothingFoundMessage="Источник не найден"
        withAsterisk={false}
        radius="md"
        rightSection={<IconChevronDown style={iconStyle} />}
        onDropdownOpen={() => setIsOpen(true)}
        onDropdownClose={() => setIsOpen(false)}
        maxDropdownHeight={200}
        classNames={{
          root: classes.root,
          wrapper: classes.wrapper,
          input: classes.input,
          label: classes.label,
          dropdown: classes.dropdown,
          option: classes.option,
          pill: classes.pill,
          pillsList: classes.pillsList,
          section: classes.section,
        }}
        comboboxProps={{
          transitionProps: {
            duration: 0,
          },
          position: 'bottom' as const,
          middlewares: { flip: true, shift: true },
          offset: 4,
        }}
      />

      <Toast
        show={showToast}
        onClose={() => setShowToast(false)}
        title="Ошибка"
        message={'Не удалось загрузить источники'}
        type="error"
        duration={5000}
      />
    </>
  );
}
