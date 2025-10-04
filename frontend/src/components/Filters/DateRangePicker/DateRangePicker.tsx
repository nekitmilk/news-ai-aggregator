import { DateInput } from '@mantine/dates';
import { Group } from '@mantine/core';
import { IconCalendar, IconCalendarEvent } from '@tabler/icons-react';
import dayjs from 'dayjs';
import classes from './DateRangePicker.module.scss';
import '@mantine/dates/styles.css';

type Props = {
  startDate?: string;
  endDate?: string;
  onStartChange: (v: string) => void;
  onEndChange: (v: string) => void;
};

export function DateRangePicker({ startDate, endDate, onStartChange, onEndChange }: Props) {
  const handleDateChange = (date: Date | null, isStartDate: boolean) => {
    const changeHandler = isStartDate ? onStartChange : onEndChange;
    // Просто передаем пустую строку или null, без форматирования
    changeHandler(date ? '' : '');
  };

  const dateParser = (value: string) => {
    if (!value || value.trim() === '') {
      return null;
    }
    const parsed = dayjs(value, 'DD.MM.YYYY', true);
    return parsed.isValid() && parsed.year() > 1900 ? parsed.toDate() : null;
  };

  // Конвертируем строку в Date для value пропса
  const parseStringToDate = (dateString?: string): Date | null => {
    if (!dateString) return null;
    const parsed = dayjs(dateString, 'YYYY-MM-DD', true);
    return parsed.isValid() ? parsed.toDate() : null;
  };

  const sharedProps = {
    radius: 'md' as const,
    valueFormat: 'DD.MM.YYYY' as const,
    locale: 'ru' as const,
    clearable: true,
    allowDeselect: false,
    inputWrapperOrder: ['label', 'input', 'error'] as const,
    classNames: {
      root: classes.datePicker,
      input: classes.dateInput,
      label: classes.label,
    },
    styles: {
      day: {
        '&[data-selected], &[data-selected]:hover': {
          backgroundColor: '#3182ce',
          color: 'white',
        },
        '&[data-in-range], &[data-in-range]:hover': {
          backgroundColor: '#3182ce',
          color: 'white',
          opacity: 0.5,
        },
        '&[data-first-in-range], &[data-first-in-range]:hover': {
          backgroundColor: '#3182ce',
          color: 'white',
          opacity: 1,
        },
        '&[data-last-in-range], &[data-last-in-range]:hover': {
          backgroundColor: '#3182ce',
          color: 'white',
          opacity: 1,
        },
      },
      input: {
        '&:focus': {
          borderColor: '#3182ce',
        },
      },
    },
    popoverProps: {
      classNames: {
        dropdown: classes.calendarDropdown,
      },
      transitionProps: { duration: 0 },
    },
    dateParser,
    onKeyDown: (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (!/[\d.]|Backspace|Delete|Tab|ArrowLeft|ArrowRight|ArrowUp|ArrowDown/.test(e.key)) {
        e.preventDefault();
      }
    },
    onPaste: (e: React.ClipboardEvent<HTMLInputElement>) => {
      e.preventDefault();
    },
  };

  return (
    <Group className={classes.container}>
      <DateInput
        {...sharedProps}
        label={
          <div className={classes.label}>
            <IconCalendar className={classes.labelIcon} />
            Начальная дата
          </div>
        }
        placeholder="Выберите дату..."
        value={parseStringToDate(startDate)}
        onChange={(date) => handleDateChange(date, true)}
      />

      <DateInput
        {...sharedProps}
        label={
          <div className={classes.label}>
            <IconCalendarEvent className={classes.labelIcon} />
            Конечная дата
          </div>
        }
        placeholder="Выберите дату..."
        value={parseStringToDate(endDate)}
        onChange={(date) => handleDateChange(date, false)}
        minDate={parseStringToDate(startDate) || undefined}
      />
    </Group>
  );
}
