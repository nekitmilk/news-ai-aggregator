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
      </Card>
    </motion.div>
  );
}
