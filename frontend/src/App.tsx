import { useEffect, useState, useCallback, useRef } from 'react';
import { MantineProvider, Group, Stack, Paper, AppShell, Affix, Transition, Button } from '@mantine/core';
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
  const [hasMore, setHasMore] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<ITelegramUser | null>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isRecommendedMode, setIsRecommendedMode] = useState(false);
  const [scroll, scrollTo] = useWindowScroll();
  const [showScrollToTop, setShowScrollToTop] = useState(false);

  // Эффект для показа/скрытия кнопки скролла вверх
  useEffect(() => {
    setShowScrollToTop(scroll.y > 400); // Показывать кнопку когда скролл больше 400px
  }, [scroll.y]);

  // Функция для скролла вверх
  const scrollToTop = useCallback(() => {
    scrollTo({ y: 0 });
  }, [scrollTo]);
  const { fetchNews, loading, error: newsError } = useNews();

  // Используем useRef для отслеживания состояния загрузки
  const isLoadingRef = useRef(false);

  // Проверка авторизации при загрузке
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = useCallback(() => {
    const savedUser = localStorage.getItem('telegram_user');
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setIsAuthenticated(true);
        setUser(userData);
      } catch (error) {
        console.error('Error parsing saved user data:', error);
        localStorage.removeItem('telegram_user');
      }
    }
  }, []);

  const handleTelegramClick = useCallback(() => {
    setShowAuthModal(true);
  }, []);

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

  const handleCloseAuthModal = useCallback(() => {
    setShowAuthModal(false);
  }, []);

  const handleLoadSavedFilters = useCallback(() => {
    const savedFilters = localStorage.getItem('saved_filters');
    if (savedFilters) {
      try {
        const filters = JSON.parse(savedFilters);
        setCategory(filters.category || []);
        setSource(filters.source || []);
        setKeyword(filters.keyword || '');
        setStartDate(filters.startDate || '');
        setEndDate(filters.endDate || '');
        setSort(filters.sort || 'desc');
      } catch (error) {
        console.error('Error loading saved filters:', error);
      }
    }
  }, []);

  const handleRecommendedNews = useCallback(() => {
    setIsRecommendedMode((prev) => !prev);
  }, []);

  // Вынесем getNews из зависимостей
  const getNews = useCallback(
    async (isLoadMore = false, currentPage = page) => {
      if (isLoadingRef.current || (isLoadMore && !hasMore)) return;

      isLoadingRef.current = true;

      const filters: NewsFilters = {
        category: category.length > 0 ? category : null,
        source: source.length > 0 ? source : null,
        search: keyword,
        start_date: startDate || null,
        end_date: endDate || null,
        page: isLoadMore ? currentPage : 1,
        limit: 20,
        sort,
      };

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
          if (!isLoadMore) {
            setPage(1);
          }
          setHasMore(true);
        }
      } catch (error) {
        console.error('Error fetching news:', error);
      } finally {
        isLoadingRef.current = false;
      }
    },
    [category, source, keyword, startDate, endDate, sort, hasMore, fetchNews],
  );

  const handleApplyFilters = useCallback(() => {
    setPage(1);
    getNews(false, 1);
  }, [getNews]);

  const handleScroll = useCallback(() => {
    if (loading || !hasMore || isLoadingRef.current) return;

    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;

    if (documentHeight - (scrollTop + windowHeight) < 200) {
      setPage((prev) => {
        const nextPage = prev + 1;
        getNews(true, nextPage);
        return nextPage;
      });
    }
  }, [loading, hasMore, getNews]);

  useEffect(() => {
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [handleScroll]);

  useEffect(() => {
    setPage(1);
  }, [category, source, keyword, startDate, endDate, sort]);

  useEffect(() => {
    getNews(false, 1);
  }, []);

  const handleSaveSuccess = useCallback(() => {}, []);

  const handleSaveError = useCallback((error: string) => {
    console.error('Ошибка сохранения фильтров:', error);
  }, []);

  const handleFiltersLoad = useCallback((loadedFilters: any) => {
    setCategory(loadedFilters.category || []);
    setSource(loadedFilters.source || []);
    setKeyword(loadedFilters.keyword || '');
    setStartDate(loadedFilters.startDate || '');
    setEndDate(loadedFilters.endDate || '');
    setSort(loadedFilters.sort || 'desc');
  }, []);

  const handleLoadError = useCallback((error: string) => {
    console.error('Ошибка загрузки фильтров:', error);
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
              <Stack>
                <Group className={classes.filterRow}>
                  <div className={classes.filterItem}>
                    <CategoryPicker value={category} onChange={setCategory} disabled={isRecommendedMode} />
                  </div>
                  <div className={classes.filterItem}>
                    <SourcePicker value={source} onChange={setSource} disabled={isRecommendedMode} />
                  </div>
                  <div className={classes.filterItem}>
                    <KeywordSearch value={keyword} onChange={setKeyword} disabled={isRecommendedMode} />
                  </div>
                </Group>

                <Group className={classes.filterRow}>
                  <div className={classes.dateContainer}>
                    <DateRangePicker
                      startDate={startDate}
                      endDate={endDate}
                      onStartChange={setStartDate}
                      onEndChange={setEndDate}
                      disabled={isRecommendedMode}
                    />
                  </div>
                  <div className={classes.sortOrderWrapper}>
                    <SortOrder value={sort} onChange={setSort} disabled={isRecommendedMode} />
                  </div>
                  <div className={classes.buttonContainer}>
                    <ApplyFiltersButton onClick={handleApplyFilters} disabled={loading || isRecommendedMode} />
                  </div>
                </Group>

                {isAuthenticated && (
                  <Group className={classes.filterRow}>
                    <div className={classes.filterActionsContainer}>
                      <Group>
                        <SaveFiltersButton
                          onClick={handleApplyFilters}
                          disabled={loading || isRecommendedMode}
                          filters={{
                            category,
                            source,
                            keyword,
                            startDate,
                            endDate,
                            sort,
                          }}
                          userId={user?.id || null}
                          onSuccess={handleSaveSuccess}
                          onError={handleSaveError}
                        />
                        <LoadFiltersButton
                          onClick={handleLoadSavedFilters}
                          disabled={loading || isRecommendedMode}
                          userId={user?.id || null}
                          onFiltersLoad={handleFiltersLoad}
                          onError={handleLoadError}
                        />
                      </Group>
                      <RecommendedNewsButton
                        onClick={handleRecommendedNews}
                        disabled={loading}
                        active={isRecommendedMode}
                      />
                    </div>
                  </Group>
                )}
              </Stack>
            </Paper>

            <Stack className={classes.newsList}>
              {newsError && (
                <Paper className={classes.errorState}>
                  <div className={classes.errorText}>Ошибка загрузки новостей</div>
                </Paper>
              )}

              {news.map((item, idx) => (
                <NewsBlock
                  key={`${item.id}-${idx}`}
                  name={item.title}
                  description={item.summary}
                  category={item.category}
                  source={item.source}
                  date={item.date}
                  url={item.url}
                />
              ))}

              {loading && (
                <Paper className={classes.loadingState}>
                  <div className={classes.loadingText}>Загрузка новостей...</div>
                </Paper>
              )}

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
