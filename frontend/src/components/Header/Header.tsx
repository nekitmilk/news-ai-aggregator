// components/Header/Header.tsx
import { Group, Container, Button, Text, Menu, Avatar, Modal } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { IconBrandTelegram, IconNews, IconLogout, IconUserFilled } from '@tabler/icons-react';
import { ITelegramUser } from '../../types/telegram';
import classes from './Header.module.scss';

interface HeaderProps {
  onTelegramClick: () => void;
  isAuthenticated: boolean;
  user: ITelegramUser | null;
  onLogout: () => void;
}

export function Header({ onTelegramClick, isAuthenticated, user, onLogout }: HeaderProps) {
  const [opened, { open, close }] = useDisclosure(false);

  const handleLogout = () => {
    onLogout();
    close();
  };

  const getUserDisplayName = () => {
    if (!user) return '';

    if (user.first_name && user.last_name) {
      return `${user.first_name} ${user.last_name}`;
    }

    return user.first_name || user.username || 'Пользователь';
  };

  const getUserInitials = () => {
    if (!user) return 'U';

    if (user.first_name) {
      return user.first_name.charAt(0).toUpperCase();
    }

    if (user.username) {
      return user.username.charAt(0).toUpperCase();
    }

    return 'U';
  };

  return (
    <div className={classes.header}>
      <Container size="xl" className={classes.headerContainer}>
        <Group justify="space-between" align="center" h="100%" w="100%">
          <Group gap="sm">
            <IconNews size={32} color="#3182ce" />
            <Text fw={700} size="xl" className={classes.logoText}>
              NewsAggregator
            </Text>
          </Group>

          {isAuthenticated ? (
            <Menu
              shadow="md"
              width={200}
              position="bottom-end"
              classNames={{
                dropdown: classes.menuDropdown,
                label: classes.menuLabel,
                item: classes.menuItem,
              }}
            >
              <Menu.Target>
                <Button
                  variant="light"
                  radius="md"
                  size="md"
                  leftSection={
                    user?.photo_url ? (
                      <Avatar src={user.photo_url} size={26} radius="xl" />
                    ) : (
                      <Avatar size={26} radius="xl" color="blue">
                        {getUserInitials()}
                      </Avatar>
                    )
                  }
                  className={classes.authButton}
                >
                  {getUserDisplayName()}
                </Button>
              </Menu.Target>

              <Menu.Dropdown>
                <Menu.Item leftSection={<IconUserFilled size={18} />} className={classes.username}>
                  {user?.username ? `@${user.username}` : 'Пользователь'}
                </Menu.Item>
                <Menu.Divider />
                <Menu.Item leftSection={<IconLogout size={18} />} onClick={open} className={classes.logout}>
                  Выйти из аккаунта
                </Menu.Item>
              </Menu.Dropdown>
            </Menu>
          ) : (
            <Button
              leftSection={<IconBrandTelegram size={22} />}
              variant="gradient"
              gradient={{ from: '#0088cc', to: '#24a1de' }}
              radius="md"
              size="md"
              onClick={onTelegramClick}
              className={classes.telegramButton}
            >
              Авторизация
            </Button>
          )}
        </Group>
      </Container>

      <Modal
        opened={opened}
        onClose={close}
        title="Подтверждение выхода"
        centered
        size="sm"
        overlayProps={{
          backgroundOpacity: 0.55,
        }}
      >
        <Text size="sm" mb="md">
          Вы уверены, что хотите выйти из аккаунта?
        </Text>

        <Group justify="flex-end" gap="sm">
          <Button variant="default" onClick={close}>
            Отмена
          </Button>
          <Button variant="filled" color="#fa5252" onClick={handleLogout} leftSection={<IconLogout size={18} />}>
            Выйти
          </Button>
        </Group>
      </Modal>
    </div>
  );
}
