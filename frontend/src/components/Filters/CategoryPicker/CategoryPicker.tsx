import { useEffect, useState } from 'react';
import { MultiSelect } from '@mantine/core';
import { IconCategory, IconChevronDown } from '@tabler/icons-react';
import classes from './CategoryPicker.module.scss';
import { useApi } from '@/hooks/useApi';
import { Toast } from '@/components/common/ToastNotify/ToastNotify';

type Props = {
  value: string[];
  onChange: (v: string[]) => void;
  disabled: boolean;
  savedValue?: string[];
};

export function CategoryPicker({ value = [], onChange, disabled, savedValue = [] }: Props) {
  const [categories, setCategories] = useState<{ label: string; value: string }[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const { makeRequest, loading, error } = useApi();

  const isChanged = JSON.stringify(value) !== JSON.stringify(savedValue);

  useEffect(() => {
    const loadCategories = async () => {
      const result = await makeRequest<Category[]>('/categories/');
      if (result.success && result.data) {
        const formattedCategories = result.data.map((cat) => ({
          label: cat.name,
          value: cat.id,
        }));
        setCategories(formattedCategories);
      } else {
        console.error('Error fetching categories:', result.error);
        setCategories([]);
        setShowToast(true);
      }
    };

    loadCategories();
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

  const placeholder = loading ? 'Загрузка категорий...' : value?.length > 0 ? '' : 'Выберите категории...';

  return (
    <>
      <div className={`${classes.root} ${isChanged ? classes.changed : ''}`}>
        <MultiSelect
          label={
            <div className={classes.label}>
              <IconCategory style={{ width: 20, height: 20 }} />
              Категории новостей
            </div>
          }
          placeholder={placeholder}
          data={categories}
          value={value || []}
          onChange={(newValue) => onChange(newValue || [])}
          searchable
          disabled={disabled}
          clearable={false}
          nothingFoundMessage="Категория не найдена"
          withAsterisk={false}
          radius="md"
          rightSection={<IconChevronDown style={iconStyle} />}
          onDropdownOpen={() => setIsOpen(true)}
          onDropdownClose={() => setIsOpen(false)}
          maxDropdownHeight={230}
          classNames={{
            root: classes.multiSelectRoot,
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
              transition: 'fade',
              duration: 0,
            },
            position: 'bottom' as const,
            middlewares: { flip: true, shift: true },
            offset: 4,
          }}
        />
      </div>
      <Toast
        show={showToast}
        onClose={() => setShowToast(false)}
        title="Ошибка"
        message={'Не удалось загрузить категории'}
        type="error"
        duration={3000}
      />
    </>
  );
}
