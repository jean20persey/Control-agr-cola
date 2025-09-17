import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box, CircularProgress } from '@mui/material';
import { useAuth } from './contexts/AuthContext';

// Componentes de páginas
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Cultivos from './pages/Cultivos';
import Parcelas from './pages/Parcelas';
import Produccion from './pages/Produccion';
import Analisis from './pages/Analisis';
import Profile from './pages/Profile';

// Componentes de layout
import Layout from './components/Layout/Layout';
import ProtectedRoute from './components/ProtectedRoute';

const App: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  // Mostrar spinner mientras se verifica la autenticación
  if (isLoading) {
    return (
      <Box className="flex-center full-height">
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Routes>
      {/* Rutas públicas */}
      <Route 
        path="/login" 
        element={
          isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />
        } 
      />
      <Route 
        path="/register" 
        element={
          isAuthenticated ? <Navigate to="/dashboard" replace /> : <Register />
        } 
      />

      {/* Rutas protegidas */}
      <Route 
        path="/" 
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        {/* Redirigir la raíz al dashboard */}
        <Route index element={<Navigate to="/dashboard" replace />} />
        
        {/* Páginas principales */}
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="cultivos" element={<Cultivos />} />
        <Route path="parcelas" element={<Parcelas />} />
        <Route path="produccion" element={<Produccion />} />
        <Route path="analisis" element={<Analisis />} />
        <Route path="profile" element={<Profile />} />
      </Route>

      {/* Ruta por defecto - redirigir al login si no está autenticado */}
      <Route 
        path="*" 
        element={
          <Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />
        } 
      />
    </Routes>
  );
};

export default App;
