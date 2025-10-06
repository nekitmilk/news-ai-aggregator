import { useEffect, useRef, useState } from 'react';
import { ITelegramUser } from '../../types/telegram';

interface TelegramWidgetProps {
  botUsername: string;
  onAuth: (user: ITelegramUser) => void;
  isVisible?: boolean;
}

export function TelegramWidget({ botUsername, onAuth, isVisible = true }: TelegramWidgetProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [shouldRender, setShouldRender] = useState(isVisible);

  useEffect(() => {
    if (isVisible) {
      setShouldRender(true);
    } else {
      const timer = setTimeout(() => setShouldRender(false), 300);
      return () => clearTimeout(timer);
    }
  }, [isVisible]);

  useEffect(() => {
    if (!containerRef.current || !shouldRender) return;

    const callbackName = `onTelegramAuth_${Date.now()}`;

    (window as any)[callbackName] = (user: ITelegramUser) => {
      onAuth(user);
      delete (window as any)[callbackName];
    };

    containerRef.current.innerHTML = '';

    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://telegram.org/js/telegram-widget.js?22';
    script.setAttribute('data-telegram-login', botUsername);
    script.setAttribute('data-size', 'large');
    script.setAttribute('data-radius', '20');
    script.setAttribute('data-request-access', 'write');
    script.setAttribute('data-onauth', `${callbackName}(user)`);

    containerRef.current.appendChild(script);

    return () => {
      if (containerRef.current) {
        containerRef.current.innerHTML = '';
      }
      if ((window as any)[callbackName]) {
        delete (window as any)[callbackName];
      }
    };
  }, [botUsername, onAuth, shouldRender]);

  if (!shouldRender) {
    return null;
  }

  return (
    <div
      ref={containerRef}
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '50px',
        padding: '10px',
        backgroundColor: '#f8f9fa',
        borderRadius: '12px',
        border: '1px solid #e9ecef',
        opacity: isVisible ? 1 : 0,
        transition: 'opacity 0.3s ease',
      }}
    />
  );
}
