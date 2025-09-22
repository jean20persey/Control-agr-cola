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
  Chip,
} from '@mui/material';
import { Close, Science } from '@mui/icons-material';
import { PrediccionCosecha, Parcela } from '../../interfaces';
import apiService from '../../services/api';

interface PrediccionModalProps {
  open: boolean;
  onClose: () => void;
  onSave: (prediccion: PrediccionCosecha) => void;
}

const modeloOptions = [
  { value: 'linear', label: 'Regresión Lineal' },
  { value: 'random_forest', label: 'Random Forest' },
  { value: 'xgboost', label: 'XGBoost' },
];

const PrediccionModal: React.FC<PrediccionModalProps> = ({
  open,
  onClose,
  onSave,
}) => {
  const [formData, setFormData] = useState({
    parcela_id: '',
    cultivo_id: '',
    temporada_objetivo: new Date().getFullYear().toString(),
    modelo: 'linear',
  });

  const [parcelas, setParcelas] = useState<Parcela[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [prediccionGenerada, setPrediccionGenerada] = useState<any>(null);

  useEffect(() => {
    if (open) {
      loadParcelas();
      setPrediccionGenerada(null);
      setError('');
    }
  }, [open]);

  const loadParcelas = async () => {
    try {
      console.log('Cargando parcelas para predicción...');
      const response = await apiService.getParcelas();
      const parcelasData = Array.isArray(response) ? response : response.results || [];
      
      // Solo parcelas activas con cultivo asignado
      const parcelasConCultivo = parcelasData.filter((p: Parcela) => 
        p.activa && p.cultivo_actual
      );
      
      setParcelas(parcelasConCultivo);
      console.log('Parcelas cargadas para predicción:', parcelasConCultivo);
    } catch (err) {
      console.error('Error al cargar parcelas:', err);
      setError('Error al cargar parcelas disponibles');
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));

    // Si cambia la parcela, actualizar el cultivo automáticamente
    if (name === 'parcela_id') {
      const parcelaSeleccionada = parcelas.find(p => p.id === Number(value));
      if (parcelaSeleccionada) {
        setFormData(prev => ({
          ...prev,
          cultivo_id: parcelaSeleccionada.cultivo_actual?.toString() || '',
        }));
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setPrediccionGenerada(null);

    try {
      // Validaciones básicas
      if (!formData.parcela_id) {
        setError('Por favor, selecciona una parcela');
        return;
      }

      if (!formData.temporada_objetivo) {
        setError('Por favor, especifica la temporada objetivo');
        return;
      }

      const prediccionData = {
        parcela_id: Number(formData.parcela_id),
        cultivo_id: Number(formData.cultivo_id),
        temporada_objetivo: formData.temporada_objetivo,
        modelo: formData.modelo,
      };

      console.log('Datos de predicción a enviar:', JSON.stringify(prediccionData, null, 2));

      const savedPrediccion = await apiService.createPrediccion(prediccionData);
      setPrediccionGenerada(savedPrediccion);
      
      console.log('Predicción creada:', savedPrediccion);
      
      // Mostrar resultado por unos segundos antes de cerrar
      setTimeout(() => {
        onSave(savedPrediccion);
        onClose();
        resetForm();
      }, 3000);
      
    } catch (err: any) {
      console.error('Error al crear predicción:', err);
      console.error('Respuesta del servidor:', JSON.stringify(err.response?.data, null, 2));
      
      let errorMessage = 'Error al generar predicción';
      if (err.response?.data) {
        if (typeof err.response.data === 'string') {
          errorMessage = err.response.data;
        } else if (err.response.data.error) {
          errorMessage = err.response.data.error;
          
          // Mensaje específico para datos insuficientes
          if (err.response.data.error.includes('al menos 5 registros históricos')) {
            errorMessage = '📊 Datos Insuficientes: Se necesitan al menos 5 registros históricos de producción para generar predicciones precisas. Crea más registros de producción y vuelve a intentarlo.';
          }
        } else if (err.response.data.detail) {
          errorMessage = err.response.data.detail;
        } else {
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

  const resetForm = () => {
    setFormData({
      parcela_id: '',
      cultivo_id: '',
      temporada_objetivo: new Date().getFullYear().toString(),
      modelo: 'linear',
    });
    setPrediccionGenerada(null);
  };

  const handleClose = () => {
    if (!loading) {
      onClose();
      resetForm();
    }
  };

  const selectedParcela = parcelas.find(p => p.id === Number(formData.parcela_id));

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Science color="primary" />
              Nueva Predicción de Cosecha
            </Box>
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

          {prediccionGenerada && (
            <Alert severity="success" sx={{ mb: 2 }}>
              <Typography variant="h6" gutterBottom>
                🎯 Predicción Generada Exitosamente
              </Typography>
              <Box sx={{ mt: 1 }}>
                <Chip 
                  label={`Rendimiento Predicho: ${prediccionGenerada.rendimiento_predicho?.toFixed(1)} kg/ha`}
                  color="success"
                  sx={{ mr: 1, mb: 1 }}
                />
                <Chip 
                  label={`Confianza: ${(prediccionGenerada.confianza_prediccion * 100)?.toFixed(1)}%`}
                  color="info"
                  sx={{ mr: 1, mb: 1 }}
                />
                <Chip 
                  label={`Modelo: ${prediccionGenerada.modelo_utilizado}`}
                  color="primary"
                  sx={{ mb: 1 }}
                />
              </Box>
            </Alert>
          )}

          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Parcela *"
                name="parcela_id"
                value={formData.parcela_id}
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
                label="Temporada Objetivo *"
                name="temporada_objetivo"
                value={formData.temporada_objetivo}
                onChange={handleChange}
                required
                disabled={loading}
                placeholder="2024"
                helperText="Año para el cual generar la predicción"
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Modelo de Predicción *"
                name="modelo"
                value={formData.modelo}
                onChange={handleChange}
                required
                disabled={loading}
              >
                {modeloOptions.map((option) => (
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
                    🏞️ Información de la Parcela Seleccionada:
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6} sm={3}>
                      <Typography variant="body2" color="text.secondary">Código:</Typography>
                      <Typography variant="body2" fontWeight={600}>{selectedParcela.codigo}</Typography>
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <Typography variant="body2" color="text.secondary">Cultivo:</Typography>
                      <Typography variant="body2" fontWeight={600}>{selectedParcela.cultivo_actual_info?.nombre}</Typography>
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <Typography variant="body2" color="text.secondary">Área:</Typography>
                      <Typography variant="body2" fontWeight={600}>{selectedParcela.area_hectareas} ha</Typography>
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
              <Alert severity="info">
                <Typography variant="body2">
                  <strong>ℹ️ Sobre las Predicciones:</strong><br/>
                  • <strong>Regresión Lineal:</strong> Modelo simple y rápido, bueno para tendencias básicas<br/>
                  • <strong>Random Forest:</strong> Modelo robusto que considera múltiples factores<br/>
                  • <strong>XGBoost:</strong> Modelo avanzado con alta precisión para datos complejos<br/>
                  • <strong>Requisito:</strong> Se necesitan al menos 5 registros históricos de producción
                </Typography>
              </Alert>
            </Grid>

            <Grid item xs={12}>
              <Alert severity="warning">
                <Typography variant="body2">
                  <strong>⚠️ Datos Insuficientes:</strong><br/>
                  Para generar predicciones precisas, necesitas crear más registros de producción históricos. 
                  Actualmente tienes 1 registro, pero se requieren mínimo 5 registros para entrenar los modelos de IA.
                </Typography>
              </Alert>
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
            disabled={loading || parcelas.length === 0 || prediccionGenerada}
            startIcon={loading ? <CircularProgress size={20} /> : <Science />}
          >
            {loading ? 'Generando Predicción...' : 'Generar Predicción'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default PrediccionModal;
