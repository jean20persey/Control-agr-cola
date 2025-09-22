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
import RegistroProduccionModal from '../components/Modals/RegistroProduccionModal';
import PrediccionModal from '../components/Modals/PrediccionModal';

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
      style={{ 
        flex: 1, 
        display: value === index ? 'flex' : 'none', 
        flexDirection: 'column',
        minHeight: 0
      }}
      {...other}
    >
      {value === index && (
        <Box sx={{ 
          p: 1, 
          flex: 1, 
          display: 'flex', 
          flexDirection: 'column',
          minHeight: 0,
          overflow: 'hidden'
        }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `simple-tab-${index}`,
    'aria-controls': `simple-tabpanel-${index}`,
  };
}

const Produccion: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [registros, setRegistros] = useState<RegistroProduccion[]>([]);
  const [predicciones, setPredicciones] = useState<PrediccionCosecha[]>([]);
  const [anomalias, setAnomalias] = useState<RegistroProduccion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [modalOpen, setModalOpen] = useState(false);
  const [prediccionModalOpen, setPrediccionModalOpen] = useState(false);

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

      console.log('Registros de producción cargados:', JSON.stringify(registrosData, null, 2));

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

  const handleOpenModal = () => {
    console.log('Abriendo modal de nuevo registro de producción');
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
  };

  const handleSaveRegistro = (savedRegistro: RegistroProduccion) => {
    setRegistros(prev => [...prev, savedRegistro]);
    loadData(); // Recargar todos los datos para actualizar estadísticas
  };

  const handleOpenPrediccionModal = () => {
    console.log('Abriendo modal de nueva predicción');
    setPrediccionModalOpen(true);
  };

  const handleClosePrediccionModal = () => {
    setPrediccionModalOpen(false);
  };

  const handleSavePrediccion = (savedPrediccion: PrediccionCosecha) => {
    setPredicciones(prev => [...prev, savedPrediccion]);
    loadData(); // Recargar todos los datos para actualizar estadísticas
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
      field: 'parcela_codigo',
      headerName: 'Parcela',
      flex: 1,
      minWidth: 120,
      renderCell: (params) => (
        <Typography variant="body2" fontWeight={500}>
          {params.value || params.row.parcela_info?.codigo || `Parcela ${params.row.parcela}`}
        </Typography>
      ),
    },
    {
      field: 'cultivo_nombre',
      headerName: 'Cultivo',
      flex: 0.8,
      minWidth: 100,
      renderCell: (params) => (
        <Typography variant="body2">
          {params.value || params.row.cultivo_info?.nombre || `Cultivo ${params.row.cultivo}`}
        </Typography>
      ),
    },
    {
      field: 'fecha_registro',
      headerName: 'Fecha',
      flex: 0.7,
      minWidth: 90,
      renderCell: (params) => (
        <Typography variant="body2">
          {new Date(params.value).toLocaleDateString()}
        </Typography>
      ),
    },
    {
      field: 'temporada',
      headerName: 'Temporada',
      flex: 0.5,
      minWidth: 70,
    },
    {
      field: 'cantidad_kg',
      headerName: 'Cantidad',
      flex: 0.8,
      minWidth: 90,
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
      flex: 1,
      minWidth: 110,
      type: 'number',
      renderCell: (params) => (
        <Typography variant="body2" fontWeight={500}>
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
    <Box sx={{ 
      height: 'calc(100vh - 80px)', 
      display: 'flex', 
      flexDirection: 'column', 
      overflow: 'hidden',
      p: 2
    }}>
      {/* Header */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        mb: 2,
        flexShrink: 0
      }}>
        <Typography variant="h4" sx={{ fontWeight: 600 }}>
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
            onClick={handleOpenModal}
          >
            Nuevo Registro
          </Button>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2, flexShrink: 0 }}>
          {error}
        </Alert>
      )}

      {/* Tarjetas de estadísticas */}
      <Grid container spacing={2} sx={{ mb: 2, flexShrink: 0 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100px' }}>
            <CardContent sx={{ textAlign: 'center', p: 1.5, '&:last-child': { pb: 1.5 } }}>
              <Assessment sx={{ fontSize: 32, color: 'primary.main', mb: 0.5 }} />
              <Typography variant="h5" sx={{ fontWeight: 600, mb: 0.5 }}>
                {Array.isArray(registros) ? registros.length : 0}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Total Registros
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100px' }}>
            <CardContent sx={{ textAlign: 'center', p: 1.5, '&:last-child': { pb: 1.5 } }}>
              <Warning sx={{ fontSize: 32, color: 'error.main', mb: 0.5 }} />
              <Typography variant="h5" sx={{ fontWeight: 600, color: 'error.main', mb: 0.5 }}>
                {Array.isArray(anomalias) ? anomalias.length : 0}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Anomalías Detectadas
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100px' }}>
            <CardContent sx={{ textAlign: 'center', p: 1.5, '&:last-child': { pb: 1.5 } }}>
              <Science sx={{ fontSize: 32, color: 'info.main', mb: 0.5 }} />
              <Typography variant="h5" sx={{ fontWeight: 600, color: 'info.main', mb: 0.5 }}>
                {Array.isArray(predicciones) ? predicciones.length : 0}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Predicciones Activas
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100px' }}>
            <CardContent sx={{ textAlign: 'center', p: 1.5, '&:last-child': { pb: 1.5 } }}>
              <TrendingUp sx={{ fontSize: 32, color: 'success.main', mb: 0.5 }} />
              <Typography variant="h5" sx={{ fontWeight: 600, color: 'success.main', mb: 0.5 }}>
                {Array.isArray(registros) && registros.length > 0 ? (registros.reduce((acc, r) => acc + r.eficiencia_rendimiento, 0) / registros.length).toFixed(1) : 0}%
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Eficiencia Promedio
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs de contenido */}
      <Card sx={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', flexShrink: 0 }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="tabs de producción">
            <Tab
              icon={<Assessment />}
              label="REGISTROS"
              {...a11yProps(0)}
              iconPosition="start"
            />
            <Tab
              icon={<Science />}
              label="PREDICCIONES"
              {...a11yProps(1)}
              iconPosition="start"
            />
            <Tab
              icon={<Warning />}
              label="ANOMALÍAS"
              {...a11yProps(2)}
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
            disableColumnMenu
            sx={{
              flex: 1,
              width: '100%',
              minHeight: 0,
              '& .MuiDataGrid-root': {
                overflowX: 'hidden',
                height: '100%',
              },
              '& .MuiDataGrid-main': {
                height: '100%',
              },
              '& .MuiDataGrid-virtualScroller': {
                overflowX: 'hidden',
              },
              '& .MuiDataGrid-cell': {
                borderBottom: '1px solid rgba(0, 0, 0, 0.08)',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              },
              '& .MuiDataGrid-columnHeaders': {
                backgroundColor: '#f8f9fa',
                borderBottom: '2px solid rgba(0, 0, 0, 0.1)',
                fontWeight: 600,
              },
              '& .MuiDataGrid-row:hover': {
                backgroundColor: 'rgba(0, 0, 0, 0.04)',
              },
              '& .MuiDataGrid-footerContainer': {
                borderTop: '1px solid rgba(0, 0, 0, 0.12)',
              },
            }}
          />
        </TabPanel>

        {/* Tab Panel - Predicciones */}
        <TabPanel value={tabValue} index={1}>
          <Box sx={{ mb: 1, display: 'flex', justifyContent: 'flex-end', flexShrink: 0 }}>
            <Button
              variant="outlined"
              startIcon={<Science />}
              onClick={handleOpenPrediccionModal}
              size="small"
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
            sx={{
              flex: 1,
              minHeight: 0,
              '& .MuiDataGrid-root': {
                height: '100%',
              },
              '& .MuiDataGrid-main': {
                height: '100%',
              },
            }}
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
              sx={{
                flex: 1,
                minHeight: 0,
                '& .MuiDataGrid-root': {
                  height: '100%',
                },
                '& .MuiDataGrid-main': {
                  height: '100%',
                },
              }}
            />
          ) : (
            <Box sx={{ 
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              textAlign: 'center'
            }}>
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

      {/* Modal funcional para nuevo registro */}
      <RegistroProduccionModal
        open={modalOpen}
        onClose={handleCloseModal}
        onSave={handleSaveRegistro}
      />

      {/* Modal funcional para nueva predicción */}
      <PrediccionModal
        open={prediccionModalOpen}
        onClose={handleClosePrediccionModal}
        onSave={handleSavePrediccion}
      />
    </Box>
  );
};

export default Produccion;
