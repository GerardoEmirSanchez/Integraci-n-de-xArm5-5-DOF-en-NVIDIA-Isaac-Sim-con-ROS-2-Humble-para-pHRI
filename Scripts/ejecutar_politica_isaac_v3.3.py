from isaacsim import SimulationApp
simulation_app = SimulationApp({"headless": False}) 

import torch
import numpy as np
import pandas as pd
import os, sys, time
import tkinter as tk
from tkinter import filedialog
from omni.isaac.core import World
from omni.isaac.core.articulations import ArticulationView 
from omni.isaac.core.utils.stage import add_reference_to_stage

class BehaviorCloningPolicy(torch.nn.Module):
    def __init__(self, input_dim=15, output_dim=8):
        super(BehaviorCloningPolicy, self).__init__()
        self.red_neuronal = torch.nn.Sequential(
            torch.nn.Linear(input_dim, 256), torch.nn.ReLU(), torch.nn.Dropout(p=0.1), 
            torch.nn.Linear(256, 500), torch.nn.ReLU(), torch.nn.Dropout(p=0.1),
            torch.nn.Linear(500, 128), torch.nn.ReLU(), torch.nn.Dropout(p=0.1),
            torch.nn.Linear(128, output_dim) 
        )
    def forward(self, state): return self.red_neuronal(state)

print("[INFO] Inicializando IA Autónoma 6D (v3.3)...")
modelo = BehaviorCloningPolicy()

try:
    modelo.load_state_dict(torch.load("xarm5_policy_6D_v3.3.pth", weights_only=True))
    modelo.eval() 
    
    norm_X = np.load('norm_params_X_v3.3.npy', allow_pickle=True).item()
    norm_Y = np.load('norm_params_Y_v3.3.npy', allow_pickle=True).item()
    print("[INFO] Pesos y Doble Normalización cargados.")
except Exception as e:
    print(f"\n[ERROR] Faltan archivos o error al cargar: {e}")
    simulation_app.close(); sys.exit()

root = tk.Tk(); root.withdraw() 
csv_path = filedialog.askopenfilename(title="Selecciona el CSV", filetypes=[("Archivos CSV", "*.csv")])
if not csv_path: simulation_app.close(); sys.exit()

# =====================================================================
# EL FIX: PRE-PROCESAR EL CSV EXPERTO IGUAL QUE EN EL ENTRENAMIENTO
# =====================================================================
df_telemetria = pd.read_csv(csv_path)

df_telemetria['deltaRoll'] = df_telemetria['Roll'].diff().fillna(0.0)
df_telemetria['deltaRoll'] = (df_telemetria['deltaRoll'] + 180) % 360 - 180

df_telemetria['deltaPitch'] = df_telemetria['Pitch'].diff().fillna(0.0)
df_telemetria['deltaPitch'] = (df_telemetria['deltaPitch'] + 180) % 360 - 180

df_telemetria['deltaYaw'] = df_telemetria['Yaw'].diff().fillna(0.0)
df_telemetria['deltaYaw'] = (df_telemetria['deltaYaw'] + 180) % 360 - 180

df_telemetria = df_telemetria.iloc[1:].reset_index(drop=True)
# =====================================================================

world = World(physics_dt=0.01, rendering_dt=0.01)
world.scene.add_default_ground_plane()

add_reference_to_stage(usd_path="/home/gerardo_emir/xarm_ws/src/xarm_ros2/xarm_description/urdf/xarm5.usd", prim_path="/World/xarm5")
xarm_view = ArticulationView(prim_paths_expr="/World/xarm5", name="xarm5_view")
world.scene.add(xarm_view)
world.reset()

q_cmd = np.radians(df_telemetria.iloc[0][['q1', 'q2', 'q3', 'q4', 'q5']].values.astype(float))
initial_positions = np.zeros((1, xarm_view.num_dof))
initial_positions[0, :5] = q_cmd
xarm_view.set_joint_positions(initial_positions)
world.step(render=True)

P_ia = np.zeros(3); P_vic = np.zeros(3)  
historial_trayectorias = []
tiempo_inicio = time.time()

for paso_actual in range(len(df_telemetria)):
    if not simulation_app.is_running(): break
    fila = df_telemetria.iloc[paso_actual]
    
    F_sim = np.array([fila['Fx'], fila['Fy'], fila['Fz']]).astype(float)
    T_sim = np.array([fila['Tx_EE'], fila['Ty_EE'], fila['Tz_EE']]).astype(float)
    joint_positions_deg = np.degrees(xarm_view.get_joint_positions()[0][:5])
    
    estado_crudo = np.concatenate([F_sim, T_sim, joint_positions_deg, [fila['F_Amp'], fila['Beta'], fila['K_Stiffness'], fila['Vel_Filt']]])
    
    # 1. Escalar entradas (X)
    estado_norm = (estado_crudo - norm_X['mu']) / norm_X['sigma']
    
    with torch.no_grad():
        accion_norm = modelo(torch.FloatTensor(estado_norm)).numpy()
        
    # 2. Des-escalar predicciones (Y)
    accion_real = (accion_norm * norm_Y['sigma']) + norm_Y['mu']
        
    deltas_xyz_mm = accion_real[0:3]
    deltas_rpy_deg = accion_real[3:6]
    
    P_ia += deltas_xyz_mm
    # Usamos los deltas corregidos que calculamos al principio
    P_vic += np.array([fila['deltaXcmd'], fila['deltaYcmd'], fila['deltaZcmd']])
    
    historial_trayectorias.append({
        'tiempo': fila.get('Time_s', paso_actual * 0.01),
        'ia_x': P_ia[0], 'ia_y': P_ia[1], 'ia_z': P_ia[2],
        'vic_x': P_vic[0], 'vic_y': P_vic[1], 'vic_z': P_vic[2]
    })
    
    delta_6D = np.zeros(6)
    delta_6D[0:3] = deltas_xyz_mm / 1000.0  
    delta_6D[3:6] = np.radians(deltas_rpy_deg) 
    
    J_full = xarm_view.get_jacobians()[0][-1, 0:6, :5] 
    delta_q_rad = np.linalg.pinv(J_full, rcond=1e-2) @ delta_6D
    
    q_cmd += delta_q_rad
    target_pos = np.zeros((1, xarm_view.num_dof))
    target_pos[0, :5] = q_cmd
    xarm_view.set_joint_position_targets(target_pos)
    
    if paso_actual % 100 == 0: print(f"[{paso_actual}] Evaluando... Fz: {F_sim[2]:.2f} N")
    world.step(render=True)

df_resultados = pd.DataFrame(historial_trayectorias)
df_resultados.to_csv("resultados_sim_to_sim.csv", index=False)
simulation_app.close()