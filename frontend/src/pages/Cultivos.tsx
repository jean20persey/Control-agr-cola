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
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Refresh,
  Agriculture,
  ThermostatAuto,
  WaterDrop,
  TrendingUp,
  Category,
} from '@mui/icons-material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { Cultivo } from '../interfaces';
import apiService from '../services/api';
import CultivoModal from '../components/Modals/CultivoModal';

const Cultivos: React.FC = () => {
  const [cultivos, setCultivos] = useState<Cultivo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedCultivo, setSelectedCultivo] = useState<Cultivo | null>(null);

  const loadCultivos = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await apiService.getCultivos();
      // Si la respuesta es paginada, extraer los resultados
      const cultivosData = Array.isArray(response) ? response : response.results || [];
      setCultivos(cultivosData);
    } catch (err: any) {
      setError(err.message || 'Error al cargar cultivos');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCultivos();
  }, []);

  const handleOpenModal = (cultivo?: Cultivo) => {
    setSelectedCultivo(cultivo || null);
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setSelectedCultivo(null);
  };

  const handleSaveCultivo = (savedCultivo: Cultivo) => {
    if (selectedCultivo?.id) {
      // Actualizar cultivo existente
      setCultivos(prev => prev.map(c => c.id === savedCultivo.id ? savedCultivo : c));
    } else {
      // Agregar nuevo cultivo
      setCultivos(prev => [...prev, savedCultivo]);
    }
  };

  const handleDeleteCultivo = async (id: number) => {
    if (window.confirm('¿Estás seguro de que deseas eliminar este cultivo?')) {
      try {
        await apiService.deleteCultivo(id);
        setCultivos(prev => prev.filter(c => c.id !== id));
      } catch (err: any) {
        setError(err.message || 'Error al eliminar cultivo');
      }
    }
  };

  const columns: GridColDef[] = [
    {
      field: 'nombre',
      headerName: 'Nombre',
      width: 150,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Agriculture color="primary" fontSize="small" />
          <Typography variant="body2" fontWeight={500}>
            {params.value}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'variedad',
      headerName: 'Variedad',
      width: 150,
    },
    {
      field: 'tipo',
      headerName: 'Tipo',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value}
          size="small"
          color="primary"
          variant="outlined"
        />
      ),
    },
    {
      field: 'ciclo_dias',
      headerName: 'Ciclo (días)',
      width: 100,
      type: 'number',
    },
    {
      field: 'rendimiento_esperado',
      headerName: 'Rendimiento (kg/ha)',
      width: 150,
      type: 'number',
      renderCell: (params) => (
        <Typography variant="body2">
          {params.value?.toLocaleString()} kg/ha
        </Typography>
      ),
    },
    {
      field: 'rango_temperatura',
      headerName: 'Temperatura',
      width: 120,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <ThermostatAuto fontSize="small" color="info" />
          <Typography variant="caption">
            {params.value || 'N/A'}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'rango_ph',
      headerName: 'pH',
      width: 100,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <WaterDrop fontSize="small" color="info" />
          <Typography variant="caption">
            {params.value || 'N/A'}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'activo',
      headerName: 'Estado',
      width: 100,
      renderCell: (params) => (
        <Chip
          label={params.value ? 'Activo' : 'Inactivo'}
          size="small"
          color={params.value ? 'success' : 'default'}
        />
      ),
    },
    {
      field: 'actions',
      headerName: 'Acciones',
      width: 120,
      sortable: false,
      renderCell: (params) => (
        <Box>
          <Tooltip title="Editar">
            <IconButton 
              size="small" 
              color="primary"
              onClick={() => handleOpenModal(params.row)}
            >
              <Edit fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Eliminar">
            <IconButton 
              size="small" 
              color="error"
              onClick={() => handleDeleteCultivo(params.row.id)}
            >
              <Delete fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      ),
    },
  ];

  if (loading) {
    return (
      <Box className="loading-spinner">
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Cargando cultivos...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
          Gestión de Cultivos
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Actualizar">
            <IconButton onClick={loadCultivos} color="primary">
              <Refresh />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => handleOpenModal()}
          >
            Nuevo Cultivo
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
              <Agriculture sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
              <Typography variant="h4" sx={{ fontWeight: 600 }}>
                {Array.isArray(cultivos) ? cultivos.length : 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Cultivos
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Chip 
                icon={<Agriculture />} 
                label="Activos" 
                color="success" 
                sx={{ mb: 1 }} 
              />
              <Typography variant="h4" sx={{ fontWeight: 600, color: 'success.main' }}>
                {Array.isArray(cultivos) ? cultivos.filter(c => c.activo).length : 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Cultivos Activos
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Category sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
              <Typography variant="h4" sx={{ fontWeight: 600, color: 'info.main' }}>
                {Array.isArray(cultivos) ? new Set(cultivos.map(c => c.tipo)).size : 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Tipos Diferentes
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <TrendingUp sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
              <Typography variant="h4" sx={{ fontWeight: 600, color: 'warning.main' }}>
                {Array.isArray(cultivos) && cultivos.length > 0 ? Math.round(cultivos.reduce((acc, c) => acc + c.rendimiento_esperado, 0) / cultivos.length).toLocaleString() : 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Rendimiento Promedio (kg/ha)
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabla de cultivos */}
      <Card>
        <CardContent>
          <DataGrid
            rows={cultivos}
            columns={columns}
            initialState={{
              pagination: {
                paginationModel: { page: 0, pageSize: 10 },
              },
            }}
            pageSizeOptions={[5, 10, 25]}
            checkboxSelection
            disableRowSelectionOnClick
            autoHeight
            sx={{
              '& .MuiDataGrid-cell': {
                borderBottom: '1px solid rgba(0, 0, 0, 0.08)',
              },
              '& .MuiDataGrid-columnHeaders': {
                backgroundColor: '#f8f9fa',
                borderBottom: '2px solid rgba(0, 0, 0, 0.1)',
              },
            }}
          />
        </CardContent>
      </Card>

      {/* Modal para crear/editar cultivo */}
      <CultivoModal
        open={modalOpen}
        onClose={handleCloseModal}
        onSave={handleSaveCultivo}
        cultivo={selectedCultivo}
      />
    </Box>
  );
};

export default Cultivos;
