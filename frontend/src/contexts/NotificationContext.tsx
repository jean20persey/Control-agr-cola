import React, { createContext, useContext, useState, ReactNode } from 'react';

export interface Notification {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  category: 'system' | 'production' | 'alert' | 'analysis';
}

interface NotificationContextType {
  notifications: Notification[];
  unreadCount: number;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  deleteNotification: (id: string) => void;
  clearAllNotifications: () => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};

interface NotificationProviderProps {
  children: ReactNode;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([
    {
      id: '1',
      type: 'warning',
      title: 'Anomalía en Producción',
      message: 'Se detectó una disminución del 15% en el rendimiento de la parcela Norte-A2',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 horas atrás
      read: false,
      category: 'production',
    },
    {
      id: '2',
      type: 'info',
      title: 'Nuevo Análisis Disponible',
      message: 'El análisis predictivo del mes de septiembre está listo para revisar',
      timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000), // 4 horas atrás
      read: false,
      category: 'analysis',
    },
    {
      id: '3',
      type: 'success',
      title: 'Cosecha Completada',
      message: 'La cosecha de la parcela Sur-B1 se completó exitosamente. Rendimiento: 2.3 ton/ha',
      timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000), // 6 horas atrás
      read: true,
      category: 'production',
    },
    {
      id: '4',
      type: 'error',
      title: 'Fallo en Sensor',
      message: 'El sensor de humedad #SH-045 no responde. Verificar conexión.',
      timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000), // 8 horas atrás
      read: false,
      category: 'system',
    },
  ]);

  const unreadCount = notifications.filter(n => !n.read).length;

  const addNotification = (notificationData: Omit<Notification, 'id' | 'timestamp'>) => {
    const newNotification: Notification = {
      ...notificationData,
      id: Date.now().toString(),
      timestamp: new Date(),
    };
    setNotifications(prev => [newNotification, ...prev]);
  };

  const markAsRead = (id: string) => {
    setNotifications(prev =>
      prev.map(notif =>
        notif.id === id ? { ...notif, read: true } : notif
      )
    );
  };

  const markAllAsRead = () => {
    setNotifications(prev =>
      prev.map(notif => ({ ...notif, read: true }))
    );
  };

  const deleteNotification = (id: string) => {
    setNotifications(prev => prev.filter(notif => notif.id !== id));
  };

  const clearAllNotifications = () => {
    setNotifications([]);
  };

  const value: NotificationContextType = {
    notifications,
    unreadCount,
    addNotification,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    clearAllNotifications,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};

export default NotificationContext;
