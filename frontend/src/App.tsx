import { useEffect, useState, useCallback, useRef, useMemo } from 'react';
import { MantineProvider, Group, Stack, Paper, AppShell, Affix, Transition, Button } from '@mantine/core';
import { useForm } from '@mantine/form';
import { CategoryPicker } from './components/Filters/CategoryPicker/CategoryPicker';
import { SourcePicker } from './components/Filters/SourcePicker/SourcePicker';
import { DateRangePicker } from './components/Filters/DateRangePicker/DateRangePicker';
import { KeywordSearch } from './components/Filters/KeywordSearch/KeywordSearch';
import { ApplyFiltersButton } from './components/Filters/ApplyFiltersButton/ApplyFiltersButton';
import { SortOrder } from './components/Filters/SortOrder/SortOrder';
import { NewsBlock } from './components/News/NewsBlock';
import { Header } from './components/Header/Header';
import { TelegramAuthModal } from './components/TelegramAuthModal/TelegramAuthModal';
import classes from './App.module.scss';
import dayjs from 'dayjs';
import 'dayjs/locale/ru';
import './styles/style.scss';
import customParseFormat from 'dayjs/plugin/customParseFormat';
import { SaveFiltersButton } from './components/Filters/SaveFiltersButton/SaveFiltersButton';
import { LoadFiltersButton } from './components/Filters/LoadFiltersButton/LoadFiltersButton';
import { RecommendedNewsButton } from './components/Filters/RecommendedNewsButton/RecommendedNewsButton';
import { useNews, NewsFilters } from './hooks/useNews';
import { useWindowScroll } from '@mantine/hooks';
import { IconArrowUp } from '@tabler/icons-react';
import { ClearFiltersButton } from './components/Filters/ClearFiltersButton/ClearFiltersButton';

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
  const { fetchNews, loading, error: newsError } = useNews();

  const [news, setNews] = useState<NewsItem[]>([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<ITelegramUser | null>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isRecommendedMode, setIsRecommendedMode] = useState(false);
  const [scroll, scrollTo] = useWindowScroll();
  const [showScrollToTop, setShowScrollToTop] = useState(false);
  const isLoadingRef = useRef(false);

  const form = useForm({
    initialValues: {
      category: [] as string[],
      source: [] as string[],
      search: '',
      start_date: '',
      end_date: '',
      sort: 'desc',
    },
  });

  const savedValuesRef = useRef(form.values);

  useEffect(() => {
    setShowScrollToTop(scroll.y > 400);
  }, [scroll.y]);

  const scrollToTop = useCallback(() => {
    scrollTo({ y: 0 });
  }, [scrollTo]);

  // ✅ Авторизация Telegram
  useEffect(() => {
    const savedUser = localStorage.getItem('telegram_user');
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setIsAuthenticated(true);
        setUser(userData);
      } catch {
        localStorage.removeItem('telegram_user');
      }
    }
  }, []);

  const handleTelegramClick = useCallback(() => setShowAuthModal(true), []);
  const handleAuthSuccess = useCallback((userData: ITelegramUser) => {
    localStorage.setItem('telegram_user', JSON.stringify(userData));
    setUser(userData);
    setIsAuthenticated(true);
    setShowAuthModal(false);
  }, []);
  const handleLogout = useCallback(() => {
    localStorage.removeItem('telegram_user');
    setIsAuthenticated(false);
    setUser(null);
  }, []);
  const handleCloseAuthModal = useCallback(() => setShowAuthModal(false), []);

  const getNews = useCallback(
    async (isLoadMore = false, currentPage = page) => {
      if (isLoadingRef.current || (isLoadMore && !hasMore)) return;
      isLoadingRef.current = true;

      const { category, source, search, start_date, end_date, sort } = form.values;

      const filters: NewsFilters = {
        category: category.length ? category : null,
        source: source.length ? source : null,
        search: search || null,
        start_date: start_date || null,
        end_date: end_date || null,
        page: isLoadMore ? currentPage : 1,
        limit: 20,
        sort,
      };

      const newNews = await fetchNews(filters);
      setHasMore(newNews.length >= 20);
      setNews((prev) => (isLoadMore ? [...prev, ...newNews] : newNews));
      if (!isLoadMore) setPage(1);
      isLoadingRef.current = false;
    },
    [form.values, fetchNews, page, hasMore],
  );

  const handleApplyFilters = useCallback(() => {
    setPage(1);
    getNews(false, 1);
  }, [getNews]);

  const handleRecommendedNews = useCallback(() => {
    setIsRecommendedMode((prev) => !prev);
  }, []);

  const handleScroll = useCallback(() => {
    if (loading || !hasMore || isLoadingRef.current) return;

    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;

    if (documentHeight - (scrollTop + windowHeight) < 200) {
      setPage((prev) => {
        const next = prev + 1;
        getNews(true, next);
        return next;
      });
    }
  }, [loading, hasMore, getNews]);

  const handleClearFilters = useCallback(() => {
    form.setValues({
      category: [],
      source: [],
      search: '',
      start_date: '',
      end_date: '',
    });
    savedValuesRef.current = {
      ...savedValuesRef.current,
      category: [],
      source: [],
      search: '',
      start_date: '',
      end_date: '',
    };
    setPage(1);
    getNews(false, 1);
  }, [form, getNews]);

  const isFiltersEmpty = useMemo(() => {
    const { category, source, search, start_date, end_date } = form.values;
    return category.length === 0 && source.length === 0 && search === '' && start_date === '' && end_date === '';
  }, [form.values]);

  useEffect(() => {
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [handleScroll]);

  useEffect(() => {
    getNews(false, 1);
  }, []);

  return (
    <MantineProvider
      theme={{
        fontFamily: 'Montserrat, sans-serif',
        headings: { fontFamily: 'Montserrat, sans-serif' },
      }}
    >
      <AppShell header={{ height: 70 }}>
        <AppShell.Header>
          <Header
            onTelegramClick={handleTelegramClick}
            isAuthenticated={isAuthenticated}
            user={user}
            onLogout={handleLogout}
          />
        </AppShell.Header>

        <AppShell.Main className={classes.main}>
          {/* Наверх */}
          <Affix position={{ bottom: 20, right: 20 }}>
            <Transition transition="slide-up" mounted={showScrollToTop}>
              {(transitionStyles) => (
                <Button
                  leftSection={<IconArrowUp size={16} />}
                  style={transitionStyles}
                  onClick={scrollToTop}
                  className={classes.scrollToTopButton}
                  size="md"
                >
                  Наверх
                </Button>
              )}
            </Transition>
          </Affix>

          {/* Telegram Auth */}
          <TelegramAuthModal
            isOpen={showAuthModal}
            onClose={handleCloseAuthModal}
            onAuthSuccess={handleAuthSuccess}
            botUsername="match_hunters_bot"
          />

          {/* Форма фильтров */}
          <section className={classes.section}>
            <Paper className={classes.paper}>
              <form onSubmit={form.onSubmit(handleApplyFilters)}>
                <Stack>
                  <Group className={classes.filterRow}>
                    <div className={classes.filterItem}>
                      <CategoryPicker
                        value={form.values.category}
                        onChange={(v) => form.setFieldValue('category', v)}
                        disabled={isRecommendedMode}
                        savedValue={savedValuesRef.current.category}
                      />
                    </div>
                    <div className={classes.filterItem}>
                      <SourcePicker
                        value={form.values.source}
                        onChange={(v) => form.setFieldValue('source', v)}
                        disabled={isRecommendedMode}
                        savedValue={savedValuesRef.current.source}
                      />
                    </div>
                    <div className={classes.filterItem}>
                      <KeywordSearch
                        value={form.values.search}
                        onChange={(v) => form.setFieldValue('search', v)}
                        disabled={isRecommendedMode}
                        savedValue={savedValuesRef.current.search}
                      />
                    </div>
                  </Group>

                  <Group className={classes.filterRow}>
                    <div className={classes.dateContainer}>
                      <DateRangePicker
                        startDate={form.values.start_date}
                        endDate={form.values.end_date}
                        savedStartDate={savedValuesRef.current.start_date}
                        savedEndDate={savedValuesRef.current.end_date}
                        onStartChange={(v) => form.setFieldValue('start_date', v)}
                        onEndChange={(v) => form.setFieldValue('end_date', v)}
                        disabled={isRecommendedMode}
                      />
                    </div>
                    <div className={classes.sortOrderWrapper}>
                      <SortOrder
                        value={form.values.sort}
                        onChange={(v) => form.setFieldValue('sort', v)}
                        disabled={isRecommendedMode}
                      />
                    </div>
                    <div className={classes.buttonContainer}>
                      <ClearFiltersButton onClear={handleClearFilters} disabled={isFiltersEmpty || isRecommendedMode} />
                      <ApplyFiltersButton onClick={handleApplyFilters} disabled={loading || isRecommendedMode} />
                    </div>
                  </Group>

                  <Group className={classes.filterRow}>
                    <Group>
                      <SaveFiltersButton
                        disabled={loading || isRecommendedMode}
                        filters={form.values}
                        userId={123456}
                        onSuccess={() => {}}
                        onError={(e) => console.error(e)}
                      />
                      <LoadFiltersButton
                        disabled={loading || isRecommendedMode}
                        userId={875430}
                        onFiltersLoad={form.setValues}
                        onError={(e) => console.error(e)}
                      />
                    </Group>
                    <RecommendedNewsButton
                      onClick={handleRecommendedNews}
                      disabled={loading}
                      active={isRecommendedMode}
                    />
                  </Group>
                </Stack>
              </form>
            </Paper>

            {/* Список новостей */}
            <Stack className={classes.newsList}>
              {newsError && (
                <Paper className={classes.emptyState}>
                  <div className={classes.emptyText}>Ошибка загрузки новостей</div>
                </Paper>
              )}
              {news.map((item) => (
                <NewsBlock
                  key={item.id}
                  name={item.title}
                  description={item.summary}
                  category={item.category}
                  source={item.source}
                  date={item.date}
                  url={item.url}
                />
              ))}
              {/* {loading && (
                <Paper className={classes.loadingState}>
                  <div className={classes.loadingText}>Загрузка новостей...</div>
                </Paper>
              )} */}
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
