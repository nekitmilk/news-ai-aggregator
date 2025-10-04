import { Group, Container, Button, Text, Menu, Avatar } from '@mantine/core';
import { IconBrandTelegram, IconNews, IconLogout } from '@tabler/icons-react';
import { ITelegramUser } from '../../types/telegram';
import classes from './Header.module.scss';

interface HeaderProps {
  onTelegramClick: () => void;
  isAuthenticated: boolean;
  user: ITelegramUser | null;
  onLogout: () => void;
}

export function Header({ onTelegramClick, isAuthenticated, user, onLogout }: HeaderProps) {
  const getUserDisplayName = () => {
    if (!user) return '';

    if (user.first_name && user.last_name) {
      return `${user.first_name} ${user.last_name}`;
    }

    return user.first_name || user.username || 'Пользователь';
  };

  const getUserInitials = () => {
    if (!user) return '';

    if (user.first_name) {
      return user.first_name.charAt(0).toUpperCase();
    }

    return 'U';
  };

  return (
    <div className={classes.header}>
      <Container size="xl" className={classes.headerContainer}>
        <Group justify="space-between" align="center" h="100%">
          <Group gap="sm">
            <IconNews size={28} color="#3182ce" />
            <Text fw={700} size="xl" className={classes.logoText}>
              NewsAggregator
            </Text>
          </Group>

          {isAuthenticated ? (
            <Menu shadow="md" width={200}>
              <Menu.Target>
                <Button
                  variant="light"
                  radius="xl"
                  size="md"
                  leftSection={
                    user?.photo_url ? (
                      <Avatar src={user.photo_url} size={24} radius="xl" />
                    ) : (
                      <Avatar size={24} radius="xl" color="blue">
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
                <Menu.Label>@{user?.username || 'user'}</Menu.Label>
                <Menu.Item leftSection={<IconLogout size={14} />} onClick={onLogout} color="red">
                  Выйти
                </Menu.Item>
              </Menu.Dropdown>
            </Menu>
          ) : (
            <Button
              leftSection={<IconBrandTelegram size={20} />}
              variant="gradient"
              gradient={{ from: '#0088cc', to: '#24a1de' }}
              radius="xl"
              size="md"
              onClick={onTelegramClick}
              className={classes.telegramButton}
            >
              Авторизация
            </Button>
          )}
        </Group>
      </Container>
    </div>
  );
}
