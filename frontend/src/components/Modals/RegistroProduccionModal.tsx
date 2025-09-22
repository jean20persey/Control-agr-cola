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
  Typography,
} from '@mui/material';
import { Close } from '@mui/icons-material';
import { RegistroProduccion, Parcela } from '../../interfaces';
import apiService from '../../services/api';

interface RegistroProduccionModalProps {
  open: boolean;
  onClose: () => void;
  onSave: (registro: RegistroProduccion) => void;
}

const calidadOptions = [
  { value: 'A', label: 'A - Excelente' },
  { value: 'B', label: 'B - Buena' },
  { value: 'C', label: 'C - Regular' },
  { value: 'D', label: 'D - Deficiente' },
];

const RegistroProduccionModal: React.FC<RegistroProduccionModalProps> = ({
  open,
  onClose,
  onSave,
}) => {
  const [formData, setFormData] = useState({
    parcela: '',
    fecha_cosecha: new Date().toISOString().split('T')[0],
    cantidad_cosechada: 0,
    calidad: 'A',
    observaciones: '',
  });

  const [parcelas, setParcelas] = useState<Parcela[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    if (open) {
      loadParcelas();
    }
  }, [open]);

  const loadParcelas = async () => {
    try {
      console.log('Cargando parcelas...');
      const response = await apiService.getParcelas();
      console.log('Respuesta completa de parcelas:', JSON.stringify(response, null, 2));
      
      const parcelasData = Array.isArray(response) ? response : response.results || [];
      console.log('Parcelas data extraída:', parcelasData);
      
      // Mostrar todas las parcelas primero
      console.log('Todas las parcelas:', parcelasData.map((p: Parcela) => ({
        id: p.id,
        codigo: p.codigo,
        activa: p.activa,
        cultivo_actual: p.cultivo_actual,
        estado: p.estado
      })));
      
      // Filtro más permisivo para debugging - solo parcelas activas
      const parcelasConCultivo = parcelasData.filter((p: Parcela) => {
        const cumpleCondiciones = p.activa; // Temporalmente solo verificar que esté activa
        console.log(`Parcela ${p.codigo}: activa=${p.activa}, cultivo=${p.cultivo_actual}, estado=${p.estado}, cumple=${cumpleCondiciones}`);
        return cumpleCondiciones;
      });
      
      console.log('Parcelas filtradas con cultivo:', parcelasConCultivo);
      setParcelas(parcelasConCultivo);
      
      if (parcelasConCultivo.length === 0) {
        setError('No hay parcelas con cultivo asignado disponibles. Asegúrate de tener parcelas activas con cultivos.');
      }
    } catch (err) {
      console.error('Error al cargar parcelas:', err);
      setError('Error al cargar parcelas disponibles');
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? (value === '' ? 0 : Number(value)) : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Validaciones básicas
      if (!formData.parcela) {
        setError('Por favor, selecciona una parcela');
        return;
      }

      if (formData.cantidad_cosechada <= 0) {
        setError('La cantidad cosechada debe ser mayor a 0');
        return;
      }

      if (!formData.fecha_cosecha) {
        setError('Por favor, selecciona una fecha de cosecha');
        return;
      }

      // Encontrar la parcela seleccionada para obtener cultivo y calcular rendimiento
      const parcelaSeleccionada = parcelas.find(p => p.id === Number(formData.parcela));
      if (!parcelaSeleccionada) {
        setError('Parcela seleccionada no encontrada');
        return;
      }

      const registroData = {
        parcela: Number(formData.parcela),
        cultivo: parcelaSeleccionada.cultivo_actual, // Obtener cultivo de la parcela
        fecha_registro: formData.fecha_cosecha, // Mapear correctamente
        cantidad_kg: formData.cantidad_cosechada, // Mapear correctamente
        calidad: formData.calidad,
        temporada: new Date().getFullYear().toString(), // Mapear correctamente
        notas_anomalia: formData.observaciones, // Mapear a campo correcto
      };

      console.log('Datos del registro a enviar:', JSON.stringify(registroData, null, 2));

      const savedRegistro = await apiService.createRegistroProduccion(registroData);
      onSave(savedRegistro);
      onClose();
      
      // Resetear formulario
      setFormData({
        parcela: '',
        fecha_cosecha: new Date().toISOString().split('T')[0],
        cantidad_cosechada: 0,
        calidad: 'A',
        observaciones: '',
      });
    } catch (err: any) {
      console.error('Error al crear registro:', err);
      console.error('Respuesta del servidor:', JSON.stringify(err.response?.data, null, 2));
      console.error('Status:', err.response?.status);
      console.error('Headers:', err.response?.headers);
      
      let errorMessage = 'Error al guardar registro de producción';
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

  const selectedParcela = parcelas.find(p => p.id === Number(formData.parcela));
  const rendimientoEstimado = selectedParcela && formData.cantidad_cosechada > 0
    ? (formData.cantidad_cosechada / selectedParcela.area_hectareas).toFixed(1)
    : '0';

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            Nuevo Registro de Producción
            <IconButton onClick={handleClose} disabled={loading}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>

        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Parcela *"
                name="parcela"
                value={formData.parcela}
                onChange={handleChange}
                required
                disabled={loading}
                helperText={parcelas.length === 0 ? "No hay parcelas con cultivo disponibles" : ""}
              >
                {parcelas.map((parcela) => (
                  <MenuItem key={parcela.id} value={parcela.id}>
                    {parcela.codigo} - {parcela.cultivo_actual_info?.nombre} ({parcela.area_hectareas} ha)
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="date"
                label="Fecha de Cosecha *"
                name="fecha_cosecha"
                value={formData.fecha_cosecha}
                onChange={handleChange}
                required
                disabled={loading}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Cantidad Cosechada (kg) *"
                name="cantidad_cosechada"
                value={formData.cantidad_cosechada}
                onChange={handleChange}
                required
                disabled={loading}
                inputProps={{ min: 0, step: 0.1 }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Calidad *"
                name="calidad"
                value={formData.calidad}
                onChange={handleChange}
                required
                disabled={loading}
              >
                {calidadOptions.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            {selectedParcela && (
              <Grid item xs={12}>
                <Box sx={{ p: 2, bgcolor: 'background.paper', borderRadius: 1, border: 1, borderColor: 'divider' }}>
                  <Typography variant="subtitle2" gutterBottom>
                    📊 Información de la Parcela Seleccionada:
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6} sm={3}>
                      <Typography variant="body2" color="text.secondary">Área:</Typography>
                      <Typography variant="body2" fontWeight={600}>{selectedParcela.area_hectareas} ha</Typography>
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <Typography variant="body2" color="text.secondary">Cultivo:</Typography>
                      <Typography variant="body2" fontWeight={600}>{selectedParcela.cultivo_actual_info?.nombre}</Typography>
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <Typography variant="body2" color="text.secondary">Rendimiento Estimado:</Typography>
                      <Typography variant="body2" fontWeight={600} color="primary.main">
                        {rendimientoEstimado} kg/ha
                      </Typography>
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <Typography variant="body2" color="text.secondary">Estado:</Typography>
                      <Typography variant="body2" fontWeight={600}>{selectedParcela.estado}</Typography>
                    </Grid>
                  </Grid>
                </Box>
              </Grid>
            )}

            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Observaciones"
                name="observaciones"
                value={formData.observaciones}
                onChange={handleChange}
                disabled={loading}
                placeholder="Notas adicionales sobre la cosecha, condiciones climáticas, problemas encontrados, etc."
              />
            </Grid>
          </Grid>
        </DialogContent>

        <DialogActions sx={{ p: 3 }}>
          <Button onClick={handleClose} disabled={loading}>
            Cancelar
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={loading || parcelas.length === 0}
            startIcon={loading && <CircularProgress size={20} />}
          >
            {loading ? 'Guardando...' : 'Crear Registro'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default RegistroProduccionModal;
