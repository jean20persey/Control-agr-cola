import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Switch,
  FormControlLabel,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  TextField,
  Button,
  Alert,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Notifications,
  Security,
  Palette,
  Storage,
  AccountCircle,
  Save,
  RestoreFromTrash,
  Edit,
  Delete,
  Add,
  Visibility,
  VisibilityOff,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

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
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
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

const Settings: React.FC = () => {
  const { user } = useAuth();
  const [tabValue, setTabValue] = useState(0);
  const [showPassword, setShowPassword] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [apiKeyDialog, setApiKeyDialog] = useState(false);
  const [newApiKey, setNewApiKey] = useState('');

  // Estados de configuración
  const [settings, setSettings] = useState({
    // Notificaciones
    emailNotifications: true,
    pushNotifications: true,
    alertSounds: false,
    weeklyReports: true,
    anomalyAlerts: true,
    
    // Apariencia
    theme: 'light',
    language: 'es',
    dateFormat: 'DD/MM/YYYY',
    timezone: 'America/Bogota',
    
    // Seguridad
    twoFactorAuth: false,
    sessionTimeout: 30,
    passwordExpiry: 90,
    
    // Datos y Exportación
    autoBackup: true,
    backupFrequency: 'weekly',
    dataRetention: 365,
    exportFormat: 'xlsx',
  });

  const [apiKeys] = useState([
    { id: '1', name: 'API Principal', key: 'ak_live_***************', created: '2024-01-15', lastUsed: '2024-09-18' },
    { id: '2', name: 'API Desarrollo', key: 'ak_test_***************', created: '2024-02-01', lastUsed: '2024-09-10' },
  ]);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleSettingChange = (key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleSave = () => {
    // Aquí iría la lógica para guardar las configuraciones
    console.log('Guardando configuraciones:', settings);
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 3000);
  };

  const handleResetToDefaults = () => {
    // Restablecer a valores por defecto
    setSettings({
      emailNotifications: true,
      pushNotifications: true,
      alertSounds: false,
      weeklyReports: true,
      anomalyAlerts: true,
      theme: 'light',
      language: 'es',
      dateFormat: 'DD/MM/YYYY',
      timezone: 'America/Bogota',
      twoFactorAuth: false,
      sessionTimeout: 30,
      passwordExpiry: 90,
      autoBackup: true,
      backupFrequency: 'weekly',
      dataRetention: 365,
      exportFormat: 'xlsx',
    });
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
          Configuración
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<RestoreFromTrash />}
            onClick={handleResetToDefaults}
          >
            Restablecer
          </Button>
          <Button
            variant="contained"
            startIcon={<Save />}
            onClick={handleSave}
          >
            Guardar Cambios
          </Button>
        </Box>
      </Box>

      {/* Alert de éxito */}
      {saveSuccess && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Configuración guardada exitosamente
        </Alert>
      )}

      {/* Tabs de configuración */}
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="configuración tabs">
            <Tab icon={<Notifications />} label="Notificaciones" />
            <Tab icon={<Palette />} label="Apariencia" />
            <Tab icon={<Security />} label="Seguridad" />
            <Tab icon={<Storage />} label="Datos" />
            <Tab icon={<AccountCircle />} label="Perfil" />
          </Tabs>
        </Box>

        {/* Panel de Notificaciones */}
        <TabPanel value={tabValue} index={0}>
          <Typography variant="h6" gutterBottom>
            Preferencias de Notificaciones
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    Canales de Notificación
                  </Typography>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.emailNotifications}
                        onChange={(e) => handleSettingChange('emailNotifications', e.target.checked)}
                      />
                    }
                    label="Notificaciones por email"
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.pushNotifications}
                        onChange={(e) => handleSettingChange('pushNotifications', e.target.checked)}
                      />
                    }
                    label="Notificaciones push"
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.alertSounds}
                        onChange={(e) => handleSettingChange('alertSounds', e.target.checked)}
                      />
                    }
                    label="Sonidos de alerta"
                  />
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    Tipos de Alertas
                  </Typography>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.weeklyReports}
                        onChange={(e) => handleSettingChange('weeklyReports', e.target.checked)}
                      />
                    }
                    label="Reportes semanales"
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.anomalyAlerts}
                        onChange={(e) => handleSettingChange('anomalyAlerts', e.target.checked)}
                      />
                    }
                    label="Alertas de anomalías"
                  />
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Panel de Apariencia */}
        <TabPanel value={tabValue} index={1}>
          <Typography variant="h6" gutterBottom>
            Personalización de Interfaz
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth margin="normal">
                <InputLabel>Tema</InputLabel>
                <Select
                  value={settings.theme}
                  label="Tema"
                  onChange={(e) => handleSettingChange('theme', e.target.value)}
                >
                  <MenuItem value="light">Claro</MenuItem>
                  <MenuItem value="dark">Oscuro</MenuItem>
                  <MenuItem value="auto">Automático</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth margin="normal">
                <InputLabel>Idioma</InputLabel>
                <Select
                  value={settings.language}
                  label="Idioma"
                  onChange={(e) => handleSettingChange('language', e.target.value)}
                >
                  <MenuItem value="es">Español</MenuItem>
                  <MenuItem value="en">English</MenuItem>
                  <MenuItem value="pt">Português</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth margin="normal">
                <InputLabel>Formato de Fecha</InputLabel>
                <Select
                  value={settings.dateFormat}
                  label="Formato de Fecha"
                  onChange={(e) => handleSettingChange('dateFormat', e.target.value)}
                >
                  <MenuItem value="DD/MM/YYYY">DD/MM/YYYY</MenuItem>
                  <MenuItem value="MM/DD/YYYY">MM/DD/YYYY</MenuItem>
                  <MenuItem value="YYYY-MM-DD">YYYY-MM-DD</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth margin="normal">
                <InputLabel>Zona Horaria</InputLabel>
                <Select
                  value={settings.timezone}
                  label="Zona Horaria"
                  onChange={(e) => handleSettingChange('timezone', e.target.value)}
                >
                  <MenuItem value="America/Bogota">Bogotá (GMT-5)</MenuItem>
                  <MenuItem value="America/Mexico_City">Ciudad de México (GMT-6)</MenuItem>
                  <MenuItem value="America/New_York">Nueva York (GMT-5)</MenuItem>
                  <MenuItem value="Europe/Madrid">Madrid (GMT+1)</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Panel de Seguridad */}
        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" gutterBottom>
            Configuración de Seguridad
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    Autenticación
                  </Typography>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.twoFactorAuth}
                        onChange={(e) => handleSettingChange('twoFactorAuth', e.target.checked)}
                      />
                    }
                    label="Autenticación de dos factores"
                  />
                  <FormControl fullWidth margin="normal">
                    <InputLabel>Tiempo de sesión (minutos)</InputLabel>
                    <Select
                      value={settings.sessionTimeout}
                      label="Tiempo de sesión (minutos)"
                      onChange={(e) => handleSettingChange('sessionTimeout', e.target.value)}
                    >
                      <MenuItem value={15}>15 minutos</MenuItem>
                      <MenuItem value={30}>30 minutos</MenuItem>
                      <MenuItem value={60}>1 hora</MenuItem>
                      <MenuItem value={120}>2 horas</MenuItem>
                    </Select>
                  </FormControl>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    Claves API
                  </Typography>
                  <List>
                    {apiKeys.map((apiKey) => (
                      <ListItem key={apiKey.id}>
                        <ListItemText
                          primary={apiKey.name}
                          secondary={`Creada: ${apiKey.created} | Último uso: ${apiKey.lastUsed}`}
                        />
                        <ListItemSecondaryAction>
                          <IconButton size="small">
                            <Edit />
                          </IconButton>
                          <IconButton size="small" color="error">
                            <Delete />
                          </IconButton>
                        </ListItemSecondaryAction>
                      </ListItem>
                    ))}
                  </List>
                  <Button
                    startIcon={<Add />}
                    onClick={() => setApiKeyDialog(true)}
                    variant="outlined"
                    size="small"
                  >
                    Nueva Clave API
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Panel de Datos */}
        <TabPanel value={tabValue} index={3}>
          <Typography variant="h6" gutterBottom>
            Gestión de Datos
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    Respaldo Automático
                  </Typography>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.autoBackup}
                        onChange={(e) => handleSettingChange('autoBackup', e.target.checked)}
                      />
                    }
                    label="Respaldo automático"
                  />
                  <FormControl fullWidth margin="normal">
                    <InputLabel>Frecuencia de respaldo</InputLabel>
                    <Select
                      value={settings.backupFrequency}
                      label="Frecuencia de respaldo"
                      onChange={(e) => handleSettingChange('backupFrequency', e.target.value)}
                    >
                      <MenuItem value="daily">Diario</MenuItem>
                      <MenuItem value="weekly">Semanal</MenuItem>
                      <MenuItem value="monthly">Mensual</MenuItem>
                    </Select>
                  </FormControl>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    Retención de Datos
                  </Typography>
                  <TextField
                    fullWidth
                    label="Días de retención"
                    type="number"
                    value={settings.dataRetention}
                    onChange={(e) => handleSettingChange('dataRetention', parseInt(e.target.value))}
                    margin="normal"
                  />
                  <FormControl fullWidth margin="normal">
                    <InputLabel>Formato de exportación</InputLabel>
                    <Select
                      value={settings.exportFormat}
                      label="Formato de exportación"
                      onChange={(e) => handleSettingChange('exportFormat', e.target.value)}
                    >
                      <MenuItem value="xlsx">Excel (.xlsx)</MenuItem>
                      <MenuItem value="csv">CSV (.csv)</MenuItem>
                      <MenuItem value="json">JSON (.json)</MenuItem>
                      <MenuItem value="pdf">PDF (.pdf)</MenuItem>
                    </Select>
                  </FormControl>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Panel de Perfil */}
        <TabPanel value={tabValue} index={4}>
          <Typography variant="h6" gutterBottom>
            Información del Perfil
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Nombre completo"
                value={user?.full_name || ''}
                margin="normal"
                disabled
              />
              <TextField
                fullWidth
                label="Correo electrónico"
                value={user?.email || ''}
                margin="normal"
                disabled
              />
              <TextField
                fullWidth
                label="Rol"
                value={user?.role === 'admin' ? 'Administrador' :
                       user?.role === 'manager' ? 'Gerente' :
                       user?.role === 'analyst' ? 'Analista' : 'Operador'}
                margin="normal"
                disabled
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    Cambiar Contraseña
                  </Typography>
                  <TextField
                    fullWidth
                    label="Contraseña actual"
                    type={showPassword ? 'text' : 'password'}
                    margin="normal"
                    InputProps={{
                      endAdornment: (
                        <IconButton
                          onClick={() => setShowPassword(!showPassword)}
                          edge="end"
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      ),
                    }}
                  />
                  <TextField
                    fullWidth
                    label="Nueva contraseña"
                    type="password"
                    margin="normal"
                  />
                  <TextField
                    fullWidth
                    label="Confirmar nueva contraseña"
                    type="password"
                    margin="normal"
                  />
                  <Button
                    variant="contained"
                    sx={{ mt: 2 }}
                    fullWidth
                  >
                    Actualizar Contraseña
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>
      </Card>

      {/* Dialog para nueva API Key */}
      <Dialog open={apiKeyDialog} onClose={() => setApiKeyDialog(false)}>
        <DialogTitle>Crear Nueva Clave API</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Nombre de la clave"
            fullWidth
            variant="outlined"
            value={newApiKey}
            onChange={(e) => setNewApiKey(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setApiKeyDialog(false)}>Cancelar</Button>
          <Button onClick={() => setApiKeyDialog(false)} variant="contained">
            Crear
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Settings;
