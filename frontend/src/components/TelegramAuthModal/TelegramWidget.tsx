import { useEffect, useRef } from 'react';
import { ITelegramUser } from '../../types/telegram';

declare global {
  interface Window {
    onTelegramAuth: (user: ITelegramUser) => void;
  }
}

interface TelegramWidgetProps {
  botUsername: string;
  onAuth: (user: ITelegramUser) => void;
}

export function TelegramWidget({ botUsername, onAuth }: TelegramWidgetProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Очищаем контейнер
    if (containerRef.current) {
      containerRef.current.innerHTML = '';
    }

    // Создаем скрипт
    const script = document.createElement('script');
    script.src = 'https://telegram.org/js/telegram-widget.js?22';
    script.async = true;
    script.setAttribute('data-telegram-login', botUsername);
    script.setAttribute('data-size', 'large');
    script.setAttribute('data-radius', '20');
    script.setAttribute('data-request-access', 'write');
    script.setAttribute('data-onauth', 'onTelegramAuth');

    // Устанавливаем callback
    window.onTelegramAuth = onAuth;

    // Добавляем скрипт в контейнер
    if (containerRef.current) {
      containerRef.current.appendChild(script);
    }

    return () => {
      // Очистка
      if (containerRef.current) {
        containerRef.current.innerHTML = '';
      }
    };
  }, [botUsername, onAuth]);

  return (
    <div
      ref={containerRef}
      style={{
        display: 'flex',
        justifyContent: 'center',
        minHeight: '44px',
      }}
    />
  );
}
