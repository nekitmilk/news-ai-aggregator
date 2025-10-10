import { DateInput } from '@mantine/dates';
import { Group } from '@mantine/core';
import { IconCalendarPlus, IconCalendarMinus } from '@tabler/icons-react';
import dayjs from 'dayjs';
import classes from './DateRangePicker.module.scss';
import '@mantine/dates/styles.css';

type Props = {
  startDate?: string;
  endDate?: string;
  savedStartDate?: string;
  savedEndDate?: string;
  onStartChange: (v: string) => void;
  onEndChange: (v: string) => void;
  disabled: boolean;
};

export function DateRangePicker({
  startDate,
  endDate,
  savedStartDate,
  savedEndDate,
  onStartChange,
  onEndChange,
  disabled,
}: Props) {
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
    if (!allowedKeys.includes(event.key)) event.preventDefault();
  };

  const getDateValue = (dateString?: string): Date | null => {
    if (!dateString) return null;
    const separator = dateString.includes('-') ? '-' : dateString.includes('.') ? '.' : null;
    if (!separator) return new Date(dateString);
    const [day, month, year] = dateString.split(separator);
    const parsed = new Date(`${year}-${month}-${day}`);
    return isNaN(parsed.getTime()) ? null : parsed;
  };

  const start = getDateValue(startDate);
  const end = getDateValue(endDate);

  const isStartChanged = startDate !== savedStartDate;
  const isEndChanged = endDate !== savedEndDate;

  return (
    <Group className={classes.container}>
      <DateInput
        label={
          <div className={classes.label}>
            <IconCalendarPlus style={{ width: 20, height: 20 }} />
            Начальная дата
          </div>
        }
        placeholder="дд.мм.гггг"
        value={start}
        onChange={(date) => {
          onStartChange(date ? dayjs(date).format('DD-MM-YYYY') : '');
        }}
        onKeyDown={filterInput}
        radius="md"
        disabled={disabled}
        valueFormat="DD.MM.YYYY"
        locale="ru"
        classNames={{
          root: classes.datePicker,
          input: `${classes.dateInput} ${isStartChanged ? classes.changed : ''}`,
          label: classes.label,
          day: classes.day,
        }}
        popoverProps={{
          classNames: {
            dropdown: classes.calendarDropdown,
          },
        }}
        maxDate={end || undefined}
        allowDeselect
        clearable
      />
      <DateInput
        label={
          <div className={classes.label}>
            <IconCalendarMinus style={{ width: 20, height: 20 }} />
            Конечная дата
          </div>
        }
        placeholder="дд.мм.гггг"
        value={end}
        onChange={(date) => {
          onEndChange(date ? dayjs(date).format('DD-MM-YYYY') : '');
        }}
        onKeyDown={filterInput}
        radius="md"
        valueFormat="DD.MM.YYYY"
        locale="ru"
        disabled={disabled}
        classNames={{
          root: classes.datePicker,
          input: `${classes.dateInput} ${isEndChanged ? classes.changed : ''}`,
          label: classes.label,
          day: classes.day,
        }}
        popoverProps={{
          classNames: {
            dropdown: classes.calendarDropdown,
          },
        }}
        minDate={start || undefined}
        allowDeselect
        clearable
      />
    </Group>
  );
}
