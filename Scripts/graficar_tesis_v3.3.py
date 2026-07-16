import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import torch
import torch.nn as nn
import tkinter as tk
from tkinter import filedialog
import sys

# =====================================================================
# 1. DEFINICIÓN DE LA RED (Debe ser idéntica a la v3.3)
# =====================================================================
class BehaviorCloningPolicy(nn.Module):
    def __init__(self, input_dim=15, output_dim=8):
        super(BehaviorCloningPolicy, self).__init__()
        self.red_neuronal = nn.Sequential(
            nn.Linear(input_dim, 256), nn.ReLU(), nn.Dropout(p=0.1),
            nn.Linear(256, 500), nn.ReLU(), nn.Dropout(p=0.1),
            nn.Linear(500, 128), nn.ReLU(), nn.Dropout(p=0.1),
            nn.Linear(128, output_dim)
        )
    def forward(self, x): 
        return self.red_neuronal(x)

# =====================================================================
# 2. FUNCIÓN PRINCIPAL DE ANÁLISIS
# =====================================================================
def main():
    print("[INFO] Generating 3x3 Validation Matrix (Grouped Legend & Metrics)...")
    
    root = tk.Tk()
    root.withdraw()
    csv_path = filedialog.askopenfilename(title="Select Expert CSV", filetypes=[("CSV Files", "*.csv")])
    if not csv_path: sys.exit()

    modelo = BehaviorCloningPolicy()
    try:
        modelo.load_state_dict(torch.load("xarm5_policy_6D_v3.3.pth", weights_only=True))
        modelo.eval()
        norm_X = np.load('norm_params_X_v3.3.npy', allow_pickle=True).item()
        norm_Y = np.load('norm_params_Y_v3.3.npy', allow_pickle=True).item()
    except Exception as e:
        print(f"[ERROR] Loading weights or normalizers: {e}")
        sys.exit()

    df = pd.read_csv(csv_path, header=0)
    
    # Diferenciales modulares
    df['deltaRoll'] = df['Roll'].diff().fillna(0.0)
    df['deltaRoll'] = (df['deltaRoll'] + 180) % 360 - 180
    df['deltaPitch'] = df['Pitch'].diff().fillna(0.0)
    df['deltaPitch'] = (df['deltaPitch'] + 180) % 360 - 180
    df['deltaYaw'] = df['Yaw'].diff().fillna(0.0)
    df['deltaYaw'] = (df['deltaYaw'] + 180) % 360 - 180
    df = df.iloc[1:].reset_index(drop=True)

    columnas_observacion = ['Fx', 'Fy', 'Fz', 'Tx_EE', 'Ty_EE', 'Tz_EE', 'q1', 'q2', 'q3', 'q4', 'q5', 'F_Amp', 'Beta', 'K_Stiffness', 'Vel_Filt']
    columnas_accion = ['deltaXcmd', 'deltaYcmd', 'deltaZcmd', 'deltaRoll', 'deltaPitch', 'deltaYaw', 'Vel_Filt', 'Acc_Filt']

    X_raw = df[columnas_observacion].to_numpy(dtype=np.float32)
    Y_real_raw = df[columnas_accion].to_numpy(dtype=np.float32)
    tiempo = df['Time_s'].to_numpy(dtype=np.float32) if 'Time_s' in df.columns else np.arange(len(df)) * 0.01

    X_norm = (X_raw - norm_X['mu']) / norm_X['sigma']
    
    # Y_real en espacio normalizado para la Gráfica 9
    Y_real_norm = (Y_real_raw - norm_Y['mu']) / norm_Y['sigma']
    
    with torch.no_grad():
        Y_pred_norm = modelo(torch.FloatTensor(X_norm)).numpy()

    Y_pred_raw = (Y_pred_norm * norm_Y['sigma']) + norm_Y['mu']

    # =====================================================================
    # 5. CREACIÓN DE LA MATRIZ 3x3 DE GRÁFICAS
    # =====================================================================
    plt.rcParams.update({'font.size': 12, 'axes.labelweight': 'normal'})
    fig, axs = plt.subplots(3, 3, figsize=(18, 13))
    fig.suptitle('Behavior Cloning Validation (Inference vs Expert)', fontsize=22, fontweight='bold', y=0.98)
    
    metadata_graficas = [
        {'etiqueta_y': r'$\Delta X$ [mm]'},
        {'etiqueta_y': r'$\Delta Y$ [mm]'},
        {'etiqueta_y': r'$\Delta Z$ [mm]'},
        {'etiqueta_y': r'$\Delta Roll$ [°]'},
        {'etiqueta_y': r'$\Delta Pitch$ [°]'},
        {'etiqueta_y': r'$\Delta Yaw$ [°]'},
        {'etiqueta_y': r'$Vel_{filt}$ [mm/s]'}, 
        {'etiqueta_y': r'$Acc_{filt}$ [mm/s²]'}
    ]

    for i in range(8):
        row, col = i // 3, i % 3
        ax = axs[row, col]
        
        y_real = Y_real_raw[:, i]
        y_pred = Y_pred_raw[:, i]
        
        error_absoluto = np.abs(y_real - y_pred)
        error_cuadratico = (y_real - y_pred)**2
        
        mae_l1 = np.mean(error_absoluto)
        mse_l2 = np.mean(error_cuadratico)
        rmse_val = np.sqrt(mse_l2)
        
        ax.plot(tiempo, y_real, label='Real Output', color='black', alpha=0.75, linewidth=1.8)
        ax.plot(tiempo, y_pred, label='Prediction Output', color='orange', linestyle='--', linewidth=1.5)
        
        ax.set_title("") 
        if row == 2 or (row == 1 and col == 2): 
             ax.set_xlabel('Time [s]', fontsize=12)
        ax.set_ylabel(metadata_graficas[i]['etiqueta_y'], fontsize=12)
        
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        
        # Filtro de ruido
        rango = np.max(np.abs(y_real))
        if rango < 1e-4:
            ax.set_ylim([-0.05, 0.05])
        else:
            min_y, max_y = np.min(y_real), np.max(y_real)
            margen = (max_y - min_y) * 0.15
            ax.set_ylim([min_y - margen, max_y + margen])
            
        ax.grid(True, linestyle=':', alpha=0.6)
        
        # UBICACIÓN AGRUPADA: Leyenda arriba a la derecha
        ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
            
        # UBICACIÓN AGRUPADA: Caja de métricas justo debajo de la leyenda
        texto_metricas = f"L1: {mae_l1:.4f}\nL2: {mse_l2:.4f}\nRMSE: {rmse_val:.4f}"
        props = dict(boxstyle='round', facecolor='white', alpha=0.85, edgecolor='gray')
        # Coordenadas (0.98, 0.70) para anclarlo debajo de la leyenda sin chocar con el borde
        ax.text(0.98, 0.72, texto_metricas, transform=ax.transAxes, fontsize=10, fontweight='bold',
                verticalalignment='top', horizontalalignment='right', bbox=props)

    # -----------------------------------------------------------
    # La 9na Gráfica: L1, L2 y RMSE (NORMALIZADO)
    # -----------------------------------------------------------
    ax9 = axs[2, 2]
    
    drift_norm = np.cumsum(Y_real_norm - Y_pred_norm, axis=0)
    
    error_L2_norm = np.linalg.norm(drift_norm, axis=1)
    error_L1_norm = np.sum(np.abs(drift_norm), axis=1)
    rmse_iterativo_norm = np.sqrt(np.cumsum(error_L2_norm**2) / np.arange(1, len(error_L2_norm) + 1))
    
    ax9.plot(tiempo, error_L1_norm, label='L1 Error', color='purple', linestyle=':', linewidth=1.8, alpha=0.8)
    ax9.plot(tiempo, error_L2_norm, label='L2 Error', color='red', linewidth=1.8)
    ax9.plot(tiempo, rmse_iterativo_norm, label='Cumulative RMSE', color='darkred', linestyle='-.', linewidth=2.0)
    
    ax9.fill_between(tiempo, error_L2_norm, color='red', alpha=0.1)
    
    ax9.set_title("")
    ax9.set_xlabel('Time [s]', fontsize=12)
    ax9.set_ylabel('Normalized Error', fontsize=12) 
    
    ax9.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ax9.grid(True, linestyle=':', alpha=0.6)
    
    # UBICACIÓN LEYENDA GLOBAL: Arriba a la izquierda (porque los datos crecen hacia la derecha)
    ax9.legend(loc='upper left', fontsize=10, framealpha=0.9)

    plt.tight_layout(rect=[0, 0.02, 1, 0.96]) 
    
    nombre_grafica = 'validation_matrix_3x3_Grouped.png'
    plt.savefig(nombre_grafica, dpi=300, bbox_inches='tight')
    print(f"✅ ¡Gráfica de validación con métricas agrupadas guardada como '{nombre_grafica}'!")
    plt.show()

if __name__ == "__main__":
    main()