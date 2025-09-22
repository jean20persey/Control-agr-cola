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
  FormControlLabel,
  Switch,
} from '@mui/material';
import { Close } from '@mui/icons-material';
import { Parcela, Cultivo } from '../../interfaces';
import apiService from '../../services/api';

interface ParcelaModalProps {
  open: boolean;
  onClose: () => void;
  onSave: (parcela: Parcela) => void;
  parcela?: Parcela | null;
}

const estadosParcela = [
  { value: 'disponible', label: 'Disponible' },
  { value: 'sembrada', label: 'Sembrada' },
  { value: 'en_crecimiento', label: 'En Crecimiento' },
  { value: 'lista_cosecha', label: 'Lista para Cosecha' },
  { value: 'cosechada', label: 'Cosechada' },
  { value: 'en_descanso', label: 'En Descanso' },
  { value: 'mantenimiento', label: 'En Mantenimiento' },
];

const tiposSuelo = [
  { value: 'arcilloso', label: 'Arcilloso' },
  { value: 'arenoso', label: 'Arenoso' },
  { value: 'limoso', label: 'Limoso' },
  { value: 'franco', label: 'Franco' },
  { value: 'franco_arcilloso', label: 'Franco Arcilloso' },
  { value: 'franco_arenoso', label: 'Franco Arenoso' },
  { value: 'franco_limoso', label: 'Franco Limoso' },
];

const tiposRiego = [
  { value: 'goteo', label: 'Goteo' },
  { value: 'aspersion', label: 'Aspersión' },
  { value: 'inundacion', label: 'Inundación' },
  { value: 'surcos', label: 'Surcos' },
  { value: 'microaspersion', label: 'Microaspersión' },
];

const ParcelaModal: React.FC<ParcelaModalProps> = ({
  open,
  onClose,
  onSave,
  parcela,
}) => {
  const [formData, setFormData] = useState({
    codigo: parcela?.codigo || '',
    nombre: parcela?.nombre || '',
    descripcion: parcela?.descripcion || '',
    area_hectareas: parcela?.area_hectareas || 0,
    ubicacion_lat: parcela?.ubicacion_lat || '',
    ubicacion_lng: parcela?.ubicacion_lng || '',
    altitud: parcela?.altitud || '',
    tipo_suelo: parcela?.tipo_suelo || '',
    ph_suelo: parcela?.ph_suelo || '',
    materia_organica: parcela?.materia_organica || '',
    capacidad_campo: parcela?.capacidad_campo || '',
    cultivo_actual: parcela?.cultivo_actual || '',
    fecha_siembra: parcela?.fecha_siembra || '',
    estado: parcela?.estado || 'disponible',
    tiene_riego: parcela?.tiene_riego ?? false,
    tipo_riego: parcela?.tipo_riego || '',
    activa: parcela?.activa ?? true,
  });

  const [cultivos, setCultivos] = useState<Cultivo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    console.log('ParcelaModal - Estado open:', open);
    if (open) {
      console.log('Cargando cultivos para el modal...');
      loadCultivos();
    }
  }, [open]);

  const loadCultivos = async () => {
    try {
      const response = await apiService.getCultivos();
      const cultivosData = Array.isArray(response) ? response : response.results || [];
      setCultivos(cultivosData.filter((c: Cultivo) => c.activo));
    } catch (err) {
      console.error('Error al cargar cultivos:', err);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : 
              type === 'number' ? (value === '' ? '' : Number(value)) : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Validaciones básicas
      if (!formData.codigo || !formData.nombre) {
        setError('Por favor, completa los campos obligatorios');
        return;
      }

      if (formData.area_hectareas <= 0) {
        setError('El área debe ser mayor a 0');
        return;
      }

      const parcelaData = {
        ...formData,
        ubicacion_lat: formData.ubicacion_lat || null,
        ubicacion_lng: formData.ubicacion_lng || null,
        altitud: formData.altitud || null,
        ph_suelo: formData.ph_suelo || null,
        materia_organica: formData.materia_organica || null,
        capacidad_campo: formData.capacidad_campo || null,
        cultivo_actual: formData.cultivo_actual || null,
        fecha_siembra: formData.fecha_siembra || null,
        tipo_riego: formData.tiene_riego ? formData.tipo_riego : null,
      };

      let savedParcela;
      if (parcela?.id) {
        // Actualizar parcela existente
        savedParcela = await apiService.updateParcela(parcela.id, parcelaData);
      } else {
        // Crear nueva parcela
        savedParcela = await apiService.createParcela(parcelaData);
      }

      onSave(savedParcela);
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Error al guardar parcela');
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
    <Dialog open={open} onClose={handleClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          {parcela?.id ? 'Editar Parcela' : 'Nueva Parcela'}
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
                label="Código *"
                name="codigo"
                value={formData.codigo}
                onChange={handleChange}
                required
                disabled={loading}
                helperText="Código único de identificación"
              />
            </Grid>

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

            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={2}
                label="Descripción"
                name="descripcion"
                value={formData.descripcion}
                onChange={handleChange}
                disabled={loading}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Área (hectáreas) *"
                name="area_hectareas"
                value={formData.area_hectareas}
                onChange={handleChange}
                required
                disabled={loading}
                inputProps={{ min: 0.01, step: 0.01 }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Estado"
                name="estado"
                value={formData.estado}
                onChange={handleChange}
                disabled={loading}
              >
                {estadosParcela.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            {/* Ubicación */}
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                type="number"
                label="Latitud"
                name="ubicacion_lat"
                value={formData.ubicacion_lat}
                onChange={handleChange}
                disabled={loading}
                inputProps={{ step: 0.000001 }}
              />
            </Grid>

            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                type="number"
                label="Longitud"
                name="ubicacion_lng"
                value={formData.ubicacion_lng}
                onChange={handleChange}
                disabled={loading}
                inputProps={{ step: 0.000001 }}
              />
            </Grid>

            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                type="number"
                label="Altitud (msnm)"
                name="altitud"
                value={formData.altitud}
                onChange={handleChange}
                disabled={loading}
              />
            </Grid>

            {/* Características del suelo */}
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Tipo de Suelo"
                name="tipo_suelo"
                value={formData.tipo_suelo}
                onChange={handleChange}
                disabled={loading}
              >
                {tiposSuelo.map((option) => (
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
                label="pH del Suelo"
                name="ph_suelo"
                value={formData.ph_suelo}
                onChange={handleChange}
                disabled={loading}
                inputProps={{ min: 0, max: 14, step: 0.1 }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Materia Orgánica (%)"
                name="materia_organica"
                value={formData.materia_organica}
                onChange={handleChange}
                disabled={loading}
                inputProps={{ min: 0, max: 100, step: 0.1 }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Capacidad de Campo (%)"
                name="capacidad_campo"
                value={formData.capacidad_campo}
                onChange={handleChange}
                disabled={loading}
                inputProps={{ min: 0, max: 100, step: 0.1 }}
              />
            </Grid>

            {/* Cultivo actual */}
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Cultivo Actual"
                name="cultivo_actual"
                value={formData.cultivo_actual}
                onChange={handleChange}
                disabled={loading}
              >
                <MenuItem value="">Sin cultivo</MenuItem>
                {cultivos.map((cultivo) => (
                  <MenuItem key={cultivo.id} value={cultivo.id}>
                    {cultivo.nombre} - {cultivo.variedad}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="date"
                label="Fecha de Siembra"
                name="fecha_siembra"
                value={formData.fecha_siembra}
                onChange={handleChange}
                disabled={loading}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            {/* Sistema de riego */}
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.tiene_riego}
                    onChange={handleChange}
                    name="tiene_riego"
                    disabled={loading}
                  />
                }
                label="Tiene Sistema de Riego"
              />
            </Grid>

            {formData.tiene_riego && (
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  select
                  label="Tipo de Riego"
                  name="tipo_riego"
                  value={formData.tipo_riego}
                  onChange={handleChange}
                  disabled={loading}
                >
                  {tiposRiego.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
            )}

            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.activa}
                    onChange={handleChange}
                    name="activa"
                    disabled={loading}
                  />
                }
                label="Parcela Activa"
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
            {loading ? 'Guardando...' : parcela?.id ? 'Actualizar' : 'Crear'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default ParcelaModal;
