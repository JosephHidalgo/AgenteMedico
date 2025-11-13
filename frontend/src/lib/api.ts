/**
 * API Service
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ====================================
// TIPOS DE RESPUESTA
// ====================================

export interface Estadisticas {
  exito: boolean;
  citas_hoy: number;
  citas_semana: number;
  total_pacientes: number;
  doctores_activos: number;
}

export interface Cita {
  id: number;
  paciente: number;
  paciente_nombre: string;
  medico: number;
  medico_nombre: string;
  medico_especialidad: string;
  fecha: string;
  hora: string;
  consultorio: string;
  estado: 'AGENDADA' | 'COMPLETADA' | 'CANCELADA' | 'EXPIRADA';
  fecha_registro: string;
}

export interface CitasResponse {
  exito: boolean;
  cantidad: number;
  citas: Cita[];
}

export interface Medico {
  id: number;
  nombre: string;
  apellido_paterno: string;
  nombre_completo: string;
  especialidad: string;
  sub_especialidad: string;
  cedula_profesional: string;
  cedula_especialidad: string;
  anos_experiencia: number;
  universidad: string;
  biografia: string;
  telefono: string;
  email: string;
  direccion: string;
  costo_consulta: string;
  duracion_consulta_minutos: number;
  acepta_nuevos_pacientes: boolean;
  activo: boolean;
}

export interface MedicosResponse {
  exito: boolean;
  cantidad: number;
  medicos: Medico[];
}

// ====================================
// UTILIDADES
// ====================================

/**
 * Función helper para hacer fetch con manejo de errores
 */
async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error(`Error en ${endpoint}:`, error);
    throw error;
  }
}

// ====================================
// SERVICIOS
// ====================================

/**
 * Servicio de Estadísticas
 */
export const estadisticasService = {
  /**
   * Obtiene las estadísticas generales del sistema
   */
  obtener: async (): Promise<Estadisticas> => {
    return fetchAPI<Estadisticas>('/api/estadisticas/');
  },
};

/**
 * Servicio de Citas
 */
export const citasService = {
  /**
   * Lista todas las citas con filtros opcionales
   */
  listar: async (filtros?: {
    estado?: string;
    medico?: number;
    fecha?: string;
    fecha_desde?: string;
    fecha_hasta?: string;
    paciente_email?: string;
  }): Promise<CitasResponse> => {
    const params = new URLSearchParams();
    
    if (filtros) {
      Object.entries(filtros).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString());
        }
      });
    }

    const queryString = params.toString();
    const endpoint = queryString ? `/api/citas/?${queryString}` : '/api/citas/';
    
    return fetchAPI<CitasResponse>(endpoint);
  },

  /**
   * Obtiene el detalle de una cita específica
   */
  obtener: async (id: number) => {
    return fetchAPI(`/api/citas/${id}/`);
  },

  /**
   * Descarga el PDF de una cita
   */
  descargarPDF: async (id: number) => {
    const response = await fetch(`${API_BASE_URL}/api/citas/${id}/pdf/`);
    if (!response.ok) {
      throw new Error('Error al descargar el PDF');
    }
    return response.blob();
  },

  /**
   * Cancela una cita
   */
  cancelar: async (id: number, motivo: string) => {
    return fetchAPI(`/api/citas/${id}/cancelar/`, {
      method: 'POST',
      body: JSON.stringify({ motivo }),
    });
  },
};

/**
 * Servicio de Médicos
 */
export const medicosService = {
  /**
   * Lista todos los médicos activos
   */
  listar: async (): Promise<MedicosResponse> => {
    return fetchAPI<MedicosResponse>('/api/medicos/');
  },

  /**
   * Obtiene los horarios disponibles de un médico
   */
  obtenerHorarios: async (medicoId: number, fecha: string) => {
    return fetchAPI(`/api/medicos/${medicoId}/horarios/?fecha=${fecha}`);
  },
};

// ====================================
// UTILIDADES DE FORMATO
// ====================================

/**
 * Formatea una fecha ISO a formato legible
 * @param fecha - Fecha en formato YYYY-MM-DD
 * @returns Fecha formateada como "1 Nov 2025"
 */
export const formatearFecha = (fecha: string): string => {
  const meses = [
    'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
    'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'
  ];
  
  const [year, month, day] = fecha.split('-');
  const mes = meses[parseInt(month) - 1];
  
  return `${parseInt(day)} ${mes} ${year}`;
};

/**
 * Formatea una hora de 24h a 12h con AM/PM
 * @param hora - Hora en formato HH:MM:SS
 * @returns Hora formateada como "10:00 AM"
 */
export const formatearHora = (hora: string): string => {
  const [hours, minutes] = hora.split(':');
  const h = parseInt(hours);
  const ampm = h >= 12 ? 'PM' : 'AM';
  const h12 = h % 12 || 12;
  
  return `${h12}:${minutes} ${ampm}`;
};

/**
 * Obtiene la fecha de hoy en formato YYYY-MM-DD
 */
export const obtenerFechaHoy = (): string => {
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, '0');
  const day = String(today.getDate()).padStart(2, '0');
  
  return `${year}-${month}-${day}`;
};
