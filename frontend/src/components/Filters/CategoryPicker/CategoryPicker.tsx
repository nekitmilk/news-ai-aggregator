import { useEffect, useState } from 'react';
import { MultiSelect } from '@mantine/core';
import { IconCategory, IconChevronDown } from '@tabler/icons-react';
import classes from './CategoryPicker.module.scss';
import { fetchCategories } from '@/api/fetchCategories';
type Props = { value: string[]; onChange: (v: string[]) => void };

export function CategoryPicker({ value = [], onChange }: Props) {
  const [categories, setCategories] = useState<{ label: string; value: string }[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadCategories = async () => {
      try {
        setLoading(true);
        const serverCategories = await fetchCategories();
        const formattedCategories = serverCategories.map((cat) => ({
          label: cat.name,
          value: cat.id,
        }));
        console.log(formattedCategories);
        setCategories(formattedCategories);
      } catch (error) {
        console.error('Error fetching categories:', error);
        // При ошибке оставляем пустой массив
        setCategories([]);
      } finally {
        setLoading(false);
      }
    };

    loadCategories();
  }, []);

  const iconStyle = {
    width: 18,
    height: 18,
    transition: 'transform 0.2s ease',
    transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
  };

  const placeholder = loading ? 'Загрузка категорий...' : value?.length > 0 ? '' : 'Выберите категории...';

  return (
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
      clearable={false}
      nothingFoundMessage="Категория не найдена"
      withAsterisk={false}
      radius="md"
      rightSection={<IconChevronDown style={iconStyle} />}
      onDropdownOpen={() => setIsOpen(true)}
      onDropdownClose={() => setIsOpen(false)}
      maxDropdownHeight={230}
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
          transition: 'fade',
          duration: 0,
        },
        position: 'bottom' as const,
        middlewares: { flip: true, shift: true },
        offset: 4,
      }}
    />
  );
}
