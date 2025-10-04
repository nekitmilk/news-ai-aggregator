import { Card, Group, Text, Badge } from '@mantine/core';
import { motion } from 'framer-motion';
import classes from './NewsBlock.module.scss';

type NewsBlockProps = {
  name: string;
  description: string;
  category: string;
  source: string;
  date: string;
};

export function NewsBlock({ name, description, category, source, date }: NewsBlockProps) {
  return (
    <motion.div
      className={classes.container}
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
    >
      <Card className={classes.card} radius="md" withBorder>
        <Group justify="space-between" align="flex-start">
          <Text className={classes.title}>{name}</Text>
          <Badge className={classes.category}>{category}</Badge>
        </Group>
        <Text className={classes.description}>{description}</Text>
        <Group className={classes.footer}>
          <Badge className={classes.source}>{source}</Badge>
          <Text className={classes.date}>{date}</Text>
        </Group>
      </Card>
    </motion.div>
  );
}
