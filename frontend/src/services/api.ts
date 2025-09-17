import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { AuthTokens } from '../interfaces';

class ApiService {
  private api: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
    
    this.api = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor para agregar token de autenticación
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Interceptor para manejar respuestas y errores
    this.api.interceptors.response.use(
      (response: AxiosResponse) => {
        return response;
      },
      async (error) => {
        const originalRequest = error.config;

        // Si el token expiró, intentar renovarlo
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
              const response = await axios.post(`${this.baseURL}/auth/refresh/`, {
                refresh: refreshToken,
              });

              const { access } = response.data;
              localStorage.setItem('access_token', access);

              // Reintentar la petición original
              originalRequest.headers.Authorization = `Bearer ${access}`;
              return this.api(originalRequest);
            }
          } catch (refreshError) {
            // Si no se puede renovar el token, redirigir al login
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');
            window.location.href = '/login';
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // Métodos de autenticación
  async login(email: string, password: string) {
    const response = await this.api.post('/auth/login/', { email, password });
    return response.data;
  }

  async register(userData: any) {
    const response = await this.api.post('/auth/register/', userData);
    return response.data;
  }

  async getUserProfile() {
    const response = await this.api.get('/auth/profile/');
    return response.data;
  }

  async updateProfile(userData: any) {
    const response = await this.api.put('/auth/profile/', userData);
    return response.data;
  }

  async changePassword(passwordData: any) {
    const response = await this.api.post('/auth/change-password/', passwordData);
    return response.data;
  }

  // Métodos para cultivos
  async getCultivos(params?: any) {
    const response = await this.api.get('/cultivos/', { params });
    return response.data;
  }

  async getCultivo(id: number) {
    const response = await this.api.get(`/cultivos/${id}/`);
    return response.data;
  }

  async createCultivo(cultivoData: any) {
    const response = await this.api.post('/cultivos/', cultivoData);
    return response.data;
  }

  async updateCultivo(id: number, cultivoData: any) {
    const response = await this.api.put(`/cultivos/${id}/`, cultivoData);
    return response.data;
  }

  async deleteCultivo(id: number) {
    const response = await this.api.delete(`/cultivos/${id}/`);
    return response.data;
  }

  async getCultivosStats() {
    const response = await this.api.get('/cultivos/stats/');
    return response.data;
  }

  async getCultivosTipos() {
    const response = await this.api.get('/cultivos/tipos/');
    return response.data;
  }

  // Métodos para parcelas
  async getParcelas(params?: any) {
    const response = await this.api.get('/parcelas/', { params });
    return response.data;
  }

  async getParcela(id: number) {
    const response = await this.api.get(`/parcelas/${id}/`);
    return response.data;
  }

  async getParcelaPorCodigo(codigo: string) {
    const response = await this.api.get(`/parcelas/codigo/${codigo}/`);
    return response.data;
  }

  async createParcela(parcelaData: any) {
    const response = await this.api.post('/parcelas/', parcelaData);
    return response.data;
  }

  async updateParcela(id: number, parcelaData: any) {
    const response = await this.api.put(`/parcelas/${id}/`, parcelaData);
    return response.data;
  }

  async deleteParcela(id: number) {
    const response = await this.api.delete(`/parcelas/${id}/`);
    return response.data;
  }

  async asignarCultivo(parcelaId: number, cultivoData: any) {
    const response = await this.api.post(`/parcelas/${parcelaId}/asignar-cultivo/`, cultivoData);
    return response.data;
  }

  async cosecharParcela(parcelaId: number, cosechaData: any) {
    const response = await this.api.post(`/parcelas/${parcelaId}/cosechar/`, cosechaData);
    return response.data;
  }

  async getParcelasStats() {
    const response = await this.api.get('/parcelas/stats/');
    return response.data;
  }

  // Métodos para producción
  async getRegistrosProduccion(params?: any) {
    const response = await this.api.get('/produccion/registros/', { params });
    return response.data;
  }

  async getRegistroProduccion(id: number) {
    const response = await this.api.get(`/produccion/registros/${id}/`);
    return response.data;
  }

  async createRegistroProduccion(registroData: any) {
    const response = await this.api.post('/produccion/registros/', registroData);
    return response.data;
  }

  async updateRegistroProduccion(id: number, registroData: any) {
    const response = await this.api.put(`/produccion/registros/${id}/`, registroData);
    return response.data;
  }

  async deleteRegistroProduccion(id: number) {
    const response = await this.api.delete(`/produccion/registros/${id}/`);
    return response.data;
  }

  async getAnomalias() {
    const response = await this.api.get('/produccion/registros/anomalias/');
    return response.data;
  }

  async getEstadisticasTemporada(temporada: string) {
    const response = await this.api.get(`/produccion/estadisticas/temporada/${temporada}/`);
    return response.data;
  }

  async getSerieTemporalParcela(parcelaId: number, params?: any) {
    const response = await this.api.get(`/produccion/series-temporales/parcela/${parcelaId}/`, { params });
    return response.data;
  }

  // Métodos para predicciones
  async getPredicciones(params?: any) {
    const response = await this.api.get('/produccion/predicciones/', { params });
    return response.data;
  }

  async crearPrediccion(prediccionData: any) {
    const response = await this.api.post('/produccion/predicciones/crear/', prediccionData);
    return response.data;
  }

  async validarPrediccion(prediccionId: number, validacionData: any) {
    const response = await this.api.post(`/produccion/predicciones/${prediccionId}/validar/`, validacionData);
    return response.data;
  }

  // Métodos para análisis
  async getEstadisticasGenerales() {
    const response = await this.api.get('/analisis/estadisticas-generales/');
    return response.data;
  }

  async compararVariedades(comparacionData: any) {
    const response = await this.api.post('/analisis/comparar-variedades/', comparacionData);
    return response.data;
  }

  async clasificarRendimiento(clasificacionData: any) {
    const response = await this.api.post('/analisis/clasificar-rendimiento/', clasificacionData);
    return response.data;
  }

  async analizarSerieTemporal(analisisData: any) {
    const response = await this.api.post('/analisis/analizar-serie-temporal/', analisisData);
    return response.data;
  }

  // Métodos para dashboard
  async getDashboardCompleto() {
    const response = await this.api.get('/dashboard/');
    return response.data;
  }

  async getDashboardStats() {
    const response = await this.api.get('/dashboard/stats/');
    return response.data;
  }

  async getDashboardKPIs() {
    const response = await this.api.get('/dashboard/kpis/');
    return response.data;
  }

  async getDashboardGraficos() {
    const response = await this.api.get('/dashboard/graficos/');
    return response.data;
  }

  async getDashboardAlertas() {
    const response = await this.api.get('/dashboard/alertas/');
    return response.data;
  }

  // Método genérico para peticiones personalizadas
  async request(method: string, url: string, data?: any, params?: any) {
    const response = await this.api.request({
      method,
      url,
      data,
      params,
    });
    return response.data;
  }
}

export default new ApiService();
