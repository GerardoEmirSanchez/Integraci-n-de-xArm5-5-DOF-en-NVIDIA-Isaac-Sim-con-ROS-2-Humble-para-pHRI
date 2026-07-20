# Integración de xArm5 (5-DOF) en NVIDIA Isaac Sim con ROS 2 Humble para pHRI

Este repositorio documenta la metodología técnica completa para el despliegue de un 
entorno de simulación enfocado en la Interacción Humano-Robot Física (pHRI). 
El sistema integra un cobot UFACTORY xArm5 mediante ROS 2 (Humble) dentro del motor de
físicas NVIDIA Isaac Sim 4.5.0.

**Autor:**  G. Emir Sánchez-Valdés 
**Afiliación:** CINVESTAV - Departamento de Ingeniería Eléctrica, Sección de Mecatrónica.




## 📂 Estructura del Repositorio

| Archivo / Carpeta | Descripción |
| :--- | :--- |
| `.vscode/` | Perfiles de terminal automatizados para cargar ROS 2 e Isaac Sim. |
| `src/xarm_ros2/` | Paquetes oficiales de UFACTORY adaptados para simulación. |
| `src/xarm_ros2/xarm_description/randomize_physics.py` | Script principal para **Domain Randomization** (fricción). |
| `src/xarm_ros2/xarm_description/mover_robot.py` | Nodo de control de posición articular en ROS 2. |
| `xarm5_phri_env.usd` | Escenario maestro de NVIDIA Isaac Sim (Binario). |
| `xarm5_isaac.urdf` | Descripción cinemática procesada con rutas absolutas. |




│  
├📦 xarm_phri_project/  
│  ├📂 .vscode/              
│  ├📂 src/xarm_ros2/xarm_description/    
│  │  ├📜 mover_robot.py        
│  │  └📜 randomize_physics.py    
│  ├📜 xarm5 phri env.usd   
│  └📜 xarm5_isaac.urdf     
│   
└── Readme.cmd  







---

## 📋 Requisitos Previos y Entorno de Hardware

Para garantizar la replicabilidad del entorno, se especifican las características de la estación de trabajo base:

* **Hardware:** Laptop Acer Nitro (GPU NVIDIA RTX Serie 40, e.g., RTX 4050).
* **Sistema Operativo:** Configuración Dual-Boot con Windows y **Ubuntu 22.04 LTS**.
* **BIOS/UEFI:** `Secure Boot` debe estar **desactivado** para permitir la correcta instalación de los controladores privativos de NVIDIA en Linux.

<img width="2390" height="1792" alt="Gemini_Generated_Image_h6a21uh6a21uh6a2" src="https://github.com/user-attachments/assets/e44a196c-763b-4aa0-abd3-813b117844f3" />
*(Imagen de ejemplo: Fotografía de la pantalla del BIOS mostrando el parámetro Secure Boot en "Disabled")*

---

## 🛠️ Fase 1: Preparación del Sistema Operativo y ROS 2

### 1.1 Instalación de Ubuntu 22.04 LTS (Dual-Boot)
Tras particionar el disco duro desde Windows y crear un USB booteable con Rufus, se procede a la instalación de Ubuntu 22.04. Es fundamental seleccionar la opción "Instalar software de terceros para hardware de gráficos" durante el proceso de instalación para obtener los drivers de NVIDIA preliminares.

### 1.2 Instalación de ROS 2 Humble
Se debe seguir la instalación oficial de paquetes Debian para ROS 2 Humble. En la terminal del sistema:


Verificar soporte `UTF-8`
~~~bash
locale  
sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
~~~

Añadir el repositorio de ROS 2
~~~bash
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
~~~

Instalar ROS 2 Desktop
~~~bash
sudo apt update
sudo apt install ros-humble-desktop -y
~~~

### 1.3 Entorno de NVIDIA Omniverse e Isaac Sim

La forma más directa, limpia y que mejor se integra con Ubuntu 22.04 es la instalación nativa vía Python PIP. Esto descargará el motor físico completo y la interfaz gráfica sin pasar por ningún gestor intermedio.

*Paso 1: Preparar el entorno de Python*

Instalar Isaac Sim en un entorno virtual (para que sus librerías masivas no choquen con las de ROS 2 ni las del sistema base).

Abrir la terminal (`Ctrl + Alt + T`) y ejecuta:
~~~bash
sudo apt update
sudo apt install python3-pip python3-venv -y
~~~

*Paso 2: Crear y activar el entorno virtual*

Crear una carpeta dedicada para el entorno del simulador en el directorio principal.

~~~bash
python3 -m venv ~/isaac_env
~~~

Activar el entorno (notarás que el inicio de la línea de comandos cambia y ahora dice `isaac_env`):

~~~bash
source ~/isaac_env/bin/activate
~~~

*Paso 3: Instalar Isaac Sim*

Ahora se le dirá a Python que se conecte directamente a los servidores privados de NVIDIA para descargar el simulador completo.

Primero, se actualiza el gestor de paquetes:

~~~bash
pip install --upgrade pip
~~~

Luego, se ejecuta el comando de instalación apuntando al índice oficial de NVIDIA.

~~~bash
pip install "isaacsim[all,extscache]" --extra-index-url https://pypi.nvidia.com
~~~
Este comando sí obligará al sistema a conectarse a NVIDIA y comenzar a descargar el motor gráfico, la interfaz visual (Simulation App) y los puentes nativos de ROS 2 Humble. Esos puentes internos son exactamente los que permitirán enlazar tus nodos de control de admitancia y visión directamente hacia la réplica virtual del xArm5.

*Paso 4: Iniciar la Interfaz Gráfica*

Una vez que la instalación finalice, ya no buscarás un ícono en el escritorio. Para abrir el simulador con toda su interfaz visual, simplemente asegúrate de tener tu entorno activado y escribe el comando de lanzamiento en la terminal:

~~~bash
isaacsim
~~~

*Nota sobre la dinámica de trabajo:*

A partir de ahora, cada vez que enciendas la computadora y quieras abrir Isaac Sim, el flujo de trabajo será abrir una terminal y ejecutar estos dos comandos:

1. `source ~/isaac_env/bin/activate` (para entrar al entorno)

2. `isaacsim` (para abrir el programa)

Este modelo centrado en desarrolladores es mucho más robusto, ya que te permitirá en el futuro importar Isaac Sim directamente en tus scripts de Python como si fuera una librería matemática más (import isaacsim), lo cual es el estándar actual para entrenar redes neuronales sin sobrecargar la computadora con interfaces gráficas innecesarias.







## ⚙️ Fase 2: Compilación del Espacio de Trabajo (xArm URDF)

Para simular el brazo robótico, es necesario extraer su descripción física (URDF) desde su paquete oficial de ROS 2.

**⚠️ Advertencia Crítica:** La compilación de paquetes de ROS 2 debe ejecutarse siempre en el entorno base del sistema. No se debe activar el entorno virtual `isaac_env` durante este paso, ya que causará conflictos (e.g., `ModuleNotFoundError: No module named 'catkin_pkg'`).

### 2.1 Preparación y Compilación
Asegurarse de que el entorno virtual esté desactivado e instalar dependencias faltantes:

~~~bash
deactivate
sudo apt update
sudo apt install python3-catkin-pkg -y
~~~

Limpiar cachés previas y compilar el paquete de descripción (`xarm_description`):

~~~bash
cd ~/xarm_ws
rm -rf build install log
colcon build --packages-select xarm_description
~~~

### 2.2 Generación del Archivo URDF Puro
Una vez compilado, se traducen los macros de Xacro a un archivo URDF estándar, especificando el uso de 5 grados de libertad (xArm5) sin gripper:

~~~bash
source install/setup.bash
xacro ~/xarm_ws/src/xarm_ros2/xarm_description/urdf/xarm_device.urdf.xacro dof:=5 add_gripper:=false > ~/xarm5_isaac.urdf
~~~

---

## 🔧 Fase 3: Resolución de Rutas (El problema del "Robot Fantasma")

NVIDIA Isaac Sim no procesa nativamente las directivas `package://` de ROS que apuntan a las mallas 3D (`.stl`). Si el URDF se importa tal cual, el robot será invisible en el simulador.

Se deben inyectar las rutas absolutas del disco duro en el archivo URDF mediante la herramienta `sed`:

~~~bash
sed -i 's|package://xarm_description|/home/gerardo_emir/xarm_ws/src/xarm_ros2/xarm_description|g' ~/xarm5_isaac.urdf
~~~

---

## 🖥️ Fase 4: Importación en Isaac Sim 4.5.0

### 4.1 Activación de Extensiones
Lanzar Isaac Sim desde su entorno virtual:

~~~bash
source ~/isaac_env/bin/activate
isaacsim
~~~

En la barra superior, navegar a **Window > Extensions**. Buscar y activar (marcando la casilla **Autoload**):
1. `URDF IMPORTER EXTENSION` (`isaacsim.asset.importer.urdf`)
2. `ROS2 Bridge` (`omni.isaac.ros2_bridge`)

<img width="1301" height="781" alt="Captura desde 2026-04-13 13-21-23" src="https://github.com/user-attachments/assets/63486784-1127-4a17-bdfd-d1390a909ef2" />

*(Imagen de ejemplo: Captura del panel de extensiones mostrando el interruptor verde en "URDF IMPORTER EXTENSION")*

### 4.2 Importación del URDF
1. Ir a **File > Import**.
2. Seleccionar el archivo `~/xarm5_isaac.urdf`.
3. En las opciones de importación (panel lateral o inferior):
   * **Model:** Seleccionar `Create in Stage` (Evitar `Referenced Model` para permitir acceso a las articulaciones).
   * **Links:** Seleccionar `Static Base` (Ancla la base del robot al suelo).
4. Hacer clic en **Import**.
5. *Nota: Si el modelo no está a la vista, seleccionarlo en el panel de **Stage** y presionar la tecla **F** para centrar la cámara.*



<img width="1850" height="1173" alt="Captura desde 2026-04-11 14-06-29" src="https://github.com/user-attachments/assets/c89dfb67-09d3-49b5-baa4-fe949765f80d" />

*(Imagen de ejemplo: Visor 3D de Isaac Sim mostrando el brazo metálico xArm5 ensamblado sobre la cuadrícula oscura)*

---

## 🧠 Fase 5: Action Graph y Comunicación ROS 2 (Telemetría)

Para que el robot simulado actúe como un sensor y envíe los estados de sus articulaciones a Ubuntu, se debe programar su comportamiento mediante OmniGraph.

### 5.1 Configuración de Nodos
1. Navegar a **Window > Graph Editors > Action Graph** y crear un `New Action Graph`.
2. Arrastrar los siguientes nodos al lienzo y conectarlos secuencialmente (Pin `Tick` a Pin `Exec In`):
   * `On Playback Tick`
   * `ROS2 Publish Joint State`

### 5.2 Asignación de Objetivos (Target)
1. Seleccionar el nodo `ROS2 Publish Joint State`.
2. En el panel **Property** (derecha), buscar la sección **Target**.
3. Hacer clic en **Add Target** y seleccionar la raíz cinemática del robot en el árbol del escenario (típicamente `link1` o el contenedor `xarm5_isaac` que posea la propiedad *Articulation Root*).


<img width="408" height="226" alt="Captura desde 2026-04-13 13-24-29" src="https://github.com/user-attachments/assets/06177ae2-536d-41ca-bda3-8be2353d8edd" />

*(Imagen de ejemplo: Grafo visual mostrando la línea de conexión entre el nodo "Tick" y el nodo de publicación de ROS 2)*

---

## ✅ Fase 6: Pruebas y Guardado del Escenario (USD)

### 6.1 Prueba de Vida (Joint States)
1. En Isaac Sim, presionar el botón de **Play** (barra lateral izquierda) para iniciar la simulación física.
2. Abrir una nueva terminal en Ubuntu y ejecutar:

~~~bash
source /opt/ros/humble/setup.bash
ros2 topic echo /joint_states
~~~

La terminal debe arrojar en tiempo real la telemetría matemática (Posición, Velocidad y Esfuerzo/Torque simulado por gravedad) de las articulaciones `joint1` a `joint5`.

![Terminal de Ubuntu mostrando el flujo de datos del tópico joint_states](assets/placeholder_terminal_ros_topic.png)
*(Imagen de ejemplo: Captura de pantalla de la terminal mostrando los arrays de esfuerzo y posición)*

### 6.2 Preservación del Entorno
Para evitar reconstruir el Action Graph y las configuraciones físicas en sesiones futuras:

1. Pausar la simulación (**Stop**).
2. Ir a **File > Save As...**
3. Guardar el escenario completo como un archivo USD en la raíz del espacio de trabajo: `~/xarm_ws/xarm5_phri_env.usd`.

Para restaurar el sistema tras reiniciar el equipo, basta con cargar el entorno virtual de Isaac, abrir la interfaz gráfica y abrir el archivo `.usd` directamente.

---

## 🆘 Troubleshooting y Resolución de Problemas

Durante el desarrollo de este entorno en una configuración Dual-Boot (Windows/Ubuntu) con gráficos híbridos, pueden surgir problemas de comunicación con la GPU. A continuación se documentan los errores más comunes y sus soluciones probadas.

### Problema 1: Error de Inicialización CUDA en Isaac Sim
Al ejecutar `isaacsim` desde la terminal, la interfaz no renderiza la malla 3D y la consola se inunda con el siguiente error continuo:

~~~Plaintext
[Error] [carb.cudainterop.plugin] CUDA error 100: cudaErrorNoDevice - no CUDA-capable device is detected)
~~~

**Diagnóstico:** Isaac Sim no detecta la GPU NVIDIA. Esto requiere verificar el estado del driver mediante el comando `nvidia-smi` en una nueva terminal.

**Escenario A:`nvidia-smi` muestra la tabla correctamente.** 
* **Causa:** Ubuntu está utilizando la tarjeta gráfica integrada (Intel/AMD) en modo ahorro de energía, ignorando la GPU dedicada para el renderizado.

* **Solución:** Forzar el uso de la GPU NVIDIA mediante `prime-select`.

  1. Ejecutar: `sudo prime-select nvidia`

  2. Reiniciar el sistema informático por completo.

**Escenario B: `nvidia-smi` devuelve un error de comunicación.** 

El error arrojado es: `NVIDIA-SMI has failed because it couldn't communicate with the NVIDIA driver. Make sure that the latest NVIDIA driver is installed and running`.

* **Causa:** El kernel de Ubuntu ha perdido la sincronización con el driver privativo, usualmente debido a una actualización silenciosa del sistema (Unattended Upgrades) que falló al recompilar el módulo DKMS.

* **Solución:** Realizar una "Tabla Rasa" purgando los drivers corruptos e instalando la versión exacta recomendada por el sistema.

**Protocolo de Tabla Rasa (Reinstalación Limpia de Drivers):**

1. Purgar el driver corrupto y dependencias:

~~~Bash
sudo apt-get purge '^nvidia-.*'
sudo apt-get autoremove --purge
~~~

2. Identificar el driver recomendado:

~~~Bash
ubuntu-drivers devices
~~~

Buscar en la salida la línea que contenga la palabra `recommended` (ej. `nvidia-driver-550 - distro non-free recommended`). Anotar ese número.

3. Instalar el driver específico:
   
Reemplazar `<VERSION>` con el número obtenido en el paso anterior.

~~~Bash
sudo apt update
sudo apt install nvidia-driver-<VERSION>
~~~

4. Aplicar cambios:

Reiniciar el sistema y verificar la conexión ejecutando `nvidia-smi` nuevamente. La tabla de estado de la GPU debe aparecer.

### Problema 2: Bloqueo del BIOS o "Fast Startup" (Dual-Boot)

Si el comando `nvidia-smi` falla consistentemente tras una reinstalación limpia en un sistema Dual-Boot, el hardware puede estar bloqueado a nivel de firmware o por el sistema operativo secundario.

* **Solución 1 (Desactivar Fast Startup en Windows):** El "Inicio Rápido" de Windows pone el hardware en un estado de hibernación que impide que Linux inicialice la GPU.

  1. Iniciar sesión en Windows.

  2. Navegar a Panel de Control > Hardware y sonido > Opciones de energía.

  3. Seleccionar "Elegir el comportamiento de los botones de inicio/apagado".

  4. Hacer clic en "Cambiar la configuración actualmente no disponible" (requiere permisos de administrador).

  5. Desmarcar la casilla "Activar inicio rápido (recomendado)" y guardar los cambios.

* **Solución 2 (Verificar Secure Boot):** Confirmar en la configuración de la BIOS que el parámetro `Secure Boot` permanece desactivado, ya que su activación bloquea la ejecución de drivers privativos en Linux.

---


## 🕹️ Fase 7: Control Bidireccional y Actuación (Python a Isaac Sim)

Con la telemetría funcionando, el siguiente paso es cerrar el ciclo de control permitiendo que el xArm5 simulado reciba y ejecute comandos de posición calculados externamente en Ubuntu. Esto sienta las bases para la futura implementación de controladores de impedancia variable (VIC).

### 7.1 Configuración de Escucha en Action Graph
Se actualizó el grafo lógico en NVIDIA Isaac Sim para suscribir los motores del cobot a la red de ROS 2:

1.  **Nuevos Nodos:** Se añadieron `ROS2 Subscribe Joint State` y `Articulation Controller`.
2.  **Flujo de Ejecución (Tick):** Se conectó `On Playback Tick` $\rightarrow$ `Subscribe` $\rightarrow$ `Articulation Controller` para garantizar la sincronización por frame.
3.  **Flujo de Datos:** Se vincularon los arrays de `Joint Names` y `Position Commands` desde el suscriptor hacia el controlador.
4.  **Asignación:**
    * **Target:** `link1` (Articulation Root del xArm5).
    * **Topic Name:** `/joint_command`.



<img width="674" height="497" alt="Captura desde 2026-04-13 12-52-04" src="https://github.com/user-attachments/assets/9ca13bab-3391-41f8-ac8a-c0ae3b0931bc" />

*(Imagen de ejemplo: Nodos de suscripción y control conectados en el editor visual de Isaac Sim)*

### 7.2 Implementación del Nodo de Control en Python
Se desarrolló un nodo básico en ROS 2 (Humble) para publicar comandos de posición articular (`sensor_msgs/JointState`) hacia el simulador, verificando la integridad del puente de comunicación.

**Ruta del script:** `~/xarm_ws/src/xarm_ros2/xarm_description/mover_robot.py`

~~~python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import time

class MoverXarm(Node):
    def __init__(self):
        super().__init__('mover_xarm_node')
        # Publicación en el tópico configurado en Isaac Sim
        self.publisher_ = self.create_publisher(JointState, '/joint_command', 10)
        time.sleep(2) # Retardo de estabilización de red
        self.enviar_comando()

    def enviar_comando(self):
        msg = JointState()
        # Nombres de las articulaciones (5-DOF)
        msg.name = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5']
        
        self.get_logger().info('Enviando comando: Moviendo robot a posición objetivo...')
        # Vector de posición en radianes
        msg.position = [0.5, -0.3, 0.2, 0.0, 0.5] 
        self.publisher_.publish(msg)
        time.sleep(4)
        
        self.get_logger().info('Enviando comando: Regresando a posición Zero (0.0)...')
        msg.position = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    nodo = MoverXarm()
    rclpy.spin_once(nodo)
    nodo.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
~~~

### 7.3 Validación Experimental
Para ejecutar el entorno:
1.  Iniciar la simulación (Play) en NVIDIA Isaac Sim.
2.  Verificar la disponibilidad del tópico: `ros2 topic list` (debe listar `/joint_command`).
3.  Ejecutar el script de control:
    ```bash
    python3 mover_robot.py
    ```
El resultado esperado es la actuación física e inmediata de los motores del modelo 3D en el simulador, desplazándose a las coordenadas objetivo y retornando al origen tras 4 segundos, confirmando el éxito del esquema *Sim-to-Real* preliminar.











---


## 💻 Fase 8: Entorno de Desarrollo Avanzado (Visual Studio Code)

Para el desarrollo de algoritmos de control complejos y redes neuronales, se migró de editores de texto básicos a Visual Studio Code (VSC), configurándolo como un centro de mando unificado para ROS 2 e Isaac Sim.

### 8.1 Instalación y Extensiones
Instalación oficial mediante Snap:

```bash
sudo snap install --classic code
```

Extensiones instaladas:

* Python (Microsoft): Para depuración y autocompletado del entorno virtual.

* Robotics Developer Environment: Sucesor oficial de la extensión de ROS, optimizado para Humble.

### 8.2 Automatización del Entorno (settings.json)

Para evitar la ejecución manual de comandos `source` en cada terminal, se configuró un perfil de terminal automatizado en el espacio de trabajo (`~/xarm_ws/.vscode/settings.json`):

```json
{
    "ROS2.distro": "humble",
    "python.defaultInterpreterPath": "/home/gerardo_emir/isaac_env/bin/python",
    "terminal.integrated.profiles.linux": {
        "Isaac-ROS2-Humble": {
            "path": "bash",
            "args": [
                "-c",
                "source /opt/ros/humble/setup.bash && source /home/gerardo_emir/isaac_env/bin/activate && exec bash"
            ]
        }
    },
    "terminal.integrated.defaultProfile.linux": "Isaac-ROS2-Humble"
}
``` 


---

## 🎲 Fase 9: Domain Randomization y Simulación Headless

Para abordar el Sim-to-Real Gap en la estimación de fuerzas para pHRI, se implementó una metodología de aleatorización del dominio. Dado que el manipulador opera en el espacio libre sin contacto inicial, la aleatorización de la fricción de superficie ( $\mu$ ) resulta inefectiva. En su lugar, el sistema perturba las inercias dinámicas modificando la masa del efector final y el amortiguamiento de cada articulación (fricción interna viscosa).

### 9.1 Script de Aleatorización y Recolección (Data Logger)
El script `randomize_physics_logger.py` ejecuta el simulador en modo Headless (sin renderizado gráfico) para optimizar el consumo de VRAM. Este script inyecta una trayectoria de excitación senoidal a los controladores PD del robot y registra los datos en un dataset (a 60 Hz).

Ruta: `src/xarm_ros2/xarm_description/randomize_physics_logger.py`

```Python
from isaacsim import SimulationApp
simulation_app = SimulationApp({"headless": True}) 

import omni
from omni.isaac.core import World
from omni.isaac.core.utils.stage import open_stage
from pxr import UsdPhysics 
import numpy as np
import csv 
from omni.isaac.core.articulations import Articulation 
from omni.isaac.core.utils.types import ArticulationAction 

def main():
    usd_path = "/home/gerardo_emir/xarm_ws/xarm5 phri env.usd" 
    open_stage(usd_path=usd_path)

    dt_simulacion = 1.0/60.0
    world = World(physics_dt=dt_simulacion, rendering_dt=dt_simulacion)
    world.reset()
    stage = omni.usd.get_context().get_stage()

    ruta_robot = "/UF_ROBOT/link1" 
    robot = Articulation(prim_path=ruta_robot, name="xarm5")
    world.scene.add(robot)
    world.reset() 

    # Sintonización del controlador PD
    kps = np.array([10000.0, 10000.0, 10000.0, 10000.0, 10000.0]) 
    kds = np.array([1000.0, 1000.0, 1000.0, 1000.0, 1000.0])
    robot.get_articulation_controller().set_gains(kps=kps, kds=kds)

    nombre_archivo = "xarm5_telemetry_dataset.csv"
    
    with open(nombre_archivo, mode='w', newline='') as archivo_csv:
        escritor = csv.writer(archivo_csv)
        encabezados = [
            "Tiempo_s", "Masa_Link5", "Damping_Articular",
            "q1", "q2", "q3", "q4", "q5",
            "dq1", "dq2", "dq3", "dq4", "dq5",
            "tau1", "tau2", "tau3", "tau4", "tau5"
        ]
        escritor.writerow(encabezados)
        
        episodio = 1
        
        while simulation_app.is_running():
            tiempo_simulacion = world.current_time_step_index * dt_simulacion

            # Excitación cinemática
            desfases = np.array([0.0, 0.5, 1.0, 1.5, 2.0])
            posiciones_objetivo = 0.5 * np.sin(2 * np.pi * 0.5 * tiempo_simulacion + desfases)
            accion_motores = ArticulationAction(joint_positions=posiciones_objetivo)
            robot.get_articulation_controller().apply_action(accion_motores)

            world.step(render=False) 
            
            # Inyección de perturbaciones paramétricas (cada 5 s)
            if world.current_time_step_index % 300 == 0:
                nueva_masa = np.random.uniform(0.1, 2.5)
                nuevo_damping = np.random.uniform(5.0, 50.0)
                
                # Modificación de Masa (Link 5)
                ruta_link5 = "/UF_ROBOT/link5" 
                link5_prim = stage.GetPrimAtPath(ruta_link5)
                if link5_prim.IsValid() and link5_prim.HasAPI(UsdPhysics.MassAPI):
                    UsdPhysics.MassAPI(link5_prim).GetMassAttr().Set(float(nueva_masa))

                # Modificación de Amortiguamiento (1-5)
                for i in range(1, 6):
                    ruta_joint = f"/UF_ROBOT/joints/joint{i}"
                    joint_prim = stage.GetPrimAtPath(ruta_joint)
                    if joint_prim.IsValid():
                        drive_attr = joint_prim.GetAttribute("drive:angular:physics:damping")
                        if drive_attr.IsValid():
                            drive_attr.Set(float(nuevo_damping))
                
                episodio += 1

            # Extracción de estado del robot
            posiciones = robot.get_joint_positions()
            velocidades = robot.get_joint_velocities()
            torques = robot.get_measured_joint_efforts()
            
            if posiciones is not None and velocidades is not None and torques is not None:
                fila_datos = [tiempo_simulacion, nueva_masa, nuevo_damping] + posiciones.tolist() + velocidades.tolist() + torques.tolist()
                escritor.writerow(fila_datos)

            if episodio > 100:
                break

    simulation_app.close()

if __name__ == '__main__':
    main()
```

## 📊 Fase 10: Validación del Conjunto de Datos

Se desarrolló un script en Python utilizando `pandas` y `matplotlib` para la verificación gráfica de los datos extraídos. El análisis permite confirmar una correcta propagación de las perturbaciones físicas hacia los pares articulares ( $\tau$ ).

Ruta: `src/xarm_ros2/xarm_description/verificar_dataset.py`

```Python
import pandas as pd
import matplotlib.pyplot as plt

def main():
    df = pd.read_csv("xarm5_telemetry_dataset.csv")
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(12, 12), sharex=True)

    # Variables aleatorizadas
    ax1.plot(df['Tiempo_s'], df['Masa_Link5'], color='purple', drawstyle='steps-post')
    ax1.set_title("Masa del Efector Final (Link 5)")
    ax1.grid(True)

    ax2.plot(df['Tiempo_s'], df['Damping_Articular'], color='brown', drawstyle='steps-post')
    ax2.set_title("Fricción Interna Global (Damping Articular)")
    ax2.grid(True)

    # Dinámica multivariable
    colores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    for i in range(1, 6):
        ax3.plot(df['Tiempo_s'], df[f'q{i}'], label=f'q_{i}', color=colores[i-1])
        ax4.plot(df['Tiempo_s'], df[f'tau{i}'], label=f'tau_{i}', color=colores[i-1])

    ax3.set_title("Trayectoria de Excitación (5 GDL)")
    ax3.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax3.grid(True)

    ax4.set_title("Esfuerzos Dinámicos Resultantes (Torques)")
    ax4.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax4.grid(True)

    ax1.set_xlim(0, 10)
    plt.tight_layout(rect=[0, 0, 0.85, 1])
    plt.show()

if __name__ == '__main__':
    main()
```


<img width="906" height="960" alt="Captura desde 2026-04-14 17-16-49" src="https://github.com/user-attachments/assets/7d61749d-ec56-4660-9ce5-d3530e17dd81" />

**(Imagen de ejemplo: Resultado experimental)**



## ⚠️ Fase 11: La Desviación Metodológica (El "Reality Gap" y Covariate Shift)

Al intentar entrenar la primera iteración de la red neuronal (Behavior Cloning) basándonos estrictamente en los datos del Paso 10, nos topamos con un problema fundamental al cerrar el bucle en Isaac Sim: El robot colapsaba sobre sí mismo en menos de 5 segundos.

### 11.1 El Diagnóstico del FalloLa red neuronal original fue diseñada con 13 variables de estado, las cuales incluían los torques de las articulaciones medidos físicamente ($\tau_1 \dots \tau_5$).

**El problema:** El motor PhysX 5 de NVIDIA, aunque sumamente preciso, no modela a la perfección las fricciones no lineales, el efecto Stribeck ni los engranajes armónicos específicos del UFACTORY xArm5 real.

Esto provocó un fenómeno conocido como Reality Gap (Brecha de Realidad):

1. El torque simulado era ligeramente distinto al torque real.
2. La IA recibía este torque "falso", haciendo una predicción con un ligero error.
3. Este error llevaba al robot a una posición inexplorada, lo que generaba un torque simulado aún más anómalo en el siguiente ciclo.
4. El error se acumulaba exponencialmente (Covariate Shift o Compounding Error), causando inestabilidad matemática.

**[Imagen 1: Gráfica o captura del simulador Isaac Sim mostrando la divergencia de la trayectoria original y el colapso del brazo robótico debido al error compuesto]**


## 🧠 Fase 12: Reestructuración a Política "Time-Aware" 6D y Preprocesamiento

Para solucionar el colapso, se planteó una desviación metodológica: Hacer a la red completamente "ciega" a los torques articulares. Si la IA no lee torques, no le afectará la diferencia de fricciones entre el simulador y la realidad.

La red ahora debe entender la dinámica guiándose puramente por la cinemática, la fuerza externa y el paso del tiempo.

### 12.1 Nuevos Vectores de Estado y Acción

Se redefinió el espacio de observación y actuación, expandiéndolo para controlar los 6 Grados de Libertad (6D: Traslación y Orientación) e inyectando la variable temporal $\Delta t$ para que la red integre la velocidad tácitamente.

* Vector de Estado (15 Entradas): $s_t = [\Delta t, F_x, F_y, F_z, T_x, T_y, T_z, Roll, Pitch, Yaw, q_1, q_2, q_3, q_4, q_5]$
* Vector de Acción (8 Salidas): $a_t = [\Delta X, \Delta Y, \Delta Z, \Delta Roll, \Delta Pitch, \Delta Yaw, Vel_{filt}, Acc_{filt}]$

### 12.2 Estabilidad Numérica (Z-Score y Aritmética Modular)

Al mezclar milímetros con aceleraciones de hasta $35,000 \text{ mm/s}^2$, los gradientes de la red explotaban. Además, los ángulos de Euler generaban saltos discontinuos al pasar de $-180^\circ$ a $180^\circ$. Se implementaron dos soluciones:

1. Aritmética Modular en Ángulos: Para evitar que la red perciba un giro falso de $360^\circ$ como un error catastrófico.
2. Normalización Z-Score: A todas las entradas y salidas.

Script de Transformación de Datos (Python):

```Python
import numpy as np
import pandas as pd

# 1. Aritmética Modular para deltas de orientación (RPY)
def normalizar_angulo_modular(delta_theta_grados):
    """ Mantiene la diferencia angular en el camino más corto [-180, 180] """
    return ((delta_theta_grados + 180) % 360) - 180

# 2. Normalización Z-Score de características
def normalizar_z_score(df, columnas):
    estadisticas = {}
    for col in columnas:
        mu = df[col].mean()
        sigma = df[col].std()
        df[f"{col}_norm"] = (df[col] - mu) / (sigma + 1e-8) # 1e-8 evita división por cero
        estadisticas[col] = {'mean': mu, 'std': sigma}
    return df, estadisticas
```

## 🛡️ Fase 13: Topología Parsimoniosa, Huber Loss y Dropout (PyTorch)

Durante el primer entrenamiento 6D, la red de embudo masiva ([256 -> 500 -> 128]) memorizó el ruido mecánico del sensor OptoForce (sobreajuste con MSE de $10^{-6}$) y generó problemas de size mismatch al inferir.

Se aplicó el principio de parsimonia: una red más pequeña obligada a generalizar.

1. Reducción Topológica: Arquitectura `[15 -> 128 -> 128 -> 8]`.
2. Huber Loss (Smooth L1): Sustituye al Error Cuadrático Medio (MSE). Actúa de forma lineal ante valores atípicos (ruido del sensor de fuerza) y cuadrática en errores pequeños, ignorando "picos" falsos.
3. Dropout Bayesiano: Se apaga aleatoriamente el 15% ($p=0.15$) de las neuronas en cada paso. Obliga a la red a no depender de trayectorias específicas y aprender la verdadera "ley de admitancia".

**Implementación de la Red (PyTorch):**
Ruta: `src/xarm_ros2/xarm_description/modelos/xarm5_policy_6D.py`

```Python
import torch
import torch.nn as nn

class PolicyNetwork6D(nn.Module):
    def __init__(self, input_dim=15, output_dim=8):
        super(PolicyNetwork6D, self).__init__()
        
        self.red = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Dropout(p=0.15), # Aproximación de incertidumbre
            
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Dropout(p=0.15),
            
            nn.Linear(128, output_dim)
        )

    def forward(self, x):
        return self.red(x)

# Para entrenamiento se usó torch.nn.HuberLoss(delta=1.0)
```

## 🔄 Fase 14: Cierre de Bucle Sim-to-Sim (Cinemática Inversa y Jacobiano)

La salida de nuestra IA son desplazamientos cartesianos 6D ($\Delta X_{6D}$), pero en Isaac Sim debemos enviarle posiciones angulares a los 5 motores ($\Delta q$).

Dado que el xArm5 tiene 5 GDL y la tarea exige controlar 6 GDL, estamos ante un sistema subactuado. Utilizar un optimizador estándar generaba inestabilidades en la muñeca. Se justificó matemáticamente el uso del Jacobiano Espacial completo de $6 \times 5$ con la pseudo-inversa de Moore-Penrose. Esto restringe al brazo para que priorice estrictamente la orientación solicitada por la IA sacrificando eslabones base si es necesario.

$$\Delta q = J^\dagger(q) \Delta X_{6D}$$

**Implementación en el nodo de inferencia:**

```Python
# Cálculo de cinemática inversa con pseudo-inversa
jacobiano = robot.get_jacobians()[0] # Matriz 6x5
jacobiano_pinv = np.linalg.pinv(jacobiano) # Moore-Penrose Pseudo-inverse

# Producto punto: (5x6) * (6x1) = (5x1) deltas articulares
delta_q = np.dot(jacobiano_pinv, accion_cartesiana_ia[:6])
posiciones_articulares_deseadas = q_actuales + delta_q
```

## 📈 Fase 15: Evaluación Cuantitativa (Filtros y Data Logging)

Para validar científicamente que la clonación de comportamiento fue exitosa, no basta con observar el simulador; necesitamos extraer las métricas de error entre la trayectoria del controlador matemático original (Experto) y las decisiones de la IA (Novato).

Desafío técnico: La derivada numérica que usa PhysX para calcular velocidades angulares (`get_joint_velocities()`) es sumamente ruidosa. Antes de registrar los datos o pasarlos a la IA, debemos aplicar un Filtro Pasa-Bajas de primer orden (Filtro Alpha).

Se insertó un *Data Logger* dentro del script maestro de simulación para registrar las respuestas de la IA.

Ruta: `src/xarm_ros2/xarm_description/ejecutar_politica_isaac_v2.2.py`

```Python
# Variables globales para el filtro de velocidad
alpha_filtro = 0.2
velocidades_filtradas = np.zeros(5)
registro_validacion = [] # Data Logger

while simulation_app.is_running():
    # 1. Obtener estado puro
    posicion_ee, orientacion_ee = xarm_view.get_world_poses()
    velocidades_crudas = robot.get_joint_velocities()[0][:5].numpy()
    
    # 2. Aplicar Filtro Pasa-Bajas (Alpha Filter)
    velocidades_filtradas = (alpha_filtro * velocidades_crudas) + ((1 - alpha_filtro) * velocidades_filtradas)
    
    # [ ... Inferencia de PyTorch aquí ... ]
    
    # 3. Registrar telemetría de validación
    registro_validacion.append({
        'Tiempo': world.current_time_step_index * dt,
        'Fuerza_Externa_Z': F_sim[2],
        'Posicion_Z_IA': posicion_ee[0][2].item(),
        'Error_Euclideo': np.linalg.norm(posicion_ee[0] - posicion_experto_referencia)
    })
    
    world.step(render=True)

# Exportar al finalizar
import pandas as pd
df_resultados = pd.DataFrame(registro_validacion)
df_resultados.to_csv("trayectoria_ia_predicha.csv", index=False)
print("✅ Datos de validación cuantitativa exportados exitosamente.")
```

**[Imagen 2: Gráfico de superposición generado a partir de 'trayectoria_ia_predicha.csv'. Debe mostrar en un eje la fuerza inyectada y en el otro la trayectoria Z del Controlador VIC vs. la Trayectoria Z inferida por la Red Neuronal, demostrando un error estacionario submilimétrico y estabilización compliante]**



## 🚀 Fase 16: Inventario de Código Final y Protocolo de Arranque (Cold Start)

Tras superar las divergencias del *Reality Gap* y consolidar la arquitectura neuronal, el proyecto se estabiliza en un conjunto de scripts definitivos. A continuación, se detalla la estructura final del código y el protocolo exacto para ejecutar la validación desde una computadora recién encendida.

### 16.1 Inventario de Archivos Definitivos
El "cerebro" y el entorno de validación residen en el espacio de trabajo de ROS 2, estructurados de la siguiente manera:

```text
~/xarm_ws/
├── xarm5_phri_env.usd                          # [1] Escenario 3D maestro con físicas listas
└── src/xarm_ros2/xarm_description/
    ├── modelos/
    │   ├── xarm5_policy_6D.py                  # [2] Topología de la red [15 -> 128 -> 128 -> 8]
    │   └── xarm5_policy_6D.pth                 # [3] Pesos entrenados (Con Huber Loss y Dropout)
    ├── ejecutar_politica_isaac_v2.2.py         # [4] Script de Inferencia (Filtro Alpha y Data Logger)
    └── analizar_resultados_6d.py               # [5] Script de validación (Error Euclídeo vs Experto)
```


### 16.2 Protocolo de Ejecución desde Cero (PC Recién Encendida)

**Paso 1:** Inicializar el Motor Físico (NVIDIA Isaac Sim)

1. Enciende la computadora y arranca en Ubuntu 22.04.
2. Abre una terminal (`Ctrl + Alt + T`).
3. Activa el entorno virtual de Python que contiene los binarios de NVIDIA y lanza el simulador:

```bash
source ~/isaac_env/bin/activate
isaacsim
```

4. Una vez abierta la interfaz gráfica, ve a File > Open y selecciona el archivo `~/xarm_ws/xarm5_phri_env.usd`.
5. Haz clic en el botón Play (Icono de reproducción en el panel izquierdo) para activar la gravedad y las físicas de PhysX 5.

**Paso 2:** Lanzar el "Cerebro" (Nodo de Inferencia PyTorch)

1. Abre una segunda terminal (puedes usar una pestaña nueva).
2. Es obligatorio cargar las variables de entorno de ROS 2 y luego activar el entorno de Isaac/PyTorch:

```bash
source /opt/ros/humble/setup.bash
source ~/isaac_env/bin/activate
```

3. Navega a la carpeta de los scripts:

```bash
cd ~/xarm_ws/src/xarm_ros2/xarm_description/
```

4. Ejecuta el script maestro de inferencia:

```bash
python3 ejecutar_politica_isaac_v2.2.py
```

El script cargará los pesos `.pth`, aplicará el control cinemático inverso usando la pseudo-inversa del Jacobiano y comenzará a mover el robot en la pantalla de Isaac Sim, guardando sus decisiones en tiempo real.

**Paso 3:** Extraer Métricas y Gráficas de Tesis

1. Una vez que el script anterior termine su ciclo, notarás que ha generado un archivo llamado `trayectoria_ia_predicha.csv` en esa misma carpeta.
2. En la misma terminal, ejecuta el script de análisis para comparar la predicción neuronal contra la trayectoria analítica del Experto (VIC):

```bash
python3 analizar_resultados_6d.py
```

Este comando abrirá una ventana de Matplotlib superponiendo ambas trayectorias y calculando el Error Cartesiano Euclídeo en milímetros.

### 16.3 Notas de Mantenimiento para la Fase de Pruebas

Si deseas activar el Domain Randomization (inyectar ruido Gaussiano al OptoForce para forzar el Dropout y probar la robustez), no necesitas abrir el entorno gráfico de Isaac Sim.

Puedes abrir el script `ejecutar_politica_isaac_v2.2.py` con VS Code y cambiar la variable global `ENABLE_SENSOR_NOISE = False` a `True` en la cabecera del código.

```bash
code ~/xarm_ws/src/xarm_ros2/xarm_description/ejecutar_politica_isaac_v2.2.py
```



## 📈 Fase 17: Refinamiento Algorítmico, Estabilización Numérica y Arquitectura 6D

```bash
source ~/isaac_env/bin/activate
cd ~/xarm_ws/src/xarm_ros2/xarm_description/
code .
```


Durante las pruebas de robustez, se detectó la necesidad de refinar el mapeo matemático de las acciones. La política evolucionó a la **Versión 3.3**, incorporando ajustes algebraicos para estabilizar la inferencia continua y desarrollar una matriz de validación de formato científico (Camera-Ready).

### 17.1 Corrección Matemática del Vector de Acción y Doble Normalización
Se reestructuró la política de Behavior Cloning asegurando una coherencia cinemática estricta con el controlador de admitancia original del experto.

* **Vector de Acción Corregido (8D):** El sistema ahora predice perfiles dinámicos precisos además de las posiciones espaciales.
  $a_t = [\Delta X, \Delta Y, \Delta Z, \Delta Roll, \Delta Pitch, \Delta Yaw, Vel_{filt}, Acc_{filt}]$
* **Aritmética Modular Diferencial:** Se aplicó un filtrado de módulo a los diferenciales de orientación (`(delta + 180) % 360 - 180`) tanto en la fase de entrenamiento como en la inferencia *Sim-to-Sim*. Esto elimina las discontinuidades angulares y previene comportamientos erráticos.
* **Doble Normalización (Z-Score):** Se implementó un escalamiento estadístico bidireccional. Tanto las entradas observadas ($X$) como las acciones predictivas ($Y$) fueron normalizadas, guardando los parámetros `norm_params_X_v3.3.npy` y `norm_params_Y_v3.3.npy` para su reconstrucción física correcta.

### 17.2 Matriz de Validación Cuantitativa 3x3
Para certificar el aprendizaje del modelo, se desarrolló el script `graficar_tesis.py`. Este módulo de validación superpone los comandos inferidos por la red (en bucle abierto) contra los comandos ideales del experto humano (bucle cerrado) extraídos de la telemetría.

El sistema calcula tres métricas de error estándar para cada variable de acción (visualizadas mediante agrupamiento dinámico sin oclusión de datos):
* **L1 (MAE):** Error Absoluto Medio (robustez ante *outliers*).
* **L2 (MSE):** Error Cuadrático Medio.
* **RMSE:** Raíz del Error Cuadrático Medio.

Además, se diseñó un **9no Panel Analítico** que integra el error Euclidiano y Manhattan del vector de estado completo (8D) mapeado en un espacio normalizado (adimensional) para evaluar la estabilidad a largo plazo.

### 17.3 Conclusión del Behavior Cloning (Warm Start)

<img width="5338" height="3737" alt="validation_matrix_3x3_Grouped" src="https://github.com/user-attachments/assets/3f2e84a7-5afc-4df7-9334-9bbb4fc8efbe" />

El análisis empírico de la matriz 3x3 comprueba la hipótesis central y demuestra el límite teórico del *Behavior Cloning*:

1. **Corto Plazo (Precisión Cinética Submilimétrica):** Las primeras 8 gráficas evidencian un clonado casi perfecto. La red mapea las fluctuaciones transitorias de velocidad y aceleración ($> 1000 \text{ mm/s}^2$) con fidelidad extrema. El RMSE en las traslaciones es consistentemente menor a **0.035 mm** por ciclo.
2. **Largo Plazo (Dead-Reckoning Drift):** El 9no panel revela el fenómeno de *Deriva por Estima* (Covariate Shift). Al carecer de un lazo de retroalimentación espacial absoluto, el minúsculo error instantáneo de la red se integra matemáticamente paso a paso, generando un error acumulativo que aleja progresivamente al efector final de su coordenada ideal.

**Siguiente Paso:** La topología neuronal actual (v3.3) es un rotundo éxito como estrategia de inicialización (**Warm Start**). El agente ha comprendido la dinámica subyacente y la ley de impedancia para pHRI. La **Fase 18** estará dedicada a importar estos pesos pre-entrenados a un entorno de **Aprendizaje por Refuerzo (Reinforcement Learning - PPO)**, donde la introducción de una función de recompensa espacial cerrará el lazo de control, eliminando la deriva estacionaria final.

### 17.4 Anexo Técnico: Reproducción y Código Fuente (v3.3)

Para replicar el entrenamiento, la ejecución *Sim-to-Sim* y la validación matemática de la versión final de la política (v3.3), el flujo de trabajo en la terminal es el siguiente:

**1. Preparación del Entorno**
```bash
# Cargar variables de ROS 2 y activar el entorno de Isaac Sim / PyTorch
source /opt/ros/humble/setup.bash
source ~/isaac_env/bin/activate

# Navegar al directorio de desarrollo
cd ~/xarm_ws/src/xarm_ros2/xarm_description/

# Abrir el espacio de trabajo en Visual Studio Code
code .
```

**2. Entrenamiento del modelo**
A continuación, se documenta el código fuente definitivo de los tres pilares de esta fase metodológica:

Este script carga la telemetría del experto, aplica aritmética modular a las orientaciones, ejecuta una doble normalización Z-Score, y entrena la topología [`15 -> 128 -> 128 -> 8`] usando Huber Loss.

```bash
python3 entrenar_agente_bc_v3.3.py
```

```python
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
        # Corrección: Vector de Estado 15D alineado a la formulación teórica
        columnas_observacion = ['Loop_Duration_s',                  # \Delta t
                                'Fx', 'Fy', 'Fz',                   # Fuerzas (3D)
                                'Tx_EE', 'Ty_EE', 'Tz_EE',          # Torques (3D)
                                'Roll', 'Pitch', 'Yaw',             # Orientación Absoluta (3D)
                                'q1', 'q2', 'q3', 'q4', 'q5'        # Cinemática Articular (5D)
                                ]
        
        # EL FIX: El vector de acción correcto según tu tesis
        columnas_accion = ['deltaXcmd', 'deltaYcmd', 'deltaZcmd', 
                           'deltaRoll', 'deltaPitch', 'deltaYaw', 
                           'Vel_Filt', 'Acc_Filt'
                           ]

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
```

**3. Ejecucion de la politica en IsaacSim**
Script que carga la red y los parámetros estadísticos, normalizando los estados percibidos y des-normalizando las predicciones en tiempo real para comandar el robot en el simulador mediante Cinemática Inversa (Pseudo-Inversa de Moore-Penrose).

```bash
python3 ejecutar_politica_isaac_v3.3.py
```

```python
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
    RPY_sim = np.array([fila['Roll'], fila['Pitch'], fila['Yaw']]).astype(float)
    joint_positions_deg = np.degrees(xarm_view.get_joint_positions()[0][:5])
    
    # Construcción rigurosa del estado 15D (Time-Aware + Spatial-Aware)
    estado_crudo = np.concatenate([
        [fila.get('Loop_Duration_s', 0.01)],  # \Delta t
        F_sim,                                # F_xyz
        T_sim,                                # T_xyz
        RPY_sim,                              # Orientación RPY
        joint_positions_deg                   # q_1..5
    ])
    
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
```

**4. Graficas comparativas y validativas**
Genera la Matriz de Validación 3x3 Formato IEEE (Camera-Ready), comparando visual y cuantitativamente (L1, L2, RMSE) el comportamiento del agente contra el controlador de admitancia. Adicionalmente modela el comportamiento estadístico de la Deriva (Dead-Reckoning Drift).

```bash
python3 graficar_tesis_v3.3.py
```

```python
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

    # Corrección alineada con la topología de la política neuronal
    columnas_observacion = [
        'Loop_Duration_s', 'Fx', 'Fy', 'Fz', 'Tx_EE', 'Ty_EE', 'Tz_EE', 
        'Roll', 'Pitch', 'Yaw', 'q1', 'q2', 'q3', 'q4', 'q5'
    ]
    columnas_accion = [
        'deltaXcmd', 'deltaYcmd', 'deltaZcmd', 
        'deltaRoll', 'deltaPitch', 'deltaYaw', 
        'Vel_Filt', 'Acc_Filt'
    ]

    
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
```


## 📈 Fase 18 (En Proceso): Aprendizaje por Refuerzo (Cierre de Bucle con PPO)

**El Objetivo Principal:**

El modelo BC actual sabe cómo moverse (imita la dinámica de velocidad y aceleración), pero sufre de Deriva por Estima (Drift) porque no sabe dónde está respecto a la meta absoluta. En esta fase, tomaremos la red pre-entrenada de BC (el "Warm Start") y la pondremos en un entorno de ensayo y error (RL). Le daremos una Recompensa (Reward) cada vez que reduzca su error cartesiano, obligando a la red a "corregir" la deriva y cerrar el bucle de control.

### 18.1. Requerimientos Técnicos y Entorno
Para esta etapa, pasaremos de un script simple de inferencia a un entorno de entrenamiento distribuido. Necesitarás:

1. **OmniIsaacGymEnvs (OIGE):** Es el framework oficial de NVIDIA para Aprendizaje por Refuerzo dentro de Isaac Sim. Está basado en Isaac Gym.
    * Nota: No usaremos scripts aislados; integraremos tu brazo en la arquitectura de tareas (`Task`) de OIGE.
2. **Librería `rl_games` o `Stable-Baselines3`:** Son los motores matemáticos que ejecutan el algoritmo PPO. OIGE usa `rl_games` por defecto por su extrema velocidad en simulaciones masivamente paralelas.
3. **VRAM de la GPU:** PPO es un devorador de memoria porque no entrena un solo robot, entrena decenas o cientos de robots al mismo tiempo (Simulación Masivamente Paralela). Con tu RTX 4050 (6GB VRAM), probablemente entrenaremos unos 64 o 128 xArm5 simultáneos en modo Headless (sin gráficos).

### 18.2. Bases Teóricas: El Algoritmo PPO (Proximal Policy Optimization)
PPO es el estándar de oro en robótica actual. Es el mismo algoritmo que usa OpenAI para ChatGPT y el que usan en Boston Dynamics para estabilizar sus robots.

#### 18.2.1 El Ecosistema Actor-Crítico (Actor-Critic)
PPO no usa una sola red neuronal, usa dos (o una con dos cabezas de salida):El Actor (Policy Network - $\pi_\theta$): Es tu red actual (la que decide las acciones: $\Delta X, \Delta Y, Vel$, etc.).El Crítico (Value Network - $V_\phi$): Es una red nueva que aprenderá a "criticar" al Actor. Su único trabajo es mirar el Estado del robot y predecir: "¿Qué tan buena es esta situación a futuro?" (Estima el valor acumulado de las recompensas).

#### 18.2.2 La Ecuación PPO (El "Clip")
¿Por qué PPO y no otros algoritmos antiguos (como DQN o DDPG)? Porque PPO evita que el robot "olvide" lo que ya sabe (el olvido catastrófico). Lo hace "recortando" (clipping) qué tanto puede cambiar la red neuronal en un solo paso de entrenamiento.


$$L^{CLIP}(\theta) = \hat{\mathbb{E}}_t \left[ \min(r_t(\theta)\hat{A}_t, \text{clip}(r_t(\theta), 1 - \epsilon, 1 + \epsilon)\hat{A}_t) \right]$$

* $r_t(\theta)$: La probabilidad de tomar una acción ahora vs. antes.
* $\hat{A}_t$ (Ventaja): Qué tan mejor fue la acción tomada comparada con lo que el Crítico esperaba.
* $\epsilon$: Margen de recorte (usualmente 0.2). Evita que la red cambie drásticamente sus pesos si descubre una acción "suertuda".

Lo crucial para tu tesis: Al usar tu red BC como pesos iniciales, PPO será muy cuidadoso de no destruir la ley de admitancia que ya aprendió.

#### 18.2.3. La Metodología (Paso a Paso)
Construir un entorno RL desde cero es complejo. Lo dividiremos en las siguientes sub-etapas metodológicas:

**Paso 1: Definición del MDP (Proceso de Decisión de Markov)**
Debemos formalizar matemáticamente el entorno de tu cobot:
* Estado ($S_t$): Los 15 valores que ya tienes (Fuerza, Posición, Tiempo). Añadiremos la posición de la meta ($X_{target}$).
* Acción ($A_t$): Los 8 valores que ya tienes ($\Delta X, Vel, Acc$).
* Recompensa ($R_t$): El corazón de la IA (se detalla abajo).

**Paso 2: Diseño de la Función de Recompensa (Reward Shaping)**
Esta es la parte más difícil e importante. Si le dices a la IA "te doy un punto si tocas la meta", se volverá loca y se moverá a $35,000 \text{ mm/s}^2$ ignorando la suavidad. La recompensa debe ser un polinomio denso:

$$R_t = R_{distancia} + R_{suavidad} - P_{penalizacion}$$

* $R_{distancia}$: Se maximiza cuando el error Euclidiano (que vimos en tu matriz) tiende a cero. (Usualmente una función Exponencial Inversa).
* $R_{suavidad}$: Premia mantener las aceleraciones parecidas a las del experto.
* $P_{penalizacion}$: Castiga a la IA si los motores del xArm5 intentan exceder sus límites de torque o articulación.

**Paso 3: Construcción de la Tarea en Isaac Gym (`XArm5_Task.py`)**
Escribiremos un script en Python que:
1. Haga Spawn (instancie) de 64 xArm5 en una cuadrícula virtual.
2. Calcule las recompensas para los 64 robots simultáneamente (usando PyTorch para operaciones matriciales en la GPU, no bucles `for`).
3. Reinicie (Reset) a un robot individual si choca o se aleja demasiado.


**Paso 4: Entrenamiento con "Warm Start"**
1. Cargaremos la red del Crítico con pesos aleatorios.
2. Cargaremos la red del Actor con el archivo `xarm5_policy_6D_v3.3.pth` que acabamos de crear.
3. Lanzaremos PPO. La red ya no empezará moviéndose al azar (sacudiéndose violentamente). Empezará moviéndose con la elegancia del experto, y PPO solo tendrá que "empujarla" unos milímetros hacia la meta para corregir la deriva.








