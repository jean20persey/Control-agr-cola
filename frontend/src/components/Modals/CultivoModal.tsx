import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Grid,
  MenuItem,
  Alert,
  CircularProgress,
  Box,
  IconButton,
} from '@mui/material';
import { Close } from '@mui/icons-material';
import { Cultivo } from '../../interfaces';
import apiService from '../../services/api';

interface CultivoModalProps {
  open: boolean;
  onClose: () => void;
  onSave: (cultivo: Cultivo) => void;
  cultivo?: Cultivo | null;
}

// Los tipos se cargarán dinámicamente desde el backend

const CultivoModal: React.FC<CultivoModalProps> = ({
  open,
  onClose,
  onSave,
  cultivo,
}) => {
  const [formData, setFormData] = useState({
    nombre: cultivo?.nombre || '',
    variedad: cultivo?.variedad || '',
    tipo: cultivo?.tipo || '',
    ciclo_dias: cultivo?.ciclo_dias || 0,
    rendimiento_esperado: cultivo?.rendimiento_esperado || 0,
    descripcion: cultivo?.descripcion || '',
    temperatura_optima_min: cultivo?.temperatura_optima_min || '',
    temperatura_optima_max: cultivo?.temperatura_optima_max || '',
    ph_suelo_min: cultivo?.ph_suelo_min || '',
    ph_suelo_max: cultivo?.ph_suelo_max || '',
    precipitacion_anual: cultivo?.precipitacion_anual || '',
    activo: cultivo?.activo ?? true,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [tiposCultivo, setTiposCultivo] = useState<Array<{value: string, label: string}>>([]);

  // Cargar tipos de cultivo desde el backend
  useEffect(() => {
    const loadTiposCultivo = async () => {
      console.log('Iniciando carga de tipos de cultivo...');
      
      // Usar tipos por defecto inmediatamente para que el dropdown funcione
      const tiposDefault = [
        { value: 'cereales', label: 'Cereales' },
        { value: 'hortalizas', label: 'Hortalizas' },
        { value: 'frutales', label: 'Frutales' },
        { value: 'legumbres', label: 'Legumbres' },
        { value: 'tubérculos', label: 'Tubérculos' },
        { value: 'oleaginosas', label: 'Oleaginosas' },
        { value: 'forrajes', label: 'Forrajes' },
        { value: 'otros', label: 'Otros' },
      ];
      
      setTiposCultivo(tiposDefault);
      
      try {
        const tipos = await apiService.getCultivosTipos();
        console.log('Tipos de cultivo desde backend:', JSON.stringify(tipos, null, 2));
        
        // Si el backend devuelve tipos, usarlos; sino mantener los default
        if (Array.isArray(tipos) && tipos.length > 0) {
          const tiposFormateados = tipos.map((tipo: any) => ({
            value: tipo.value || tipo.key || tipo,
            label: tipo.label || tipo.display_name || tipo
          }));
          console.log('Tipos formateados:', tiposFormateados);
          setTiposCultivo(tiposFormateados);
        }
      } catch (error) {
        console.error('Error al cargar tipos de cultivo desde backend:', error);
        console.log('Usando tipos por defecto');
        // Los tipos default ya están establecidos, no hacer nada más
      }
    };

    if (open) {
      loadTiposCultivo();
    }
  }, [open]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? (value === '' ? '' : Number(value)) : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Validaciones básicas
      if (!formData.nombre || !formData.variedad || !formData.tipo) {
        setError('Por favor, completa los campos obligatorios');
        return;
      }

      if (formData.ciclo_dias <= 0) {
        setError('El ciclo de días debe ser mayor a 0');
        return;
      }

      if (formData.rendimiento_esperado <= 0) {
        setError('El rendimiento esperado debe ser mayor a 0');
        return;
      }

      const cultivoData = {
        nombre: formData.nombre.trim(),
        variedad: formData.variedad.trim(),
        tipo: formData.tipo,
        ciclo_dias: Number(formData.ciclo_dias),
        rendimiento_esperado: Number(formData.rendimiento_esperado),
        descripcion: formData.descripcion.trim(),
        temperatura_optima_min: formData.temperatura_optima_min ? Number(formData.temperatura_optima_min) : null,
        temperatura_optima_max: formData.temperatura_optima_max ? Number(formData.temperatura_optima_max) : null,
        ph_suelo_min: formData.ph_suelo_min ? Number(formData.ph_suelo_min) : null,
        ph_suelo_max: formData.ph_suelo_max ? Number(formData.ph_suelo_max) : null,
        precipitacion_anual: formData.precipitacion_anual ? Number(formData.precipitacion_anual) : null,
        activo: formData.activo,
      };

      // Debug: mostrar datos que se envían
      console.log('Datos del cultivo a enviar:', JSON.stringify(cultivoData, null, 2));

      let savedCultivo;
      if (cultivo?.id) {
        // Actualizar cultivo existente
        savedCultivo = await apiService.updateCultivo(cultivo.id, cultivoData);
      } else {
        // Crear nuevo cultivo
        savedCultivo = await apiService.createCultivo(cultivoData);
      }

      onSave(savedCultivo);
      onClose();
    } catch (err: any) {
      console.error('Error al crear cultivo:', err);
      console.error('Respuesta del servidor:', JSON.stringify(err.response?.data, null, 2));
      console.error('Status:', err.response?.status);
      console.error('Headers:', err.response?.headers);
      
      let errorMessage = 'Error al guardar cultivo';
      if (err.response?.data) {
        if (typeof err.response.data === 'string') {
          errorMessage = err.response.data;
        } else if (err.response.data.error) {
          errorMessage = err.response.data.error;
        } else if (err.response.data.detail) {
          errorMessage = err.response.data.detail;
        } else {
          // Mostrar errores de validación específicos
          const errors = Object.entries(err.response.data).map(([field, messages]) => {
            if (Array.isArray(messages)) {
              return `${field}: ${messages.join(', ')}`;
            }
            return `${field}: ${messages}`;
          }).join('\n');
          errorMessage = errors || errorMessage;
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      onClose();
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          {cultivo?.id ? 'Editar Cultivo' : 'Nuevo Cultivo'}
          <IconButton onClick={handleClose} disabled={loading}>
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>

      <form onSubmit={handleSubmit}>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Grid container spacing={2}>
            {/* Información básica */}
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Nombre *"
                name="nombre"
                value={formData.nombre}
                onChange={handleChange}
                required
                disabled={loading}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Variedad *"
                name="variedad"
                value={formData.variedad}
                onChange={handleChange}
                required
                disabled={loading}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Tipo *"
                name="tipo"
                value={formData.tipo}
                onChange={handleChange}
                required
                disabled={loading}
              >
                {tiposCultivo.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Ciclo (días) *"
                name="ciclo_dias"
                value={formData.ciclo_dias}
                onChange={handleChange}
                required
                disabled={loading}
                inputProps={{ min: 1 }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Rendimiento Esperado (kg/ha) *"
                name="rendimiento_esperado"
                value={formData.rendimiento_esperado}
                onChange={handleChange}
                required
                disabled={loading}
                inputProps={{ min: 0, step: 0.1 }}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Descripción"
                name="descripcion"
                value={formData.descripcion}
                onChange={handleChange}
                disabled={loading}
              />
            </Grid>

            {/* Condiciones óptimas */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Temperatura Mínima Óptima (°C)"
                name="temperatura_optima_min"
                type="number"
                value={formData.temperatura_optima_min}
                onChange={handleChange}
                disabled={loading}
                inputProps={{ step: 0.1 }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Temperatura Máxima Óptima (°C)"
                name="temperatura_optima_max"
                type="number"
                value={formData.temperatura_optima_max}
                onChange={handleChange}
                disabled={loading}
                inputProps={{ step: 0.1 }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="pH Mínimo del Suelo"
                name="ph_suelo_min"
                type="number"
                value={formData.ph_suelo_min}
                onChange={handleChange}
                disabled={loading}
                inputProps={{ min: 0, max: 14, step: 0.1 }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="pH Máximo del Suelo"
                name="ph_suelo_max"
                type="number"
                value={formData.ph_suelo_max}
                onChange={handleChange}
                disabled={loading}
                inputProps={{ min: 0, max: 14, step: 0.1 }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Precipitación Anual (mm)"
                name="precipitacion_anual"
                type="number"
                value={formData.precipitacion_anual}
                onChange={handleChange}
                disabled={loading}
                inputProps={{ min: 0 }}
              />
            </Grid>
          </Grid>
        </DialogContent>

        <DialogActions sx={{ p: 2 }}>
          <Button onClick={handleClose} disabled={loading}>
            Cancelar
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : null}
          >
            {loading ? 'Guardando...' : cultivo?.id ? 'Actualizar' : 'Crear'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default CultivoModal;
