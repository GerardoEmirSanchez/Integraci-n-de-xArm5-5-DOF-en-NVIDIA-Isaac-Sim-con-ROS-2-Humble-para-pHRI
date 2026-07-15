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

Durante las pruebas de robustez y transferencia, se identificaron vulnerabilidades críticas en la formulación discreta del control clásico y en la dimensionalidad de la política neuronal, requiriendo reestructuraciones fundamentales para viabilizar el despliegue.

### 17.1 Mitigación de la Bomba de Energía Numérica (Euler Semi-Implícito)
Se sustituyó la integración de Euler Explícito por un esquema de Euler Semi-Implícito para el control de admitancia[cite: 6]. La formulación discreta anterior inducía un polo fuera del círculo unitario bajo variaciones bruscas de rigidez, actuando como una bomba de energía numérica e inestabilizando el sistema[cite: 6].
* La nueva velocidad de comando se evalúa de forma implícita: $\dot{x}_c(k+1) = \frac{\dot{x}_c(k) + \frac{T}{M_d}[\hat{F}_{ext}(k) - K_d(k)(x_c(k) - x_{ref})]}{1 + \frac{T \cdot B_d(k)}{M_d}}$[cite: 6].
* El polo característico se redefine como $z = [1 + \frac{T \cdot B_d(k)}{M_d}]^{-1}$[cite: 6].
* Dado que los parámetros físicos son positivos, se garantiza que $z \in (0,1)$, asegurando la disipación asintótica de la energía elástica y proporcionando un amortiguamiento numérico que preserva la estabilidad física[cite: 6].

### 17.2 Arquitectura "Time-Aware" 6D y Preprocesamiento
Para solucionar el colapso del xArm5 virtual causado por el *Reality Gap* y el error compuesto (*Covariate Shift*) de los motores físicos (PhysX 5), se reestructuró el vector de observación y acción[cite: 7, 8].
* **Ceguera a torques:** La red neuronal ahora es completamente ciega a los torques articulares $(\tau_1 \dots \tau_5)$ para evadir la dependencia de las fricciones no lineales y no modeladas[cite: 7, 8].
* **Vector de Estado (15D):** Se inyectó explícitamente el diferencial temporal $\Delta t$ para inducir una integración tácita de la velocidad: $s_t = [\Delta t, F_x, F_y, F_z, T_x, T_y, T_z, Roll, Pitch, Yaw, q_1, q_2, q_3, q_4, q_5]$[cite: 7, 8].
* **Vector de Acción (8D):** $a_t = [\Delta_X, \Delta_Y, \Delta_Z, \Delta_{Roll}, \Delta_{Pitch}, \Delta_{Yaw}, Vel_{filt}, Acc_{filt}]$[cite: 8].
* **Acondicionamiento Numérico:** Se implementó una normalización Z-Score estricta ($z = (x - \mu) / (\sigma + 1e-8)$) y aritmética modular diferencial para los ángulos de Euler ($\Delta\theta_{\text{norm}} = ((\Delta\theta + 180^\circ) \bmod 360^\circ) - 180^\circ$)[cite: 7, 8].
* Esto previene discontinuidades espaciales y la explosión de gradientes ante aceleraciones de alta magnitud[cite: 7, 8].
* **Topología Parsimoniosa:** La red se redujo a la arquitectura $[15 \to 128 \to 128 \to 8]$ empleando Dropout ($p=0.15$) y función de pérdida Huber (Smooth L1) para suprimir valores atípicos del sensor OptoForce y prevenir el sobreajuste[cite: 7, 8].

### 17.3 Cierre de Bucle Sim-to-Sim (Cinemática Inversa Subactuada)
Dado que la tarea exige controlar 6 grados de libertad (6D) en el espacio operativo utilizando un manipulador de 5 grados de libertad (xArm5), el cálculo del error cartesiano requiere adaptar el mapeo cinemático[cite: 8].
* Se implementó el Jacobiano Espacial asimétrico ($6 \times 5$) empleando la pseudo-inversa de Moore-Penrose: $\Delta q = J^\dagger(q) \Delta X_{6D}$[cite: 7, 8].
* Esta formulación restringe al brazo subactuado para priorizar estrictamente la orientación RPY solicitada por la IA[cite: 8].

### 17.4 Transición a Políticas Residuales (Enfoque TRANSIC)
Para la futura fase de despliegue físico y mitigación de la brecha *Sim-to-Real*, el clonado de comportamiento (*Behavior Cloning*) fungirá exclusivamente como un *Warm-Start* inmutable ($\pi_B$) para Proximal Policy Optimization (PPO)[cite: 3, 7, 8].
* Las variabilidades biomecánicas, la fatiga del operador y las fuerzas de fricción reales serán absorbidas por una Política Residual adaptable ($\pi_R$)[cite: 3, 8].
* Esta política se entrenará a partir de las correcciones humanas en línea, mitigando el olvido catastrófico y aislando el conocimiento cinemático base[cite: 3, 8].

































































