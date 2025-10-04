import { useEffect, useState, useCallback } from 'react';
import { MantineProvider, Group, Stack, Paper, AppShell } from '@mantine/core';
import { CategoryPicker } from './components/Filters/CategoryPicker/CategoryPicker';
import { SourcePicker } from './components/Filters/SourcePicker/SourcePicker';
import { DateRangePicker } from './components/Filters/DateRangePicker/DateRangePicker';
import { KeywordSearch } from './components/Filters/KeywordSearch/KeywordSearch';
import { ApplyFiltersButton } from './components/Filters/ApplyFiltersButton/ApplyFiltersButton';
import { SortOrder } from './components/Filters/SortOrder/SortOrder';
import { NewsBlock } from './components/News/NewsBlock';
import { Header } from './components/Header/Header';
import { TelegramAuthModal } from './components/TelegramAuthModal/TelegramAuthModal';
import { fetchNews } from './api/fetchNews';
import classes from './App.module.scss';
import dayjs from 'dayjs';
import 'dayjs/locale/ru';
import './styles/style.scss';
import customParseFormat from 'dayjs/plugin/customParseFormat';
import { SaveFiltersButton } from './components/Filters/SaveFiltersButton/SaveFiltersButton';

dayjs.locale('ru');
dayjs.extend(customParseFormat);

interface NewsItem {
  id: string;
  title: string;
  summary: string;
  category: string;
  source: string;
  url: string;
  date: string;
}

export interface ITelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  auth_date: number;
  hash: string;
}

declare global {
  interface Window {
    onTelegramAuth: (user: ITelegramUser) => void;
  }
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
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<ITelegramUser | null>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);

  // Проверка авторизации при загрузке
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = () => {
    const savedUser = localStorage.getItem('telegram_user');
    if (savedUser) {
      const userData = JSON.parse(savedUser);
      setIsAuthenticated(true);
      setUser(userData);
    }
  };

  const handleTelegramAuth = () => {
    setShowAuthModal(true);
  };

  const handleAuthSuccess = (userData: ITelegramUser) => {
    // Сохраняем в localStorage
    console.log(userData);
    localStorage.setItem('telegram_user', JSON.stringify(userData));

    setIsAuthenticated(true);
    setUser(userData);
    setShowAuthModal(false);

    console.log('User authenticated with ID:', userData.id);
  };

  const handleLogout = () => {
    localStorage.removeItem('telegram_user');
    setIsAuthenticated(false);
    setUser(null);
  };

  async function getNews(isLoadMore = false) {
    if (loading || (isLoadMore && !hasMore)) return;

    setLoading(true);
    const filters = {
      category: category.length > 0 ? category : null,
      source: source.length > 0 ? source : null,
      search: keyword,
      start_date: startDate || null,
      end_date: endDate || null,
      page: isLoadMore ? page : 1,
      limit: 20,
      sort,
    };
    console.log(JSON.stringify(filters));
    try {
      const newNews = await fetchNews(filters);

      if (newNews.length < 20) {
        setHasMore(false);
      } else {
        setHasMore(true);
      }

      if (isLoadMore) {
        setNews((prev) => [...prev, ...newNews]);
      } else {
        setNews(newNews);
        setPage(1);
        setHasMore(true);
      }
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

  const handleScroll = useCallback(() => {
    if (loading || !hasMore) return;

    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;

    if (documentHeight - (scrollTop + windowHeight) < 200) {
      setPage((prev) => prev + 1);
    }
  }, [loading, hasMore]);

  useEffect(() => {
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [handleScroll]);

  useEffect(() => {
    if (page > 1) {
      getNews(true);
    }
  }, [page]);

  useEffect(() => {
    setPage(1);
  }, [category, source, keyword, startDate, endDate, sort]);

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
      <AppShell header={{ height: 70 }}>
        <AppShell.Header>
          <Header
            onTelegramClick={handleTelegramAuth}
            isAuthenticated={isAuthenticated}
            user={user}
            onLogout={handleLogout}
          />
        </AppShell.Header>

        <AppShell.Main className={classes.main}>
          {/* Модальное окно авторизации */}
          <TelegramAuthModal
            isOpen={showAuthModal}
            onClose={() => setShowAuthModal(false)}
            onAuthSuccess={handleAuthSuccess}
            botUsername="match_hunters_bot"
          />

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
                    <SaveFiltersButton onClick={handleApplyFilters} disabled={loading} />
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

              {loading && (
                <Paper className={classes.loadingState}>
                  <div className={classes.loadingText}>Загрузка новостей...</div>
                </Paper>
              )}

              {news.length === 0 && !loading && (
                <Paper className={classes.emptyState}>
                  <div className={classes.emptyText}>Новости не найдены. Измените параметры фильтрации.</div>
                </Paper>
              )}

              {!hasMore && news.length > 0 && (
                <Paper className={classes.endState}>
                  <div className={classes.endText}>Вы просмотрели все новости</div>
                </Paper>
              )}
            </Stack>
          </section>
        </AppShell.Main>
      </AppShell>
    </MantineProvider>
  );
}
