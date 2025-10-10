import { Portal, Box } from '@mantine/core';
import { IconX } from '@tabler/icons-react';
import { useEffect } from 'react';
import classes from './ToastNotify.module.scss';

interface ToastProps {
  show: boolean;
  onClose: () => void;
  title: string;
  message: string;
  type?: 'error' | 'success' | 'warning';
  duration?: number;
}

export function Toast({ show, onClose, title, message, type = 'error', duration = 3000 }: ToastProps) {
  useEffect(() => {
    if (show && duration > 0) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [show, duration, onClose]);

  if (!show) return null;

  const backgroundColor = {
    error: '#fa5252',
    success: '#38a169',
    warning: '#fcc419',
  }[type];

  return (
    <Portal>
      <Box className={classes.toast} style={{ backgroundColor }}>
        <div className={classes.toastContent}>
          <div className={classes.toastText}>
            <div className={classes.toastTitle}>{title}</div>
            <div className={classes.toastMessage}>{message}</div>
          </div>
          <button className={classes.toastClose} onClick={onClose}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <IconX size={16} />
            </div>
          </button>
        </div>
      </Box>
    </Portal>
  );
}
