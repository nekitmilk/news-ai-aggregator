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
        value={startDate ? new Date(startDate) : null}
        onChange={(date) => onStartChange(date ? dayjs(date).format('YYYY-MM-DD') : '')}
        radius="md"
        valueFormat="DD.MM.YYYY"
        locale="ru"
        classNames={{
          root: classes.datePicker,
          input: classes.dateInput,
          label: classes.label,
          month: classes.month, // ← добавляем стили для календаря
        }}
        popoverProps={{
          classNames: {
            dropdown: classes.calendarDropdown,
          },
          transitionProps: {
            duration: 0,
          },
        }}
        dateParser={(input: string) => {
          const formats = ['DD.MM.YYYY', 'DD-MM-YYYY', 'DD/MM/YYYY', 'YYYY-MM-DD'];
          for (const format of formats) {
            const parsed = dayjs(input, format, true);
            if (parsed.isValid()) {
              return parsed.toDate();
            }
          }
          return null;
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
        value={endDate ? new Date(endDate) : null}
        onChange={(date) => onEndChange(date ? dayjs(date).format('YYYY-MM-DD') : '')}
        radius="md"
        valueFormat="DD.MM.YYYY"
        locale="ru"
        classNames={{
          root: classes.datePicker,
          input: classes.dateInput,
          label: classes.label,
          section: classes.section,
        }}
        popoverProps={{
          classNames: {
            dropdown: classes.calendarDropdown,
          },
          transitionProps: {
            duration: 0,
          },
        }}
        dateParser={(input: string) => {
          const formats = ['DD.MM.YYYY', 'DD-MM-YYYY', 'DD/MM/YYYY', 'YYYY-MM-DD'];
          for (const format of formats) {
            const parsed = dayjs(input, format, true);
            if (parsed.isValid()) {
              return parsed.toDate();
            }
          }
          return null;
        }}
        minDate={startDate ? new Date(startDate) : undefined}
      />
    </Group>
  );
}
