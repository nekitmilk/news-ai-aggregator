import { StrictMode } from 'react';
import ReactDOM from 'react-dom/client';
import { OpenAPI } from './client';
import App from './App';
import '@mantine/core/styles.css';
import { MantineProvider } from '@mantine/core';

OpenAPI.BASE = import.meta.env.VITE_API_URL;

ReactDOM.createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <MantineProvider>
      <App />
    </MantineProvider>
  </StrictMode>,
);
