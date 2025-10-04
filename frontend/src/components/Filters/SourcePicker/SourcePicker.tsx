import { useEffect, useState } from 'react';
import { MultiSelect } from '@mantine/core';
import { IconWorld, IconChevronDown } from '@tabler/icons-react';
import classes from './SourcePicker.module.scss';
import { fetchSources } from '@/api/fetchSouces';
type Props = { value: string[]; onChange: (v: string[]) => void };

export function SourcePicker({ value = [], onChange }: Props) {
  const [sources, setSources] = useState<{ label: string; value: string }[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadSources = async () => {
      try {
        setLoading(true);
        const serverSources = await fetchSources();

        const formattedSources = serverSources.map((src: any) => ({
          label: src.name,
          value: src.id,
        }));
        setSources(formattedSources);
      } catch (error) {
        console.error('Error fetching sources:', error);
        setSources([]);
      } finally {
        setLoading(false);
      }
    };

    loadSources();
  }, []);

  const iconStyle = {
    width: 18,
    height: 18,
    transition: 'transform 0.2s ease',
    transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
  };

  const placeholder = loading ? 'Загрузка источников...' : value?.length > 0 ? '' : 'Выберите источники...';

  return (
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
  );
}
