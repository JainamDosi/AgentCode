import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { Provider } from './components/ui/provider.jsx'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

import App from './App.jsx'
import './index.css'
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Provider>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
    </Provider>
  </StrictMode>
)
