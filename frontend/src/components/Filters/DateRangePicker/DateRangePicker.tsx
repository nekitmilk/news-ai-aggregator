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
  const filterInput = (event: React.KeyboardEvent<HTMLInputElement>) => {
    const allowedKeys = [
      '0',
      '1',
      '2',
      '3',
      '4',
      '5',
      '6',
      '7',
      '8',
      '9',
      '.', 
      '-', 
      'Backspace',
      'Delete',
      'Tab',
      'ArrowLeft',
      'ArrowRight',
      'ArrowUp',
      'ArrowDown',
    ];

    if (!allowedKeys.includes(event.key)) {
      event.preventDefault();
    }
  };

  const getDateValue = (dateString: string | undefined): Date | null => {
    if (!dateString) return null;

    if (dateString.includes('-') || dateString.includes('.')) {
      const separator = dateString.includes('-') ? '-' : '.';
      const [day, month, year] = dateString.split(separator);
      if (day && month && year) {
        const date = new Date(`${year}-${month}-${day}`);
        return isNaN(date.getTime()) ? null : date;
      }
    }
    const date = new Date(dateString);
    return isNaN(date.getTime()) ? null : date;
  };

  const getMinDate = (): Date | undefined => {
    if (!startDate) return undefined;
    return getDateValue(startDate) || undefined;
  };

  const getMaxDate = (): Date | undefined => {
    if (!endDate) return undefined;
    return getDateValue(endDate) || undefined;
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
        placeholder="дд.мм.гггг" 
        value={getDateValue(startDate)}
        onChange={(date) => {
          if (date) {
            const formatted = dayjs(date).format('DD-MM-YYYY');
            onStartChange(formatted);
          } else {
            onStartChange('');
          }
        }}
        onKeyDown={filterInput}
        radius="md"
        valueFormat="DD.MM.YYYY" 
        locale="ru"
        classNames={{
          root: classes.datePicker,
          input: classes.dateInput,
          label: classes.label,
          day: classes.day,
        }}
        popoverProps={{
          classNames: {
            dropdown: classes.calendarDropdown,
          },
        }}
        maxDate={getMaxDate()}
        allowDeselect
        clearable
      />
      <DateInput
        label={
          <div className={classes.label}>
            <IconCalendarEvent style={{ width: 20, height: 20 }} />
            Конечная дата
          </div>
        }
        placeholder="дд.мм.гггг" 
        value={getDateValue(endDate)}
        onChange={(date) => {
          if (date) {
            const formatted = dayjs(date).format('DD-MM-YYYY');
            onEndChange(formatted);
          } else {
            onEndChange('');
          }
        }}
        onKeyDown={filterInput}
        radius="md"
        valueFormat="DD.MM.YYYY" 
        locale="ru"
        classNames={{
          root: classes.datePicker,
          input: classes.dateInput,
          label: classes.label,
          day: classes.day,
        }}
        popoverProps={{
          classNames: {
            dropdown: classes.calendarDropdown,
          },
        }}
        minDate={getMinDate()}
        allowDeselect
        clearable
      />
    </Group>
  );
}
