// Manejador de errores global para suprimir warnings de extensiones de Chrome
export const setupErrorHandler = () => {
  // Suprimir errores de extensiones de Chrome en desarrollo
  if (import.meta.env.DEV) {
    const originalError = console.error;
    console.error = (...args: any[]) => {
      const message = args[0];
      
      // Filtrar errores conocidos de extensiones de Chrome y API
      if (
        typeof message === 'string' && (
          message.includes('chrome-extension://') ||
          message.includes('Extension context invalidated') ||
          message.includes('Could not establish connection') ||
          message.includes('react-devtools') ||
          message.includes('ERR_FAILED') ||
          message.includes('net::ERR_FAILED') ||
          message.includes('404 (Not Found)') ||
          message.includes('Request failed with status code 404') ||
          message.includes('nullish-content') ||
          message.includes('RETRIES_FAILED') ||
          message.includes('invalid') ||
          message.includes('HEAD') ||
          message.includes('GET') ||
          message.includes('guillbot-content') ||
          message.includes('/invalid/') ||
          message.includes('Failed to load resource') ||
          (message.includes(':29') && message.includes('FAILED')) ||
          (message.includes('HEAD') && message.includes('chrome-extension://'))
        )
      ) {
        return; // No mostrar estos errores
      }
      
      // También filtrar objetos de error que contengan URLs de extensiones
      if (args.length > 0 && args[0] && typeof args[0] === 'object') {
        const errorObj = args[0];
        if (errorObj.config && errorObj.config.url && 
            errorObj.config.url.includes('chrome-extension://')) {
          return;
        }
        if (errorObj.message && typeof errorObj.message === 'string' &&
            errorObj.message.includes('chrome-extension://')) {
          return;
        }
      }
      
      // Mostrar otros errores normalmente
      originalError.apply(console, args);
    };

    // Suprimir warnings específicos de React Router
    const originalWarn = console.warn;
    console.warn = (...args: any[]) => {
      const message = args[0];
      
      if (
        typeof message === 'string' && (
          message.includes('React Router Future Flag Warning') ||
          message.includes('Relative route resolution within Splat routes')
        )
      ) {
        return; // No mostrar estos warnings
      }
      
      originalWarn.apply(console, args);
    };
  }
};

// Función para manejar errores no capturados
export const handleUnhandledErrors = () => {
  window.addEventListener('error', (event) => {
    // Filtrar errores de extensiones
    if (
      event.filename?.includes('chrome-extension://') ||
      event.message?.includes('chrome-extension://') ||
      event.message?.includes('Script error')
    ) {
      event.preventDefault();
      return false;
    }
  });

  window.addEventListener('unhandledrejection', (event) => {
    // Filtrar promesas rechazadas de extensiones
    if (
      event.reason?.message?.includes('chrome-extension://') ||
      event.reason?.stack?.includes('chrome-extension://')
    ) {
      event.preventDefault();
      return false;
    }
  });
};
