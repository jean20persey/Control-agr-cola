// Interfaces para el sistema de Control Agrícola

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone?: string;
  role: 'admin' | 'manager' | 'operator' | 'analyst';
  is_active: boolean;
  created_at: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  role?: string;
  password: string;
  password_confirm: string;
}

export interface Cultivo {
  id: number;
  nombre: string;
  variedad: string;
  tipo: string;
  ciclo_dias: number;
  rendimiento_esperado: number;
  descripcion?: string;
  temperatura_optima_min?: number;
  temperatura_optima_max?: number;
  ph_suelo_min?: number;
  ph_suelo_max?: number;
  precipitacion_anual?: number;
  activo: boolean;
  fecha_creacion: string;
  fecha_actualizacion: string;
  nombre_completo: string;
  rango_temperatura: string;
  rango_ph: string;
}

export interface Parcela {
  id: number;
  codigo: string;
  nombre: string;
  descripcion?: string;
  area_hectareas: number;
  area_metros_cuadrados: number;
  ubicacion_lat?: number;
  ubicacion_lng?: number;
  ubicacion_completa: string;
  altitud?: number;
  tipo_suelo?: string;
  ph_suelo?: number;
  materia_organica?: number;
  capacidad_campo?: number;
  cultivo_actual?: number;
  cultivo_actual_info?: Cultivo;
  fecha_siembra?: string;
  fecha_cosecha_estimada?: string;
  estado: string;
  tiene_riego: boolean;
  tipo_riego?: string;
  activa: boolean;
  fecha_creacion: string;
  fecha_actualizacion: string;
  tiene_cultivo: boolean;
  dias_desde_siembra?: number;
}

export interface RegistroProduccion {
  id: number;
  parcela: number;
  parcela_info: Parcela;
  cultivo: number;
  cultivo_info: Cultivo;
  fecha_registro: string;
  temporada: string;
  cantidad_kg: number;
  rendimiento_hectarea: number;
  calidad?: string;
  temperatura_promedio?: number;
  precipitacion_mm?: number;
  humedad_relativa?: number;
  desviacion_esperada?: number;
  anomalia_detectada: boolean;
  notas_anomalia?: string;
  porcentaje_desviacion: number;
  eficiencia_rendimiento: number;
  datos_adicionales?: any;
  fecha_creacion: string;
  fecha_actualizacion: string;
}

export interface PrediccionCosecha {
  id: number;
  parcela: number;
  parcela_info: Parcela;
  cultivo: number;
  cultivo_info: Cultivo;
  fecha_prediccion: string;
  temporada_objetivo: string;
  rendimiento_predicho: number;
  confianza_prediccion: number;
  rango_minimo?: number;
  rango_maximo?: number;
  modelo_utilizado: string;
  parametros_modelo?: any;
  rendimiento_real?: number;
  precision_prediccion?: number;
  fecha_creacion: string;
}

export interface DashboardStats {
  total_parcelas: number;
  parcelas_activas: number;
  total_cultivos: number;
  total_registros_produccion: number;
  produccion_total_kg: number;
  rendimiento_promedio: number;
  area_total_hectareas: number;
  area_cultivada_hectareas: number;
  anomalias_detectadas: number;
  porcentaje_anomalias: number;
  distribucion_calidades: Record<string, number>;
  crecimiento_mensual: number;
  eficiencia_promedio: number;
}

export interface KPI {
  nombre: string;
  valor: number;
  unidad: string;
  tendencia: 'up' | 'down' | 'stable';
  cambio_porcentual: number;
  descripcion: string;
}

export interface GraficoData {
  fecha?: string;
  etiqueta?: string;
  valor: number;
  categoria?: string;
  color?: string;
  porcentaje?: number;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

export interface FilterOptions {
  search?: string;
  ordering?: string;
  page?: number;
  page_size?: number;
  [key: string]: any;
}
