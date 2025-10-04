import { useEffect, useState } from 'react';
import { MantineProvider, Group, Stack, Paper } from '@mantine/core';
import { CategoryPicker } from './components/Filters/CategoryPicker/CategoryPicker';
import { SourcePicker } from './components/Filters/SourcePicker/SourcePicker';
import { DateRangePicker } from './components/Filters/DateRangePicker/DateRangePicker';
import { KeywordSearch } from './components/Filters/KeywordSearch/KeywordSearch';
import { ApplyFiltersButton } from './components/Filters/ApplyFiltersButton/ApplyFiltersButton';
import { SortOrder } from './components/Filters/SortOrder/SortOrder';
import { NewsBlock } from './components/News/NewsBlock';
import { fetchNews } from './api/fetchNews';
import classes from './App.module.scss';
import dayjs from 'dayjs';
import 'dayjs/locale/ru';
import './styles/globals.scss';

dayjs.locale('ru');

interface NewsItem {
  id: string;
  title: string;
  summary: string;
  category: string;
  source: string;
  url: string;
  date: string;
}

export default function App() {
  const [category, setCategory] = useState<string[]>([]);
  const [source, setSource] = useState<string[]>([]);
  const [keyword, setKeyword] = useState<string>('');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [sort, setSort] = useState<string>('desc');
  const [news, setNews] = useState<NewsItem[]>([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);

  async function getNews(isLoadMore = false) {
    if (loading) return;

    setLoading(true);
    const filters = {
      category: category.length > 0 ? category : null,
      source: source.length > 0 ? source : null,
      search: keyword,
      start_date: startDate || null,
      end_date: endDate || null,
      page: isLoadMore ? page : 1,
      limit: 5,
      sort,
    };
    console.log(JSON.stringify(filters));
    try {
      const newNews = await fetchNews(filters);

      if (isLoadMore) {
        setNews((prev) => [...prev, ...newNews]);
      } else {
        setNews(newNews);
        setPage(1);
      }
      console.log(hasMore);
      setHasMore(newNews.length === filters.limit);
    } catch (error) {
      console.error('Error fetching news:', error);
    } finally {
      setLoading(false);
    }
  }

  function handleApplyFilters() {
    setPage(1);
    getNews(false);
  }

  //   function loadMore() {
  //     if (hasMore && !loading) {
  //       setPage((prev) => prev + 1);
  //     }
  //   }

  useEffect(() => {
    if (page > 1) {
      getNews(true);
    }
  }, [page]);

  useEffect(() => {
    setPage(1);
  }, [category, source, keyword, startDate, endDate, sort]);

  // Загружаем новости при первом рендере
  useEffect(() => {
    getNews(false);
  }, []);

  return (
    <MantineProvider
      theme={{
        fontFamily: 'Montserrat, sans-serif',
        headings: {
          fontFamily: 'Montserrat, sans-serif',
        },
      }}
    >
      <main className={classes.main}>
        <section className={classes.section}>
          <Paper className={classes.paper}>
            <Stack>
              <Group className={classes.filterRow}>
                <div className={classes.filterItem}>
                  <CategoryPicker value={category} onChange={setCategory} />
                </div>
                <div className={classes.filterItem}>
                  <SourcePicker value={source} onChange={setSource} />
                </div>
                <div className={classes.filterItem}>
                  <KeywordSearch value={keyword} onChange={setKeyword} />
                </div>
              </Group>

              <Group className={classes.filterRow}>
                <div className={classes.dateContainer}>
                  <DateRangePicker
                    startDate={startDate}
                    endDate={endDate}
                    onStartChange={setStartDate}
                    onEndChange={setEndDate}
                  />
                </div>
                <div className={classes.sortOrderWrapper}>
                  <SortOrder value={sort} onChange={setSort} />
                </div>
                <div className={classes.buttonContainer}>
                  <ApplyFiltersButton onClick={handleApplyFilters} disabled={loading} />
                </div>
              </Group>
            </Stack>
          </Paper>

          <Stack className={classes.newsList}>
            {news.map((item, idx) => (
              <NewsBlock
                key={`${item.id}-${idx}`}
                name={item.title}
                description={item.summary}
                category={item.category}
                source={item.source}
                date={item.date}
              />
            ))}

            {news.length === 0 && !loading && (
              <Paper className={classes.emptyState}>
                <div className={classes.emptyText}>Новости не найдены. Измените параметры фильтрации.</div>
              </Paper>
            )}
          </Stack>
        </section>
      </main>
    </MantineProvider>
  );
}
