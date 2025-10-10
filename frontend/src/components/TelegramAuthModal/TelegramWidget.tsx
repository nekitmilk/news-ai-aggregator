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
  const [isLoading, setIsLoading] = useState(true);
  const scriptLoadedRef = useRef(false); 

  useEffect(() => {
    if (isVisible) {
      setShouldRender(true);
    } else {
      const timer = setTimeout(() => setShouldRender(false), 300);
      return () => clearTimeout(timer);
    }
  }, [isVisible]);

  useEffect(() => {
    if (!containerRef.current || !shouldRender || scriptLoadedRef.current) return;

    const callbackName = `onTelegramAuth_${Date.now()}`;
    setIsLoading(true);

    (window as any)[callbackName] = (user: ITelegramUser) => {
      onAuth(user);
      delete (window as any)[callbackName];
    };

    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://telegram.org/js/telegram-widget.js?22';
    script.setAttribute('data-telegram-login', botUsername);
    script.setAttribute('data-size', 'large');
    script.setAttribute('data-radius', '20');
    script.setAttribute('data-request-access', 'write');
    script.setAttribute('data-onauth', `${callbackName}(user)`);

    script.onload = () => {
      setIsLoading(false);
      scriptLoadedRef.current = true;
    };

    script.onerror = () => {
      setIsLoading(false);
      console.error('Ошибка загрузки Telegram Widget');
    };

    containerRef.current.appendChild(script);

    return () => {
      if ((window as any)[callbackName]) {
        delete (window as any)[callbackName];
      }
      setIsLoading(false);
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
        position: 'relative',
      }}
    >
      {isLoading && (
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            color: '#6c757d',
            fontSize: '14px',
            fontWeight: 500,
          }}
        >
          <div
            style={{
              width: '16px',
              height: '16px',
              border: '2px solid #e9ecef',
              borderTop: '2px solid #3b76d9',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
            }}
          />
          Загрузка виджета...
        </div>
      )}
    </div>
  );
}
