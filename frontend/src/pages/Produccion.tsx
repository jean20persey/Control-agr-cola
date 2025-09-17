import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  Chip,
  IconButton,
  Tooltip,
  Alert,
  CircularProgress,
  Tab,
  Tabs,
} from '@mui/material';
import {
  Add,
  Refresh,
  Assessment,
  Warning,
  Science,
  TrendingUp,
} from '@mui/icons-material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { RegistroProduccion, PrediccionCosecha } from '../interfaces';
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
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
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

const Produccion: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [registros, setRegistros] = useState<RegistroProduccion[]>([]);
  const [predicciones, setPredicciones] = useState<PrediccionCosecha[]>([]);
  const [anomalias, setAnomalias] = useState<RegistroProduccion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');
      
      const [registrosResponse, prediccionesResponse, anomaliasResponse] = await Promise.all([
        apiService.getRegistrosProduccion(),
        apiService.getPredicciones(),
        apiService.getAnomalias(),
      ]);

      // Si las respuestas son paginadas, extraer los resultados
      const registrosData = Array.isArray(registrosResponse) ? registrosResponse : registrosResponse.results || [];
      const prediccionesData = Array.isArray(prediccionesResponse) ? prediccionesResponse : prediccionesResponse.results || [];
      const anomaliasData = Array.isArray(anomaliasResponse) ? anomaliasResponse : anomaliasResponse.results || [];

      setRegistros(registrosData);
      setPredicciones(prediccionesData);
      setAnomalias(anomaliasData);
    } catch (err: any) {
      setError(err.message || 'Error al cargar datos de producción');
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

  const getCalidadColor = (calidad: string) => {
    switch (calidad) {
      case 'A':
        return 'success';
      case 'B':
        return 'info';
      case 'C':
        return 'warning';
      case 'D':
        return 'error';
      default:
        return 'default';
    }
  };

  const registrosColumns: GridColDef[] = [
    {
      field: 'parcela_info',
      headerName: 'Parcela',
      width: 120,
      renderCell: (params) => (
        <Typography variant="body2" fontWeight={500}>
          {params.value?.codigo}
        </Typography>
      ),
    },
    {
      field: 'cultivo_info',
      headerName: 'Cultivo',
      width: 150,
      renderCell: (params) => (
        <Typography variant="body2">
          {params.value?.nombre}
        </Typography>
      ),
    },
    {
      field: 'fecha_registro',
      headerName: 'Fecha',
      width: 120,
      renderCell: (params) => (
        <Typography variant="body2">
          {new Date(params.value).toLocaleDateString()}
        </Typography>
      ),
    },
    {
      field: 'temporada',
      headerName: 'Temporada',
      width: 100,
    },
    {
      field: 'cantidad_kg',
      headerName: 'Cantidad (kg)',
      width: 120,
      type: 'number',
      renderCell: (params) => (
        <Typography variant="body2">
          {params.value?.toLocaleString()} kg
        </Typography>
      ),
    },
    {
      field: 'rendimiento_hectarea',
      headerName: 'Rendimiento',
      width: 120,
      type: 'number',
      renderCell: (params) => (
        <Typography variant="body2">
          {params.value?.toFixed(1)} kg/ha
        </Typography>
      ),
    },
    {
      field: 'calidad',
      headerName: 'Calidad',
      width: 100,
      renderCell: (params) => (
        params.value ? (
          <Chip
            label={`Calidad ${params.value}`}
            size="small"
            color={getCalidadColor(params.value) as any}
          />
        ) : (
          <Typography variant="body2" color="text.secondary">
            N/A
          </Typography>
        )
      ),
    },
    {
      field: 'anomalia_detectada',
      headerName: 'Anomalía',
      width: 100,
      renderCell: (params) => (
        params.value ? (
          <Warning color="error" fontSize="small" />
        ) : (
          <Typography variant="body2" color="text.secondary">
            Normal
          </Typography>
        )
      ),
    },
    {
      field: 'eficiencia_rendimiento',
      headerName: 'Eficiencia',
      width: 100,
      renderCell: (params) => (
        <Typography 
          variant="body2" 
          color={params.value >= 100 ? 'success.main' : params.value >= 80 ? 'warning.main' : 'error.main'}
        >
          {params.value?.toFixed(1)}%
        </Typography>
      ),
    },
  ];

  const prediccionesColumns: GridColDef[] = [
    {
      field: 'parcela_info',
      headerName: 'Parcela',
      width: 120,
      renderCell: (params) => (
        <Typography variant="body2" fontWeight={500}>
          {params.value?.codigo}
        </Typography>
      ),
    },
    {
      field: 'cultivo_info',
      headerName: 'Cultivo',
      width: 150,
      renderCell: (params) => (
        <Typography variant="body2">
          {params.value?.nombre}
        </Typography>
      ),
    },
    {
      field: 'temporada_objetivo',
      headerName: 'Temporada',
      width: 120,
    },
    {
      field: 'rendimiento_predicho',
      headerName: 'Predicción',
      width: 120,
      renderCell: (params) => (
        <Typography variant="body2" fontWeight={500}>
          {params.value?.toFixed(1)} kg/ha
        </Typography>
      ),
    },
    {
      field: 'confianza_prediccion',
      headerName: 'Confianza',
      width: 100,
      renderCell: (params) => (
        <Typography 
          variant="body2"
          color={params.value >= 0.8 ? 'success.main' : params.value >= 0.6 ? 'warning.main' : 'error.main'}
        >
          {(params.value * 100).toFixed(1)}%
        </Typography>
      ),
    },
    {
      field: 'modelo_utilizado',
      headerName: 'Modelo',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value}
          size="small"
          color="info"
          variant="outlined"
        />
      ),
    },
    {
      field: 'fecha_prediccion',
      headerName: 'Fecha',
      width: 120,
      renderCell: (params) => (
        <Typography variant="body2">
          {new Date(params.value).toLocaleDateString()}
        </Typography>
      ),
    },
    {
      field: 'precision_prediccion',
      headerName: 'Precisión',
      width: 100,
      renderCell: (params) => (
        params.value ? (
          <Typography variant="body2" color="success.main">
            {params.value.toFixed(1)}%
          </Typography>
        ) : (
          <Typography variant="body2" color="text.secondary">
            Pendiente
          </Typography>
        )
      ),
    },
  ];

  if (loading) {
    return (
      <Box className="loading-spinner">
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Cargando datos de producción...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
          Gestión de Producción
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Actualizar">
            <IconButton onClick={loadData} color="primary">
              <Refresh />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => {/* TODO: Abrir modal de crear registro */}}
          >
            Nuevo Registro
          </Button>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Estadísticas rápidas */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Assessment sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
              <Typography variant="h4" sx={{ fontWeight: 600 }}>
                {Array.isArray(registros) ? registros.length : 0}
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
              <Warning sx={{ fontSize: 40, color: 'error.main', mb: 1 }} />
              <Typography variant="h4" sx={{ fontWeight: 600, color: 'error.main' }}>
                {Array.isArray(anomalias) ? anomalias.length : 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Anomalías Detectadas
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Science sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
              <Typography variant="h4" sx={{ fontWeight: 600, color: 'info.main' }}>
                {Array.isArray(predicciones) ? predicciones.length : 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Predicciones Activas
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <TrendingUp sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
              <Typography variant="h4" sx={{ fontWeight: 600, color: 'success.main' }}>
                {Array.isArray(registros) && registros.length > 0 ? (registros.reduce((acc, r) => acc + r.eficiencia_rendimiento, 0) / registros.length).toFixed(1) : 0}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Eficiencia Promedio
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="tabs de producción">
            <Tab 
              label={`Registros (${Array.isArray(registros) ? registros.length : 0})`} 
              icon={<Assessment />} 
              iconPosition="start"
            />
            <Tab 
              label={`Predicciones (${Array.isArray(predicciones) ? predicciones.length : 0})`} 
              icon={<Science />} 
              iconPosition="start"
            />
            <Tab 
              label={`Anomalías (${Array.isArray(anomalias) ? anomalias.length : 0})`} 
              icon={<Warning />} 
              iconPosition="start"
            />
          </Tabs>
        </Box>

        {/* Tab Panel - Registros */}
        <TabPanel value={tabValue} index={0}>
          <DataGrid
            rows={registros}
            columns={registrosColumns}
            initialState={{
              pagination: {
                paginationModel: { page: 0, pageSize: 10 },
              },
            }}
            pageSizeOptions={[5, 10, 25]}
            checkboxSelection
            disableRowSelectionOnClick
            autoHeight
          />
        </TabPanel>

        {/* Tab Panel - Predicciones */}
        <TabPanel value={tabValue} index={1}>
          <Box sx={{ mb: 2, display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="outlined"
              startIcon={<Science />}
              onClick={() => {/* TODO: Abrir modal de crear predicción */}}
            >
              Nueva Predicción
            </Button>
          </Box>
          <DataGrid
            rows={predicciones}
            columns={prediccionesColumns}
            initialState={{
              pagination: {
                paginationModel: { page: 0, pageSize: 10 },
              },
            }}
            pageSizeOptions={[5, 10, 25]}
            checkboxSelection
            disableRowSelectionOnClick
            autoHeight
          />
        </TabPanel>

        {/* Tab Panel - Anomalías */}
        <TabPanel value={tabValue} index={2}>
          {Array.isArray(anomalias) && anomalias.length > 0 ? (
            <DataGrid
              rows={anomalias}
              columns={registrosColumns}
              initialState={{
                pagination: {
                  paginationModel: { page: 0, pageSize: 10 },
                },
              }}
              pageSizeOptions={[5, 10, 25]}
              disableRowSelectionOnClick
              autoHeight
            />
          ) : (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Assessment sx={{ fontSize: 48, color: 'success.main', mb: 2 }} />
              <Typography variant="h6" color="text.secondary">
                No hay anomalías detectadas
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Todos los registros están dentro de los parámetros normales
              </Typography>
            </Box>
          )}
        </TabPanel>
      </Card>
    </Box>
  );
};

export default Produccion;
