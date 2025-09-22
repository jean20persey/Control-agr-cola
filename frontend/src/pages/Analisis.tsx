import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  Chip,
  Alert,
  CircularProgress,
  Tab,
  Tabs,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
} from '@mui/material';
import {
  Analytics,
  Science,
  Timeline,
  BarChart,
  CompareArrows,
  Assessment,
  Functions,
  Close,
  Info,
} from '@mui/icons-material';
import apiService from '../services/api';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`analisis-tabpanel-${index}`}
      aria-labelledby={`analisis-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const Analisis: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [estadisticasGenerales, setEstadisticasGenerales] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedAnalysis, setSelectedAnalysis] = useState<any>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');
      
      const estadisticas = await apiService.getEstadisticasGenerales();
      setEstadisticasGenerales(estadisticas);
    } catch (err: any) {
      setError(err.message || 'Error al cargar datos de análisis');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleOpenAnalysis = (analysisOption: any) => {
    console.log('Abriendo análisis:', analysisOption.title);
    setSelectedAnalysis(analysisOption);
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setSelectedAnalysis(null);
  };

  const analisisOptions = [
    {
      title: 'Comparación de Variedades',
      description: 'Análisis estadístico para comparar rendimiento entre diferentes variedades de cultivos',
      icon: <CompareArrows color="primary" />,
      action: 'Comparar Variedades',
      features: ['Prueba T de Student', 'Mann-Whitney U', 'ANOVA', 'Kruskal-Wallis']
    },
    {
      title: 'Clasificación por Rendimiento',
      description: 'Algoritmos de clasificación para ordenar parcelas según su rendimiento',
      icon: <BarChart color="success" />,
      action: 'Clasificar Parcelas',
      features: ['Percentiles', 'K-Means', 'Cuartiles', 'Z-Score']
    },
    {
      title: 'Análisis de Series Temporales',
      description: 'Análisis de tendencias y patrones temporales en la producción',
      icon: <Timeline color="info" />,
      action: 'Analizar Series',
      features: ['Detección de tendencias', 'Valores atípicos', 'Estacionalidad', 'Predicciones']
    },
    {
      title: 'Modelos Predictivos',
      description: 'Modelos de machine learning para predecir rendimientos futuros',
      icon: <Science color="warning" />,
      action: 'Crear Modelo',
      features: ['Regresión Lineal', 'Random Forest', 'XGBoost', 'Validación cruzada']
    }
  ];

  if (loading) {
    return (
      <Box className="loading-spinner">
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Cargando análisis estadístico...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
          Análisis Estadístico
        </Typography>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Estadísticas generales */}
      {estadisticasGenerales && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Assessment sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                <Typography variant="h4" sx={{ fontWeight: 600 }}>
                  {estadisticasGenerales.total_registros}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Registros
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" sx={{ fontWeight: 600, color: 'success.main' }}>
                  {estadisticasGenerales.rendimiento_promedio.toFixed(1)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Rendimiento Promedio (kg/ha)
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" sx={{ fontWeight: 600, color: 'warning.main' }}>
                  {estadisticasGenerales.porcentaje_anomalias.toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Tasa de Anomalías
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" sx={{ fontWeight: 600, color: 'info.main' }}>
                  {estadisticasGenerales.top_cultivos_rendimiento.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Cultivos Analizados
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tabs */}
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="tabs de análisis">
            <Tab 
              label="Herramientas de Análisis" 
              icon={<Analytics />} 
              iconPosition="start"
            />
            <Tab 
              label="Resultados Guardados" 
              icon={<Functions />} 
              iconPosition="start"
            />
          </Tabs>
        </Box>

        {/* Tab Panel - Herramientas */}
        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            {analisisOptions.map((option, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      {option.icon}
                      <Typography variant="h6" sx={{ ml: 1, fontWeight: 600 }}>
                        {option.title}
                      </Typography>
                    </Box>
                    
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {option.description}
                    </Typography>
                    
                    <Typography variant="subtitle2" sx={{ mb: 1 }}>
                      Características:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
                      {option.features.map((feature, idx) => (
                        <Chip
                          key={idx}
                          label={feature}
                          size="small"
                          variant="outlined"
                          color="primary"
                        />
                      ))}
                    </Box>
                  </CardContent>
                  
                  <Box sx={{ p: 2, pt: 0 }}>
                    <Button
                      fullWidth
                      variant="contained"
                      onClick={() => handleOpenAnalysis(option)}
                    >
                      {option.action}
                    </Button>
                  </Box>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        {/* Tab Panel - Resultados */}
        <TabPanel value={tabValue} index={1}>
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Functions sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              Historial de Análisis
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Aquí aparecerán los análisis estadísticos guardados
            </Typography>
            <Button variant="outlined" disabled>
              Próximamente
            </Button>
          </Box>
        </TabPanel>
      </Card>

      {/* Modal de Análisis */}
      <Dialog open={modalOpen} onClose={handleCloseModal} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {selectedAnalysis?.icon}
              {selectedAnalysis?.title}
            </Box>
            <IconButton onClick={handleCloseModal}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        
        <DialogContent>
          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="body2">
              <strong>🚧 Funcionalidad en Desarrollo</strong><br/>
              Esta herramienta de análisis estadístico está siendo desarrollada y estará disponible próximamente.
            </Typography>
          </Alert>

          {selectedAnalysis && (
            <Box>
              <Typography variant="body1" sx={{ mb: 2 }}>
                {selectedAnalysis.description}
              </Typography>

              <Typography variant="h6" sx={{ mb: 2 }}>
                📊 Características Incluidas:
              </Typography>
              
              <Grid container spacing={1} sx={{ mb: 3 }}>
                {selectedAnalysis.features?.map((feature: string, idx: number) => (
                  <Grid item key={idx}>
                    <Chip
                      label={feature}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  </Grid>
                ))}
              </Grid>

              <Alert severity="warning">
                <Typography variant="body2">
                  <strong>📋 Requisitos para usar esta herramienta:</strong><br/>
                  • Al menos 10 registros de producción históricos<br/>
                  • Múltiples parcelas con diferentes cultivos<br/>
                  • Datos de al menos 2 temporadas completas<br/>
                  • Información completa de rendimientos y condiciones ambientales
                </Typography>
              </Alert>

              <Box sx={{ mt: 3, p: 2, bgcolor: 'background.paper', borderRadius: 1, border: 1, borderColor: 'divider' }}>
                <Typography variant="subtitle2" gutterBottom>
                  💡 Mientras tanto, puedes:
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemIcon>
                      <Info color="primary" />
                    </ListItemIcon>
                    <ListItemText primary="Crear más registros de producción" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <Info color="primary" />
                    </ListItemIcon>
                    <ListItemText primary="Registrar datos de múltiples parcelas" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <Info color="primary" />
                    </ListItemIcon>
                    <ListItemText primary="Documentar condiciones ambientales" />
                  </ListItem>
                </List>
              </Box>
            </Box>
          )}
        </DialogContent>

        <DialogActions>
          <Button onClick={handleCloseModal} color="primary">
            Entendido
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Analisis;
