import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Agriculture,
  Terrain,
  Assessment,
  Warning,
  CheckCircle,
  Refresh,
  Timeline,
} from '@mui/icons-material';
import { DashboardStats, KPI } from '../interfaces';
import apiService from '../services/api';

// Componente para KPI Card
interface KPICardProps {
  kpi: KPI;
}

const KPICard: React.FC<KPICardProps> = ({ kpi }) => {
  const getTrendIcon = () => {
    switch (kpi.tendencia) {
      case 'up':
        return <TrendingUp color="success" />;
      case 'down':
        return <TrendingDown color="error" />;
      default:
        return <Timeline color="info" />;
    }
  };

  const getTrendColor = () => {
    switch (kpi.tendencia) {
      case 'up':
        return 'success.main';
      case 'down':
        return 'error.main';
      default:
        return 'info.main';
    }
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6" component="div" color="text.secondary">
            {kpi.nombre}
          </Typography>
          {getTrendIcon()}
        </Box>
        
        <Typography variant="h3" component="div" sx={{ mb: 1, fontWeight: 600 }}>
          {kpi.valor.toLocaleString()} {kpi.unidad}
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography
            variant="body2"
            sx={{ color: getTrendColor(), fontWeight: 500 }}
          >
            {kpi.cambio_porcentual > 0 ? '+' : ''}{kpi.cambio_porcentual.toFixed(1)}%
          </Typography>
          <Typography variant="body2" color="text.secondary">
            vs mes anterior
          </Typography>
        </Box>
        
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          {kpi.descripcion}
        </Typography>
      </CardContent>
    </Card>
  );
};

// Componente para Alertas
interface AlertItemProps {
  alerta: any;
}

const AlertItem: React.FC<AlertItemProps> = ({ alerta }) => {
  const getIcon = () => {
    switch (alerta.tipo) {
      case 'anomalia':
        return <Warning color="error" />;
      case 'prediccion':
        return <Timeline color="info" />;
      default:
        return <CheckCircle color="success" />;
    }
  };

  const getSeverityColor = () => {
    switch (alerta.severidad) {
      case 'alta':
        return 'error';
      case 'media':
        return 'warning';
      default:
        return 'info';
    }
  };

  return (
    <ListItem>
      <ListItemIcon>
        {getIcon()}
      </ListItemIcon>
      <ListItemText
        primary={alerta.titulo}
        secondary={
          <Box>
            <Typography variant="body2" color="text.secondary">
              {alerta.descripcion}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
              <Chip
                label={alerta.severidad}
                size="small"
                color={getSeverityColor() as any}
                variant="outlined"
              />
              <Typography variant="caption" color="text.secondary">
                {new Date(alerta.fecha).toLocaleDateString()}
              </Typography>
            </Box>
          </Box>
        }
      />
    </ListItem>
  );
};

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [kpis, setKpis] = useState<KPI[]>([]);
  const [alertas, setAlertas] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError('');

      // Cargar datos en paralelo
      const [statsResponse, kpisResponse, alertasResponse] = await Promise.all([
        apiService.getDashboardStats(),
        apiService.getDashboardKPIs(),
        apiService.getDashboardAlertas(),
      ]);

      setStats(statsResponse);
      
      // Validar que kpis sea un array
      const kpisData = Array.isArray(kpisResponse) ? kpisResponse : kpisResponse.results || [];
      setKpis(kpisData);
      
      // Validar que alertas sea un array
      const alertasData = Array.isArray(alertasResponse) ? alertasResponse : alertasResponse.results || [];
      setAlertas(alertasData.slice(0, 10)); // Mostrar solo las primeras 10 alertas
    } catch (err: any) {
      setError(err.message || 'Error al cargar datos del dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  if (loading) {
    return (
      <Box className="loading-spinner">
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Cargando dashboard...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert 
        severity="error" 
        action={
          <IconButton color="inherit" size="small" onClick={loadDashboardData}>
            <Refresh />
          </IconButton>
        }
      >
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      {/* Hero Section with Agricultural Image */}
      <Card sx={{ mb: 4, position: 'relative', overflow: 'hidden' }}>
        <Box
          sx={{
            position: 'relative',
            height: 200,
            background: 'linear-gradient(135deg, #1976d2 0%, #42a5f5 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            px: 4,
            color: 'white',
          }}
        >
          <Box sx={{ flex: 1, zIndex: 2 }}>
            <Typography variant="h3" component="h1" sx={{ fontWeight: 700, mb: 1 }}>
              Sistema de Control Agrícola
            </Typography>
            <Typography variant="h6" sx={{ opacity: 0.9, mb: 2 }}>
              Monitoreo inteligente y análisis de cultivos
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography variant="h5" sx={{ fontWeight: 600 }}>
                Dashboard
              </Typography>
              <Tooltip title="Actualizar datos">
                <IconButton onClick={loadDashboardData} sx={{ color: 'white' }}>
                  <Refresh />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
          <Box
            sx={{
              position: 'absolute',
              right: 20,
              top: '50%',
              transform: 'translateY(-50%)',
              opacity: 0.3,
              zIndex: 1,
            }}
          >
            <img
              src="/agriculture-hero.svg"
              alt="Sistema Agrícola"
              style={{
                width: 300,
                height: 150,
                objectFit: 'contain',
              }}
            />
          </Box>
        </Box>
      </Card>

      {/* KPIs principales */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {kpis.map((kpi, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <KPICard kpi={kpi} />
          </Grid>
        ))}
      </Grid>

      {/* Estadísticas generales */}
      {stats && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Resumen General
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Agriculture sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                      <Typography variant="h4" sx={{ fontWeight: 600 }}>
                        {stats.total_cultivos}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Cultivos
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Terrain sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
                      <Typography variant="h4" sx={{ fontWeight: 600 }}>
                        {stats.parcelas_activas}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Parcelas Activas
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Assessment sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
                      <Typography variant="h4" sx={{ fontWeight: 600 }}>
                        {stats.total_registros_produccion}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Registros
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Warning sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
                      <Typography variant="h4" sx={{ fontWeight: 600 }}>
                        {stats.anomalias_detectadas}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Anomalías
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Métricas de Producción
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Producción Total
                  </Typography>
                  <Typography variant="h5" sx={{ fontWeight: 600 }}>
                    {stats.produccion_total_kg.toLocaleString()} kg
                  </Typography>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Rendimiento Promedio
                  </Typography>
                  <Typography variant="h5" sx={{ fontWeight: 600 }}>
                    {stats.rendimiento_promedio.toFixed(1)} kg/ha
                  </Typography>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Área Cultivada
                  </Typography>
                  <Typography variant="h5" sx={{ fontWeight: 600 }}>
                    {stats.area_cultivada_hectareas.toFixed(1)} ha
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Eficiencia de Parcelas
                  </Typography>
                  <Typography variant="h5" sx={{ fontWeight: 600 }}>
                    {((stats.area_cultivada_hectareas / stats.area_total_hectareas) * 100).toFixed(1)}%
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Alertas y notificaciones */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Alertas Recientes
              </Typography>
              {alertas.length > 0 ? (
                <List>
                  {alertas.map((alerta, index) => (
                    <AlertItem key={index} alerta={alerta} />
                  ))}
                </List>
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <CheckCircle sx={{ fontSize: 48, color: 'success.main', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary">
                    No hay alertas pendientes
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Todo está funcionando correctamente
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
