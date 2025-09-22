import React from 'react';
import {
  Popover,
  Box,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Divider,
  Button,
  Chip,
  Badge,
} from '@mui/material';
import {
  Warning,
  Info,
  CheckCircle,
  Error,
  Close,
  MarkEmailRead,
  Delete,
  Agriculture,
  TrendingUp,
  Assessment,
} from '@mui/icons-material';
import { useNotifications, Notification } from '../../contexts/NotificationContext';

interface NotificationPanelProps {
  anchorEl: HTMLElement | null;
  open: boolean;
  onClose: () => void;
}

const NotificationPanel: React.FC<NotificationPanelProps> = ({
  anchorEl,
  open,
  onClose,
}) => {
  const {
    notifications,
    unreadCount,
    markAsRead,
    markAllAsRead,
    deleteNotification,
  } = useNotifications();

  const getIcon = (type: Notification['type']) => {
    switch (type) {
      case 'warning':
        return <Warning color="warning" />;
      case 'error':
        return <Error color="error" />;
      case 'success':
        return <CheckCircle color="success" />;
      default:
        return <Info color="info" />;
    }
  };

  const getCategoryIcon = (category: Notification['category']) => {
    switch (category) {
      case 'production':
        return <Agriculture fontSize="small" />;
      case 'analysis':
        return <Assessment fontSize="small" />;
      case 'system':
        return <TrendingUp fontSize="small" />;
      default:
        return <Info fontSize="small" />;
    }
  };

  const formatTime = (timestamp: Date) => {
    const now = new Date();
    const diff = now.getTime() - timestamp.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

    if (hours > 0) {
      return `hace ${hours}h`;
    } else if (minutes > 0) {
      return `hace ${minutes} minutos`;
    } else {
      return 'ahora';
    }
  };


  return (
    <Popover
      open={open}
      anchorEl={anchorEl}
      onClose={onClose}
      anchorOrigin={{
        vertical: 'bottom',
        horizontal: 'right',
      }}
      transformOrigin={{
        vertical: 'top',
        horizontal: 'right',
      }}
      PaperProps={{
        sx: {
          width: 400,
          maxHeight: 600,
          mt: 1,
        },
      }}
    >
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">
            Notificaciones
            {unreadCount > 0 && (
              <Badge badgeContent={unreadCount} color="error" sx={{ ml: 1 }} />
            )}
          </Typography>
          <IconButton size="small" onClick={onClose}>
            <Close />
          </IconButton>
        </Box>
        {unreadCount > 0 && (
          <Button
            size="small"
            startIcon={<MarkEmailRead />}
            onClick={markAllAsRead}
            sx={{ mt: 1 }}
          >
            Marcar todas como leídas
          </Button>
        )}
      </Box>

      <List sx={{ p: 0, maxHeight: 350, overflow: 'auto' }}>
        {notifications.length === 0 ? (
          <ListItem>
            <ListItemText
              primary="No hay notificaciones"
              secondary="Todas las notificaciones aparecerán aquí"
              sx={{ textAlign: 'center' }}
            />
          </ListItem>
        ) : (
          notifications.map((notification, index) => (
            <React.Fragment key={notification.id}>
              <ListItem
                sx={{
                  backgroundColor: notification.read ? 'transparent' : 'action.hover',
                  '&:hover': { backgroundColor: 'action.selected' },
                }}
              >
                <ListItemIcon>
                  {getIcon(notification.type)}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: notification.read ? 400 : 600 }}>
                        {notification.title}
                      </Typography>
                      <Chip
                        icon={getCategoryIcon(notification.category)}
                        label={notification.category}
                        size="small"
                        variant="outlined"
                        sx={{ height: 20, fontSize: '0.7rem' }}
                      />
                    </Box>
                  }
                  secondary={
                    <React.Fragment>
                      <Typography variant="body2" color="text.secondary" component="span" sx={{ display: 'block', mb: 0.5 }}>
                        {notification.message}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" component="span">
                        {formatTime(notification.timestamp)}
                      </Typography>
                    </React.Fragment>
                  }
                />
                <ListItemSecondaryAction>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                    {!notification.read && (
                      <IconButton
                        size="small"
                        onClick={() => markAsRead(notification.id)}
                        title="Marcar como leída"
                      >
                        <MarkEmailRead fontSize="small" />
                      </IconButton>
                    )}
                    <IconButton
                      size="small"
                      onClick={() => deleteNotification(notification.id)}
                      title="Eliminar notificación"
                    >
                      <Delete fontSize="small" />
                    </IconButton>
                  </Box>
                </ListItemSecondaryAction>
              </ListItem>
              {index < notifications.length - 1 && <Divider />}
            </React.Fragment>
          ))
        )}
      </List>

      {notifications.length > 0 && (
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider', textAlign: 'center' }}>
          <Button size="small" color="primary">
            Ver todas las notificaciones
          </Button>
        </Box>
      )}
    </Popover>
  );
};

export default NotificationPanel;
