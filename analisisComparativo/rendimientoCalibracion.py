import matplotlib.pyplot as plt
import numpy as np

# --- DATOS REALES RTG-008 ---
raw_air_initial = np.array([6043.0, 4971.0, 4821.0, 6454.0])
slopes = np.array([0.008117, 0.006037, 0.006229, 0.006827])
zeros_ground = np.array([3977.0, 3942.0, 3976.0, 3955.0])
TARGET_WEIGHT = 11.2

# --- SIMULACIÓN ---
DAYS = 60
days_axis = np.arange(DAYS)

# Escenario: Celda 4 pierde 5% sensibilidad
sensor_health_c4 = np.linspace(1.0, 0.95, DAYS)

results_legacy = []
results_new_system = []
current_wear_factor = 1.0

for day in range(DAYS):
    # Generar señal fisica degradada
    delta_initial = raw_air_initial - zeros_ground
    health_today = np.array([1.0, 1.0, 1.0, sensor_health_c4[day]])
    raw_measured_today = zeros_ground + (delta_initial * health_today)
    
    # Legacy
    weights_legacy = (raw_measured_today - zeros_ground) * slopes
    if day == 0:
        factor_normalization = TARGET_WEIGHT / np.sum(weights_legacy)
    total_legacy = np.sum(weights_legacy) * factor_normalization
    results_legacy.append(total_legacy)
    
    # New System
    weights_new = (raw_measured_today - zeros_ground) * slopes * factor_normalization * current_wear_factor
    total_new_measured = np.sum(weights_new)
    
    if day > 0:
        ratio = TARGET_WEIGHT / total_new_measured
        # Filtro acelerado para visualización
        current_wear_factor = (current_wear_factor * 0.8) + (ratio * current_wear_factor * 0.2)
        
    results_new_system.append(total_new_measured)

# --- GRAFICAR MEJORADO ---
plt.figure(figsize=(14, 8)) # Más ancho y alto

# Estilos de línea y colores de alto contraste
plt.plot(days_axis, results_legacy, color='#d62728', linewidth=3.5, label='Sistema Actual (Legacy)') # Rojo
plt.plot(days_axis, results_new_system, color='#1f77b4', linewidth=3.5, label='Sistema Propuesto (Auto-Learning)') # Azul
plt.axhline(y=11.2, color='green', linestyle='--', linewidth=2.5, label='Referencia Real (11.2 Ton)', alpha=0.8)

# Configuración de fuentes y títulos
plt.title('Simulación Comparativa: Estabilidad del Dato VGM ante Desgaste de Sensor', fontsize=20, fontweight='bold', pad=20)
plt.xlabel('Días de Operación (Degradación Progresiva del Sensor)', fontsize=16, labelpad=15)
plt.ylabel('Peso Calculado del Spreader (Ton)', fontsize=16, labelpad=15)

# Configuración de los ejes (Ticks)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.grid(True, linestyle='--', alpha=0.6, which='both')

# Leyenda mejorada
plt.legend(fontsize=14, loc='lower left', frameon=True, shadow=True, borderpad=1)

# Anotaciones grandes y claras
bbox_props = dict(boxstyle="round,pad=0.5", fc="white", ec="black", alpha=0.9)
plt.annotate(f'Error Crítico: -{11.2 - results_legacy[-1]:.2f} Ton', 
             xy=(59, results_legacy[-1]), xytext=(35, 10.9),
             fontsize=14, color='#d62728', fontweight='bold',
             arrowprops=dict(facecolor='#d62728', shrink=0.05, width=2),
             bbox=bbox_props)

plt.annotate('Auto-Corrección Activa\n(Estabilidad Garantizada)', 
             xy=(7, results_new_system[7]), xytext=(15, 11.25),
             fontsize=14, color='#1f77b4', fontweight='bold',
             arrowprops=dict(facecolor='#1f77b4', shrink=0.05, width=2),
             bbox=bbox_props)

plt.tight_layout()
plt.savefig('simulacion_comparativa_vgm_hd.png', dpi=300) # Alta resolución
plt.show()
