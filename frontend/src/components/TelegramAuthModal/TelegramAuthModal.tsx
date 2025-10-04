import { Modal } from '@mantine/core';
import { ITelegramUser } from '../../types/telegram';
import { TelegramWidget } from './TelegramWidget';
import classes from './TelegramAuthModal.module.scss';

interface TelegramAuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAuthSuccess: (user: ITelegramUser) => void;
  botUsername: string;
}

export function TelegramAuthModal({ isOpen, onClose, onAuthSuccess, botUsername }: TelegramAuthModalProps) {
  return (
    <Modal opened={isOpen} onClose={onClose} title="Авторизация через Telegram" size="sm" centered>
      <div className={classes.modalContent}>
        <div className={classes.description}>Нажмите на кнопку ниже для авторизации через Telegram</div>

        <TelegramWidget botUsername={botUsername} onAuth={onAuthSuccess} />
      </div>
    </Modal>
  );
}
