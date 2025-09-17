import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Typography,
  Chip,
} from '@mui/material';
import {
  Dashboard,
  Agriculture,
  Terrain,
  Assessment,
  Analytics,
  TrendingUp,
  Science,
  BarChart,
  Nature,
} from '@mui/icons-material';

interface SidebarProps {
  onItemClick?: () => void;
}

interface MenuItem {
  text: string;
  icon: React.ReactElement;
  path: string;
  badge?: string;
  description?: string;
}

const menuItems: MenuItem[] = [
  {
    text: 'Dashboard',
    icon: <Dashboard />,
    path: '/dashboard',
    description: 'Panel principal con métricas'
  },
  {
    text: 'Cultivos',
    icon: <Agriculture />,
    path: '/cultivos',
    description: 'Gestión de cultivos y variedades'
  },
  {
    text: 'Parcelas',
    icon: <Terrain />,
    path: '/parcelas',
    description: 'Control de parcelas agrícolas'
  },
  {
    text: 'Producción',
    icon: <Assessment />,
    path: '/produccion',
    description: 'Registro de producción'
  },
  {
    text: 'Análisis',
    icon: <Analytics />,
    path: '/analisis',
    description: 'Análisis estadístico avanzado'
  },
];

const Sidebar: React.FC<SidebarProps> = ({ onItemClick }) => {
  const location = useLocation();
  const navigate = useNavigate();

  const handleItemClick = (path: string) => {
    navigate(path);
    if (onItemClick) {
      onItemClick();
    }
  };

  const isSelected = (path: string) => {
    return location.pathname === path;
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header del sidebar */}
      <Box
        sx={{
          p: 2,
          display: 'flex',
          alignItems: 'center',
          minHeight: 64,
          borderBottom: '1px solid rgba(0, 0, 0, 0.08)',
        }}
      >
        <Nature sx={{ color: 'primary.main', mr: 1, fontSize: 28 }} />
        <Box>
          <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>
            Control Agrícola
          </Typography>
          <Typography variant="caption" color="text.secondary">
            v1.0.0
          </Typography>
        </Box>
      </Box>

      {/* Menú principal */}
      <List sx={{ flexGrow: 1, pt: 1 }}>
        {menuItems.map((item) => (
          <ListItem key={item.path} disablePadding sx={{ mb: 0.5 }}>
            <ListItemButton
              selected={isSelected(item.path)}
              onClick={() => handleItemClick(item.path)}
              sx={{
                mx: 1,
                borderRadius: 2,
                '&.Mui-selected': {
                  backgroundColor: 'primary.main',
                  color: 'white',
                  '&:hover': {
                    backgroundColor: 'primary.dark',
                  },
                  '& .MuiListItemIcon-root': {
                    color: 'white',
                  },
                },
                '&:hover': {
                  backgroundColor: 'action.hover',
                },
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: 40,
                  color: isSelected(item.path) ? 'white' : 'primary.main',
                }}
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.text}
                secondary={item.description}
                primaryTypographyProps={{
                  fontSize: '0.875rem',
                  fontWeight: isSelected(item.path) ? 600 : 500,
                }}
                secondaryTypographyProps={{
                  fontSize: '0.75rem',
                  color: isSelected(item.path) ? 'rgba(255,255,255,0.7)' : 'text.secondary',
                }}
              />
              {item.badge && (
                <Chip
                  label={item.badge}
                  size="small"
                  color="secondary"
                  sx={{ ml: 1, height: 20, fontSize: '0.75rem' }}
                />
              )}
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      <Divider />

      {/* Sección de estadísticas rápidas */}
      <Box sx={{ p: 2 }}>
        <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
          Acceso Rápido
        </Typography>
        
        <List dense>
          <ListItem disablePadding>
            <ListItemButton
              onClick={() => handleItemClick('/dashboard')}
              sx={{ borderRadius: 1, py: 0.5 }}
            >
              <ListItemIcon sx={{ minWidth: 32 }}>
                <TrendingUp fontSize="small" color="success" />
              </ListItemIcon>
              <ListItemText
                primary="Métricas"
                primaryTypographyProps={{ fontSize: '0.75rem' }}
              />
            </ListItemButton>
          </ListItem>

          <ListItem disablePadding>
            <ListItemButton
              onClick={() => handleItemClick('/produccion')}
              sx={{ borderRadius: 1, py: 0.5 }}
            >
              <ListItemIcon sx={{ minWidth: 32 }}>
                <Science fontSize="small" color="info" />
              </ListItemIcon>
              <ListItemText
                primary="Anomalías"
                primaryTypographyProps={{ fontSize: '0.75rem' }}
              />
            </ListItemButton>
          </ListItem>

          <ListItem disablePadding>
            <ListItemButton
              onClick={() => handleItemClick('/analisis')}
              sx={{ borderRadius: 1, py: 0.5 }}
            >
              <ListItemIcon sx={{ minWidth: 32 }}>
                <BarChart fontSize="small" color="warning" />
              </ListItemIcon>
              <ListItemText
                primary="Reportes"
                primaryTypographyProps={{ fontSize: '0.75rem' }}
              />
            </ListItemButton>
          </ListItem>
        </List>
      </Box>

      {/* Footer del sidebar */}
      <Box
        sx={{
          p: 2,
          borderTop: '1px solid rgba(0, 0, 0, 0.08)',
          backgroundColor: 'background.paper',
        }}
      >
        <Typography variant="caption" color="text.secondary" align="center" display="block">
          Sistema de Gestión Agrícola
        </Typography>
        <Typography variant="caption" color="text.secondary" align="center" display="block">
          © 2024 Control Agrícola
        </Typography>
      </Box>
    </Box>
  );
};

export default Sidebar;
