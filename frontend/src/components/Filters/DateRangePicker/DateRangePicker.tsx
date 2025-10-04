import { DateInput } from '@mantine/dates';
import { Group } from '@mantine/core';
import { IconCalendar, IconCalendarEvent } from '@tabler/icons-react';
import dayjs from 'dayjs';
import { useState } from 'react';
import classes from './DateRangePicker.module.scss';
import '@mantine/dates/styles.css';

type Props = {
  startDate?: string;
  endDate?: string;
  onStartChange: (v: string) => void;
  onEndChange: (v: string) => void;
};

export function DateRangePicker({ startDate, endDate, onStartChange, onEndChange }: Props) {
  const [startInputValue, setStartInputValue] = useState('');
  const [endInputValue, setEndInputValue] = useState('');
  console.log(startInputValue, endInputValue);
  const handleStartChange = (value: string | null) => {
    if (value) {
      // Конвертируем из формата DD.MM.YYYY в YYYY-MM-DD
      const parsed = dayjs(value, 'DD.MM.YYYY', true);
      if (parsed.isValid()) {
        onStartChange(parsed.format('YYYY-MM-DD'));
      } else {
        onStartChange('');
      }
    } else {
      onStartChange('');
    }
  };

  const handleEndChange = (value: string | null) => {
    if (value) {
      // Конвертируем из формата DD.MM.YYYY в YYYY-MM-DD
      const parsed = dayjs(value, 'DD.MM.YYYY', true);
      if (parsed.isValid()) {
        onEndChange(parsed.format('YYYY-MM-DD'));
      } else {
        onEndChange('');
      }
    } else {
      onEndChange('');
    }
  };

  // Конвертируем YYYY-MM-DD в DD.MM.YYYY для отображения
  const formatForDisplay = (dateString: string | undefined) => {
    if (!dateString) return '';
    const date = dayjs(dateString, 'YYYY-MM-DD');
    return date.isValid() ? date.format('DD.MM.YYYY') : '';
  };

  return (
    <Group className={classes.container}>
      <DateInput
        label={
          <div className={classes.label}>
            <IconCalendar style={{ width: 20, height: 20 }} />
            Начальная дата
          </div>
        }
        placeholder="Выберите дату..."
        value={formatForDisplay(startDate)}
        onChange={handleStartChange}
        onInput={(event) => {
          const value = event.currentTarget.value;
          setStartInputValue(value);
          if (value === '') {
            onStartChange('');
          }
        }}
        radius="md"
        valueFormat="DD.MM.YYYY"
        locale="ru"
        clearable
        classNames={{
          root: classes.datePicker,
          input: classes.dateInput,
          label: classes.label,
          month: classes.month,
        }}
        allowDeselect
        inputWrapperOrder={['label', 'input', 'error']}
        onKeyDown={(e) => {
          if (!/[\d\.]|Backspace|Delete|Tab|ArrowLeft|ArrowRight|ArrowUp|ArrowDown/.test(e.key)) {
            e.preventDefault();
          }
        }}
        onPaste={(e) => {
          e.preventDefault();
        }}
        styles={{
          day: {
            '&[data-selected], &[data-selected]:hover': {
              backgroundColor: '#3182ce',
              color: 'white',
            },
            '&[data-in-range], &[data-in-range]:hover': {
              backgroundColor: '#3182ce',
              color: 'white',
              opacity: '0.5',
            },
            '&[data-first-in-range], &[data-first-in-range]:hover': {
              backgroundColor: '#3182ce',
              color: 'white',
              opacity: '1',
            },
            '&[data-last-in-range], &[data-last-in-range]:hover': {
              backgroundColor: '#3182ce',
              color: 'white',
              opacity: '1',
            },
          },
          input: {
            '&:focus': {
              borderColor: '#3182ce',
            },
          },
        }}
        popoverProps={{
          classNames: {
            dropdown: classes.calendarDropdown,
          },
          transitionProps: {
            duration: 0,
          },
        }}
      />
      <DateInput
        label={
          <div className={classes.label}>
            <IconCalendarEvent style={{ width: 20, height: 20 }} />
            Конечная дата
          </div>
        }
        placeholder="Выберите дату..."
        value={formatForDisplay(endDate)}
        onChange={handleEndChange}
        onInput={(event) => {
          const value = event.currentTarget.value;
          setEndInputValue(value);
          if (value === '') {
            onEndChange('');
          }
        }}
        radius="md"
        valueFormat="DD.MM.YYYY"
        locale="ru"
        clearable
        classNames={{
          root: classes.datePicker,
          input: classes.dateInput,
          label: classes.label,
          month: classes.month,
        }}
        allowDeselect
        inputWrapperOrder={['label', 'input', 'error']}
        onKeyDown={(e) => {
          if (!/[\d\.]|Backspace|Delete|Tab|ArrowLeft|ArrowRight|ArrowUp|ArrowDown/.test(e.key)) {
            e.preventDefault();
          }
        }}
        onPaste={(e) => {
          e.preventDefault();
        }}
        styles={{
          day: {
            '&[data-selected], &[data-selected]:hover': {
              backgroundColor: '#3182ce',
              color: 'white',
            },
            '&[data-in-range], &[data-in-range]:hover': {
              backgroundColor: '#3182ce',
              color: 'white',
              opacity: '0.5',
            },
            '&[data-first-in-range], &[data-first-in-range]:hover': {
              backgroundColor: '#3182ce',
              color: 'white',
              opacity: '1',
            },
            '&[data-last-in-range], &[data-last-in-range]:hover': {
              backgroundColor: '#3182ce',
              color: 'white',
              opacity: '1',
            },
          },
          input: {
            '&:focus': {
              borderColor: '#3182ce',
            },
          },
        }}
        popoverProps={{
          classNames: {
            dropdown: classes.calendarDropdown,
          },
          transitionProps: {
            duration: 0,
          },
        }}
        minDate={startDate ? dayjs(startDate).toDate() : undefined}
      />
    </Group>
  );
}
