import { StrictMode } from 'react';
import ReactDOM from 'react-dom/client';
import { OpenAPI } from './client';
import App from './App';
import '@mantine/core/styles.css';
import { MantineProvider } from '@mantine/core';

OpenAPI.BASE = import.meta.env.VITE_API_URL;
OpenAPI.TOKEN = async () => {
  return localStorage.getItem('access_token') || '';
};

// const handleApiError = (error: Error) => {
//   if (error instanceof ApiError && [401, 403].includes(error.status)) {
//     localStorage.removeItem('access_token');
//     window.location.href = '/login';
//   }
// };

ReactDOM.createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <MantineProvider>
      <App />
    </MantineProvider>
  </StrictMode>,
);
