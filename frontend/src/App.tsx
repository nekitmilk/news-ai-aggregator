import { useEffect, useState, useCallback, useRef, useMemo } from 'react';
import { MantineProvider, Group, Stack, Paper, AppShell, Affix, Transition, Button } from '@mantine/core';
import { useForm } from '@mantine/form';
import { useWindowScroll } from '@mantine/hooks';
import { IconArrowUp } from '@tabler/icons-react';
import dayjs from 'dayjs';
import 'dayjs/locale/ru';
import customParseFormat from 'dayjs/plugin/customParseFormat';

import { CategoryPicker } from './components/Filters/CategoryPicker/CategoryPicker';
import { SourcePicker } from './components/Filters/SourcePicker/SourcePicker';
import { DateRangePicker } from './components/Filters/DateRangePicker/DateRangePicker';
import { KeywordSearch } from './components/Filters/KeywordSearch/KeywordSearch';
import { ApplyFiltersButton } from './components/Filters/ApplyFiltersButton/ApplyFiltersButton';
import { SortOrder } from './components/Filters/SortOrder/SortOrder';
import { NewsBlock } from './components/News/NewsBlock';
import { Header } from './components/Header/Header';
import { TelegramAuthModal } from './components/TelegramAuthModal/TelegramAuthModal';
import { SaveFiltersButton } from './components/Filters/SaveFiltersButton/SaveFiltersButton';
import { LoadFiltersButton } from './components/Filters/LoadFiltersButton/LoadFiltersButton';
import { RecommendedNewsButton } from './components/Filters/RecommendedNewsButton/RecommendedNewsButton';
import { ClearFiltersButton } from './components/Filters/ClearFiltersButton/ClearFiltersButton';

import { useNews, NewsFilters } from './hooks/useNews';
import { ITelegramUser } from './types/telegram';

import classes from './App.module.scss';
import './styles/style.scss';

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

const INITIAL_PAGE = 1;
const NEWS_LIMIT = 20;
const SCROLL_THRESHOLD = 400;
const INFINITE_SCROLL_OFFSET = 200;

export default function App() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [page, setPage] = useState(INITIAL_PAGE);
  const [hasMore, setHasMore] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<ITelegramUser | null>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isRecommendedMode, setIsRecommendedMode] = useState(false);
  const [filtersApplied, setFiltersApplied] = useState(true);

  const { fetchNews, fetchRecommendedNews, loading, error: newsError } = useNews();
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

  const updateSavedValues = useCallback(() => {
    savedValuesRef.current = { ...form.values };
  }, [form.values]);

  useEffect(() => {
    setShowScrollToTop(scroll.y > SCROLL_THRESHOLD);
  }, [scroll.y]);

  const scrollToTop = useCallback(() => {
    scrollTo({ y: 0 });
  }, [scrollTo]);

  useEffect(() => {
    const savedUser = localStorage.getItem('telegram_user');
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser) as ITelegramUser;
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
    setIsRecommendedMode(false);
  }, []);

  const handleCloseAuthModal = useCallback(() => setShowAuthModal(false), []);

  const getNewsWithFilters = useCallback(
    async (filters: Partial<NewsFilters>, isLoadMore = false, currentPage = page, needSavedUpd = false) => {
      if (isLoadingRef.current || (isLoadMore && !hasMore)) return;

      isLoadingRef.current = true;

      try {
        const newsFilters: NewsFilters = {
          category: filters.category ?? (form.values.category.length ? form.values.category : null),
          source: filters.source ?? (form.values.source.length ? form.values.source : null),
          search: filters.search ?? (form.values.search || null),
          start_date: filters.start_date ?? (form.values.start_date || null),
          end_date: filters.end_date ?? (form.values.end_date || null),
          page: isLoadMore ? currentPage : INITIAL_PAGE,
          limit: NEWS_LIMIT,
          sort: filters.sort ?? form.values.sort,
        };
        const newNews = await fetchNews(newsFilters);
        setHasMore(newNews.length >= NEWS_LIMIT);
        setNews((prev) => (isLoadMore ? [...prev, ...newNews] : newNews));
        if (!isLoadMore) {
          setPage(INITIAL_PAGE);
        }

        if (needSavedUpd) updateSavedValues();
      } finally {
        isLoadingRef.current = false;
      }
    },
    [form.values, fetchNews, page, hasMore],
  );

  const getNews = useCallback(
    async (isLoadMore = false, currentPage = page, needSavedUpd = false) => {
      await getNewsWithFilters({}, isLoadMore, currentPage, needSavedUpd);
    },
    [getNewsWithFilters, page],
  );
  const userId = useMemo(() => user?.id || 2345, [user]);

  const handleRecommendedNews = useCallback(async () => {
    const newIsRecommendedMode = !isRecommendedMode;
    setIsRecommendedMode(newIsRecommendedMode);

    if (newIsRecommendedMode) {
      isLoadingRef.current = true;
      setPage(INITIAL_PAGE);

      const recommendedNews = await fetchRecommendedNews(userId, INITIAL_PAGE, NEWS_LIMIT);
      setNews(recommendedNews);
      setHasMore(recommendedNews.length >= NEWS_LIMIT);
      isLoadingRef.current = false;
    } else {
      setPage(INITIAL_PAGE);
      getNews(false, INITIAL_PAGE);
    }
  }, [isRecommendedMode, userId, fetchRecommendedNews, getNews]);

  const handleClearFilters = useCallback(() => {
    const clearedValues = {
      category: [],
      source: [],
      search: '',
      start_date: '',
      end_date: '',
    };

    form.setValues(clearedValues);
    setFiltersApplied(false);
  }, [form]);

  const handleScroll = useCallback(() => {
    if (isLoadingRef.current || !hasMore) return;

    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    if (documentHeight - (scrollTop + windowHeight) < INFINITE_SCROLL_OFFSET) {
      const nextPage = page + 1;
      setPage(nextPage);

      if (isRecommendedMode && userId) {
        isLoadingRef.current = true;
        fetchRecommendedNews(userId, nextPage, NEWS_LIMIT)
          .then((newNews) => {
            setNews((prevNews) => [...prevNews, ...newNews]);
            setHasMore(newNews.length >= NEWS_LIMIT);
            isLoadingRef.current = false;
          })
          .catch(() => {
            isLoadingRef.current = false;
          });
      } else {
        getNewsWithFilters({}, true, nextPage);
      }
    }
  }, [page, hasMore, isRecommendedMode, userId, fetchRecommendedNews, getNewsWithFilters]);

  const isFiltersEmpty = useMemo(() => {
    const { category, source, search, start_date, end_date } = form.values;
    return category.length === 0 && source.length === 0 && search === '' && start_date === '' && end_date === '';
  }, [form.values]);

  const hasFiltersChanged = useMemo(() => {
    if (!filtersApplied) return true;

    const currentValues = form.values;
    const savedValues = savedValuesRef.current;

    return (
      JSON.stringify(currentValues.category) !== JSON.stringify(savedValues.category) ||
      JSON.stringify(currentValues.source) !== JSON.stringify(savedValues.source) ||
      currentValues.search !== savedValues.search ||
      currentValues.start_date !== savedValues.start_date ||
      currentValues.end_date !== savedValues.end_date ||
      currentValues.sort !== savedValues.sort
    );
  }, [form.values, filtersApplied]);

  const handleApplyFilters = useCallback(() => {
    if (!hasFiltersChanged) {
      return;
    }

    setPage(INITIAL_PAGE);
    getNews(false, INITIAL_PAGE, true);
    setFiltersApplied(true);
  }, [getNews, hasFiltersChanged]);

  useEffect(() => {
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [handleScroll]);

  useEffect(() => {
    getNews(false, INITIAL_PAGE);
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

          <TelegramAuthModal
            isOpen={showAuthModal}
            onClose={handleCloseAuthModal}
            onAuthSuccess={handleAuthSuccess}
            botUsername="match_hunters_bot"
          />

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
                        disabled={isFiltersEmpty || loading || isRecommendedMode || !hasFiltersChanged}
                        filters={form.values}
                        userId={userId}
                        onSuccess={() => {}}
                        onError={(e) => console.error(e)}
                      />
                      <LoadFiltersButton
                        disabled={loading || isRecommendedMode}
                        userId={userId}
                        onFiltersLoad={(filters) => {
                          const cleanedFilters = Object.fromEntries(
                            Object.entries(filters).filter(
                              ([_, value]) =>
                                value !== '' &&
                                value !== null &&
                                value !== undefined &&
                                !(Array.isArray(value) && value.length === 0),
                            ),
                          );

                          form.setValues(cleanedFilters);
                          updateSavedValues();
                          setFiltersApplied(false);
                        }}
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

            <Stack className={classes.newsList}>
              {newsError && (
                <Paper className={classes.emptyState}>
                  <div className={classes.emptyText}>Ошибка загрузки новостей</div>
                </Paper>
              )}

              {news.map((item) => (
                <NewsBlock
                  key={item.id}
                  id={item.id}
                  name={item.title}
                  description={item.summary}
                  category={item.category}
                  source={item.source}
                  date={item.date}
                  url={item.url}
                  userId={userId}
                />
              ))}
              {news.length === 0 && !loading && !newsError && (
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
