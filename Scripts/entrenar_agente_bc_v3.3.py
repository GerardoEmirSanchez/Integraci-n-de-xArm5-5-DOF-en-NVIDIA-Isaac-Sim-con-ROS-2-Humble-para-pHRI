import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from datetime import datetime
import glob
import tkinter as tk
from tkinter import filedialog

class XArmDataset(Dataset):
    def __init__(self, X_data, Y_data):
        self.X = torch.tensor(X_data, dtype=torch.float32)
        self.Y = torch.tensor(Y_data, dtype=torch.float32)
    def __len__(self): return len(self.X)
    def __getitem__(self, idx): return self.X[idx], self.Y[idx]

class BehaviorCloningPolicy(nn.Module):
    def __init__(self):
        super(BehaviorCloningPolicy, self).__init__()
        self.red_neuronal = nn.Sequential(
            nn.Linear(15, 256), nn.ReLU(), nn.Dropout(p=0.1),
            nn.Linear(256, 500), nn.ReLU(), nn.Dropout(p=0.1),
            nn.Linear(500, 128), nn.ReLU(), nn.Dropout(p=0.1),
            nn.Linear(128, 8)
        )
    def forward(self, x): return self.red_neuronal(x)
    
def train_model():
    print("[INFO] Iniciando Entrenamiento BC v3.3 (Doble Norm. + Fix Cinemático + Fix Vector de Acción)...")
    
    root = tk.Tk(); root.withdraw() 
    carpeta_datos = filedialog.askdirectory(title="Selecciona la carpeta de mediciones")
    if not carpeta_datos: return

    try:
        archivos_csv = glob.glob(os.path.join(carpeta_datos, "*.csv"))
        if not archivos_csv: return
            
        lista_x, lista_y = [], []
        columnas_observacion = ['Fx', 'Fy', 'Fz', 'Tx_EE', 'Ty_EE', 'Tz_EE', 'q1', 'q2', 'q3', 'q4', 'q5', 'F_Amp', 'Beta', 'K_Stiffness', 'Vel_Filt']
        
        # EL FIX: El vector de acción correcto según tu tesis
        columnas_accion = ['deltaXcmd', 'deltaYcmd', 'deltaZcmd', 'deltaRoll', 'deltaPitch', 'deltaYaw', 'Vel_Filt', 'Acc_Filt']

        for archivo in archivos_csv:
            df = pd.read_csv(archivo, header=0)
            
            # 1. Cálculo del diferencial de orientación con aritmética modular
            df['deltaRoll'] = df['Roll'].diff().fillna(0.0)
            df['deltaRoll'] = (df['deltaRoll'] + 180) % 360 - 180

            df['deltaPitch'] = df['Pitch'].diff().fillna(0.0)
            df['deltaPitch'] = (df['deltaPitch'] + 180) % 360 - 180

            df['deltaYaw'] = df['Yaw'].diff().fillna(0.0)
            df['deltaYaw'] = (df['deltaYaw'] + 180) % 360 - 180

            # 2. Eliminación de la primera fila (ruido inicial del .diff)
            df = df.iloc[1:].reset_index(drop=True)

            try:
                lista_x.append(df[columnas_observacion].to_numpy(dtype=np.float32))
                lista_y.append(df[columnas_accion].to_numpy(dtype=np.float32))
            except Exception as e: 
                print(f"[ADVERTENCIA] Error leyendo columnas en {archivo}: {e}")
                continue

        X_raw = np.vstack(lista_x)
        Y_raw = np.vstack(lista_y)
        
    except Exception as e: 
        print(f"[ERROR] Hubo un problema general: {e}")
        return

    # ==========================================================
    # NORMALIZACIÓN DE ENTRADAS (X) Y SALIDAS (Y)
    # ==========================================================
    mu_X = np.mean(X_raw, axis=0)
    sigma_X = np.std(X_raw, axis=0) + 1e-8
    X_data = (X_raw - mu_X) / sigma_X
    np.save('norm_params_X_v3.3.npy', {'mu': mu_X, 'sigma': sigma_X})

    mu_Y = np.mean(Y_raw, axis=0)
    sigma_Y = np.std(Y_raw, axis=0) + 1e-8
    Y_data = (Y_raw - mu_Y) / sigma_Y
    np.save('norm_params_Y_v3.3.npy', {'mu': mu_Y, 'sigma': sigma_Y})
    # ==========================================================

    X_train, X_val, Y_train, Y_val = train_test_split(X_data, Y_data, test_size=0.15, random_state=42)
    train_loader = DataLoader(XArmDataset(X_train, Y_train), batch_size=64, shuffle=True)
    val_loader = DataLoader(XArmDataset(X_val, Y_val), batch_size=64, shuffle=False)

    model = BehaviorCloningPolicy()
    criterion = nn.HuberLoss(delta=1.0)
    optimizer = optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=100)

    max_epochs = 10000
    umbral_error = 0.000005       
    train_losses, val_losses = [], []
    best_val_loss = float('inf')

    print("\n[INFO] Ciclo iniciado. Usa 'Ctrl+C' para detener el entrenamiento.\n")
    try:
        for epoch in range(max_epochs):
            model.train()
            running_train_loss = 0.0
            for inputs, targets in train_loader:
                optimizer.zero_grad()
                outputs = model(inputs)
                loss = criterion(outputs, targets)
                loss.backward()
                optimizer.step()
                running_train_loss += loss.item()
            
            model.eval()
            running_val_loss = 0.0
            with torch.no_grad():
                for inputs, targets in val_loader:
                    outputs = model(inputs)
                    running_val_loss += criterion(outputs, targets).item()
            
            avg_train_loss = running_train_loss / len(train_loader)
            avg_val_loss = running_val_loss / len(val_loader)
            train_losses.append(avg_train_loss); val_losses.append(avg_val_loss)
            scheduler.step()

            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss
                torch.save(model.state_dict(), 'xarm5_policy_6D_v3.3.pth')

            print(f"Epoch [{epoch+1}/{max_epochs}] | Train: {avg_train_loss:.6f} | Val: {avg_val_loss:.6f} | Mejor: {best_val_loss:.6f}")
            if best_val_loss <= umbral_error: break

    except KeyboardInterrupt: print(f"\n[INFO] Detenido. Mejor Val Loss guardado: {best_val_loss:.6f}")

    plt.figure(figsize=(10, 5))
    plt.plot(train_losses, label='Train Loss', color='blue')
    plt.plot(val_losses, label='Validation Loss', color='orange')
    plt.title('Curvas de Aprendizaje (v3.3 - Fix Cinemático + Acción)')
    plt.xlabel('Épocas'); plt.ylabel('Huber Loss')
    plt.grid(True, linestyle='--', alpha=0.7); plt.legend()
    plt.savefig(f"training_loss_v3.3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png", dpi=300)
    plt.show()

if __name__ == "__main__": train_model()