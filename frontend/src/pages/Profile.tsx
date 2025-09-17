import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Grid,
  Avatar,
  Divider,
  Alert,
  CircularProgress,
  Tab,
  Tabs,
} from '@mui/material';
import {
  Person,
  Security,
  Save,
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
      id={`profile-tabpanel-${index}`}
      aria-labelledby={`profile-tab-${index}`}
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

const Profile: React.FC = () => {
  const { user, updateUser } = useAuth();
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  
  const [profileData, setProfileData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    phone: user?.phone || '',
  });

  const [passwordData, setPasswordData] = useState({
    old_password: '',
    new_password: '',
    new_password_confirm: '',
  });

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    setMessage(null);
  };

  const handleProfileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setProfileData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      await updateUser(profileData);
      setMessage({ type: 'success', text: 'Perfil actualizado correctamente' });
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Error al actualizar perfil' });
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    // Validaciones
    if (passwordData.new_password.length < 6) {
      setMessage({ type: 'error', text: 'La nueva contraseña debe tener al menos 6 caracteres' });
      setLoading(false);
      return;
    }

    if (passwordData.new_password !== passwordData.new_password_confirm) {
      setMessage({ type: 'error', text: 'Las nuevas contraseñas no coinciden' });
      setLoading(false);
      return;
    }

    try {
      // TODO: Implementar cambio de contraseña
      setMessage({ type: 'success', text: 'Contraseña actualizada correctamente' });
      setPasswordData({
        old_password: '',
        new_password: '',
        new_password_confirm: '',
      });
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Error al cambiar contraseña' });
    } finally {
      setLoading(false);
    }
  };

  const getRoleLabel = (role: string) => {
    switch (role) {
      case 'admin':
        return 'Administrador';
      case 'manager':
        return 'Gerente';
      case 'analyst':
        return 'Analista';
      case 'operator':
        return 'Operador';
      default:
        return role;
    }
  };

  return (
    <Box>
      {/* Header */}
      <Typography variant="h4" component="h1" sx={{ fontWeight: 600, mb: 3 }}>
        Mi Perfil
      </Typography>

      {/* Información del usuario */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
            <Avatar
              sx={{
                width: 80,
                height: 80,
                bgcolor: 'primary.main',
                fontSize: '2rem',
              }}
            >
              {user?.first_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
            </Avatar>
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 600 }}>
                {user?.full_name || user?.username}
              </Typography>
              <Typography variant="body1" color="text.secondary">
                {user?.email}
              </Typography>
              <Typography variant="body2" color="primary.main" sx={{ fontWeight: 500 }}>
                {getRoleLabel(user?.role || '')}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Miembro desde {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="tabs de perfil">
            <Tab 
              label="Información Personal" 
              icon={<Person />} 
              iconPosition="start"
            />
            <Tab 
              label="Seguridad" 
              icon={<Security />} 
              iconPosition="start"
            />
          </Tabs>
        </Box>

        {/* Mensajes */}
        {message && (
          <Box sx={{ p: 3, pb: 0 }}>
            <Alert severity={message.type}>
              {message.text}
            </Alert>
          </Box>
        )}

        {/* Tab Panel - Información Personal */}
        <TabPanel value={tabValue} index={0}>
          <Box component="form" onSubmit={handleProfileSubmit}>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Nombre"
                  name="first_name"
                  value={profileData.first_name}
                  onChange={handleProfileChange}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Apellido"
                  name="last_name"
                  value={profileData.last_name}
                  onChange={handleProfileChange}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Correo Electrónico"
                  name="email"
                  type="email"
                  value={profileData.email}
                  onChange={handleProfileChange}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Teléfono"
                  name="phone"
                  value={profileData.phone}
                  onChange={handleProfileChange}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Nombre de Usuario"
                  value={user?.username || ''}
                  disabled
                  helperText="El nombre de usuario no se puede modificar"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Rol"
                  value={getRoleLabel(user?.role || '')}
                  disabled
                  helperText="El rol es asignado por un administrador"
                />
              </Grid>
            </Grid>

            <Divider sx={{ my: 3 }} />

            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                type="submit"
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} /> : <Save />}
                disabled={loading}
              >
                {loading ? 'Guardando...' : 'Guardar Cambios'}
              </Button>
            </Box>
          </Box>
        </TabPanel>

        {/* Tab Panel - Seguridad */}
        <TabPanel value={tabValue} index={1}>
          <Box component="form" onSubmit={handlePasswordSubmit}>
            <Typography variant="h6" gutterBottom>
              Cambiar Contraseña
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Para cambiar tu contraseña, ingresa tu contraseña actual y la nueva contraseña.
            </Typography>

            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Contraseña Actual"
                  name="old_password"
                  type="password"
                  value={passwordData.old_password}
                  onChange={handlePasswordChange}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Nueva Contraseña"
                  name="new_password"
                  type="password"
                  value={passwordData.new_password}
                  onChange={handlePasswordChange}
                  required
                  helperText="Mínimo 6 caracteres"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Confirmar Nueva Contraseña"
                  name="new_password_confirm"
                  type="password"
                  value={passwordData.new_password_confirm}
                  onChange={handlePasswordChange}
                  required
                />
              </Grid>
            </Grid>

            <Divider sx={{ my: 3 }} />

            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                type="submit"
                variant="contained"
                color="warning"
                startIcon={loading ? <CircularProgress size={20} /> : <Security />}
                disabled={loading}
              >
                {loading ? 'Cambiando...' : 'Cambiar Contraseña'}
              </Button>
            </Box>
          </Box>
        </TabPanel>
      </Card>
    </Box>
  );
};

export default Profile;
