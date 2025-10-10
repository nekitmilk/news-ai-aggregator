import { Card, Group, Text, Badge, Button } from '@mantine/core';
import { motion } from 'framer-motion';
import { useApi } from '@/hooks/useApi';
import { IconExternalLink } from '@tabler/icons-react';
import classes from './NewsBlock.module.scss';

type NewsBlockProps = {
  id: string;
  key: string;
  name: string;
  description: string;
  category: string;
  source: string;
  date: string;
  url: string;
  userId: number;
};

export function NewsBlock({ id, name, description, category, source, date, url, userId }: NewsBlockProps) {
  const { makeRequest } = useApi();

  const handleTrackAndOpen = async () => {
    try {
      await makeRequest('/user-history/', {
        method: 'POST',
        data: {
          news_id: id,
          user_id: userId,
          view_timestamp: new Date().toISOString(),
        },
      });
    } catch (error) {
      console.error('Ошибка при отправке истории:', error);
    } finally {
      window.open(url, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <motion.div className={classes.container}>
      <Card className={classes.card} radius="md" withBorder>
        <Group className={classes.header}>
          <Text className={classes.title}>{name}</Text>
          <Badge className={classes.category}>{category}</Badge>
        </Group>
        <Text className={classes.description}>{description}</Text>
        <Group className={classes.footer}>
          <Group className={classes.sourceGroup}>
            <Text className={classes.date}>Источник: </Text>
            <Badge className={classes.source}>{source}</Badge>
          </Group>
          <Text className={classes.date}>{date}</Text>
        </Group>
        <Button
          fullWidth
          variant="light"
          rightSection={<IconExternalLink size={16} />}
          onClick={handleTrackAndOpen}
          className={classes.readButton}
        >
          Читать новость
        </Button>
      </Card>
    </motion.div>
  );
}
