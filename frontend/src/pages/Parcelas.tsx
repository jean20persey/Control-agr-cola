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
  Terrain,
  LocationOn,
  Agriculture,
  WaterDrop,
} from '@mui/icons-material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { Parcela } from '../interfaces';
import apiService from '../services/api';
import ParcelaModal from '../components/Modals/ParcelaModal';

const Parcelas: React.FC = () => {
  const [parcelas, setParcelas] = useState<Parcela[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedParcela, setSelectedParcela] = useState<Parcela | null>(null);

  const loadParcelas = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await apiService.getParcelas();
      // Si la respuesta es paginada, extraer los resultados
      const parcelasData = Array.isArray(response) ? response : response.results || [];
      setParcelas(parcelasData);
    } catch (err: any) {
      setError(err.message || 'Error al cargar parcelas');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadParcelas();
  }, []);

  const handleOpenModal = (parcela?: Parcela) => {
    setSelectedParcela(parcela || null);
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setSelectedParcela(null);
  };

  const handleSaveParcela = (savedParcela: Parcela) => {
    if (selectedParcela?.id) {
      // Actualizar parcela existente
      setParcelas(prev => prev.map(p => p.id === savedParcela.id ? savedParcela : p));
    } else {
      // Agregar nueva parcela
      setParcelas(prev => [...prev, savedParcela]);
    }
  };

  const handleDeleteParcela = async (id: number) => {
    if (window.confirm('¿Estás seguro de que deseas eliminar esta parcela?')) {
      try {
        await apiService.deleteParcela(id);
        setParcelas(prev => prev.filter(p => p.id !== id));
      } catch (err: any) {
        setError(err.message || 'Error al eliminar parcela');
      }
    }
  };

  const getEstadoColor = (estado: string) => {
    switch (estado) {
      case 'disponible':
        return 'success';
      case 'sembrada':
        return 'primary';
      case 'en_crecimiento':
        return 'info';
      case 'lista_cosecha':
        return 'warning';
      case 'cosechada':
        return 'secondary';
      default:
        return 'default';
    }
  };

  const getEstadoLabel = (estado: string) => {
    switch (estado) {
      case 'disponible':
        return 'Disponible';
      case 'sembrada':
        return 'Sembrada';
      case 'en_crecimiento':
        return 'En Crecimiento';
      case 'lista_cosecha':
        return 'Lista Cosecha';
      case 'cosechada':
        return 'Cosechada';
      case 'en_descanso':
        return 'En Descanso';
      case 'mantenimiento':
        return 'Mantenimiento';
      default:
        return estado;
    }
  };

  const columns: GridColDef[] = [
    {
      field: 'codigo',
      headerName: 'Código',
      width: 100,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Terrain color="primary" fontSize="small" />
          <Typography variant="body2" fontWeight={600}>
            {params.value}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'nombre',
      headerName: 'Nombre',
      width: 150,
    },
    {
      field: 'area_hectareas',
      headerName: 'Área (ha)',
      width: 100,
      type: 'number',
      renderCell: (params) => (
        <Typography variant="body2">
          {params.value?.toFixed(2)} ha
        </Typography>
      ),
    },
    {
      field: 'estado',
      headerName: 'Estado',
      width: 130,
      renderCell: (params) => (
        <Chip
          label={getEstadoLabel(params.value)}
          size="small"
          color={getEstadoColor(params.value) as any}
          variant="outlined"
        />
      ),
    },
    {
      field: 'cultivo_actual_info',
      headerName: 'Cultivo Actual',
      width: 150,
      renderCell: (params) => (
        params.value ? (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Agriculture fontSize="small" color="success" />
            <Typography variant="body2">
              {params.value.nombre}
            </Typography>
          </Box>
        ) : (
          <Typography variant="body2" color="text.secondary">
            Sin cultivo
          </Typography>
        )
      ),
    },
    {
      field: 'tipo_suelo',
      headerName: 'Tipo Suelo',
      width: 120,
      renderCell: (params) => (
        params.value ? (
          <Typography variant="caption">
            {params.value.replace('_', ' ')}
          </Typography>
        ) : (
          <Typography variant="caption" color="text.secondary">
            N/A
          </Typography>
        )
      ),
    },
    {
      field: 'tiene_riego',
      headerName: 'Riego',
      width: 80,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <WaterDrop 
            fontSize="small" 
            color={params.value ? 'primary' : 'disabled'} 
          />
          <Typography variant="caption">
            {params.value ? 'Sí' : 'No'}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'ubicacion_completa',
      headerName: 'Ubicación',
      width: 120,
      renderCell: (params) => (
        params.value && params.value !== 'No especificada' ? (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <LocationOn fontSize="small" color="info" />
            <Typography variant="caption">
              Ubicada
            </Typography>
          </Box>
        ) : (
          <Typography variant="caption" color="text.secondary">
            Sin ubicación
          </Typography>
        )
      ),
    },
    {
      field: 'activa',
      headerName: 'Estado',
      width: 100,
      renderCell: (params) => (
        <Chip
          label={params.value ? 'Activa' : 'Inactiva'}
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
              onClick={() => handleDeleteParcela(params.row.id)}
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
          Cargando parcelas...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
          Gestión de Parcelas
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Actualizar">
            <IconButton onClick={loadParcelas} color="primary">
              <Refresh />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => handleOpenModal()}
          >
            Nueva Parcela
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
              <Terrain sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
              <Typography variant="h4" sx={{ fontWeight: 600 }}>
                {Array.isArray(parcelas) ? parcelas.length : 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Parcelas
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 600, color: 'success.main' }}>
                {Array.isArray(parcelas) ? parcelas.filter(p => p.tiene_cultivo).length : 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Con Cultivo
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 600, color: 'info.main' }}>
                {Array.isArray(parcelas) ? parcelas.filter(p => p.estado === 'disponible').length : 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Disponibles
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 600, color: 'warning.main' }}>
                {Array.isArray(parcelas) ? parcelas.reduce((acc, p) => acc + p.area_hectareas, 0).toFixed(1) : '0.0'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Área Total (ha)
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabla de parcelas */}
      <Card>
        <CardContent>
          <DataGrid
            rows={parcelas}
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

      {/* Modal para crear/editar parcela */}
      <ParcelaModal
        open={modalOpen}
        onClose={handleCloseModal}
        onSave={handleSaveParcela}
        parcela={selectedParcela}
      />
    </Box>
  );
};

export default Parcelas;
