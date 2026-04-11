# Integración de xArm5 (5-DOF) en NVIDIA Isaac Sim con ROS 2 Humble para pHRI

Este repositorio documenta la metodología técnica completa para el despliegue de un 
entorno de simulación enfocado en la Interacción Humano-Robot Física (pHRI). 
El sistema integra un cobot UFACTORY xArm5 mediante ROS 2 (Humble) dentro del motor de
físicas NVIDIA Isaac Sim 4.5.0.

**Autor:**  G. Emir Sánchez-Valdés 
**Afiliación:** CINVESTAV - Departamento de Ingeniería Eléctrica, Sección de Mecatrónica.

---

## 📋 Requisitos Previos y Entorno de Hardware

Para garantizar la replicabilidad del entorno, se especifican las características de la estación de trabajo base:

* **Hardware:** Laptop Acer Nitro (GPU NVIDIA RTX Serie 40, e.g., RTX 4050).
* **Sistema Operativo:** Configuración Dual-Boot con Windows y **Ubuntu 22.04 LTS**.
* **BIOS/UEFI:** `Secure Boot` debe estar **desactivado** para permitir la correcta instalación de los controladores privativos de NVIDIA en Linux.

![Configuración del BIOS para Secure Boot](assets/placeholder_bios_secure_boot.png)
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
Descargar e instalar el **NVIDIA Omniverse Launcher** para Linux. Desde el Launcher, instalar **Isaac Sim 4.5.0**.

Posteriormente, se configura un entorno virtual de Python (denominado `isaac_env`) para aislar las dependencias del simulador.

![Omniverse Launcher mostrando Isaac Sim 4.5.0 instalado](assets/placeholder_omniverse_launcher.png)
*(Imagen de ejemplo: Captura del Omniverse Launcher con el botón "Launch" visible en Isaac Sim)*

---

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

![Panel de Extensiones en Isaac Sim con URDF Importer activo](assets/placeholder_extensions_panel.png)
*(Imagen de ejemplo: Captura del panel de extensiones mostrando el interruptor verde en "URDF IMPORTER EXTENSION")*

### 4.2 Importación del URDF
1. Ir a **File > Import**.
2. Seleccionar el archivo `~/xarm5_isaac.urdf`.
3. En las opciones de importación (panel lateral o inferior):
   * **Model:** Seleccionar `Create in Stage` (Evitar `Referenced Model` para permitir acceso a las articulaciones).
   * **Links:** Seleccionar `Static Base` (Ancla la base del robot al suelo).
4. Hacer clic en **Import**.
5. *Nota: Si el modelo no está a la vista, seleccionarlo en el panel de **Stage** y presionar la tecla **F** para centrar la cámara.*

![Robot xArm5 importado en el escenario de Isaac Sim](assets/placeholder_robot_stage.png)
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

![Nodos conectados en el Action Graph apuntando a link1](assets/placeholder_action_graph.png)
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

![Configuración del Action Graph para Control Bidireccional](assets/placeholder_action_graph_control.png)
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

