# Servicio de videos con gRPC

Este proyecto demuestra tres modalidades de comunicación mediante **gRPC y Protocol Buffers**:

1. **Subida de videos (`UploadVideo`)**: *client streaming*. El cliente envía metadatos y posteriormente el archivo en bloques de 64 KiB.
2. **Listado de videos (`ListVideos`)**: llamada unaria. El cliente consulta los archivos de video disponibles en el servidor.
3. **Transmisión de video (`StreamVideo`)**: *server streaming*. El servidor lee un video, convierte sus fotogramas a JPEG y los envía progresivamente al cliente, que los muestra mediante OpenCV.

> **Importante:** este ejemplo transmite fotogramas JPEG mediante gRPC; no implementa un protocolo de reproducción multimedia como HLS o DASH. La comunicación usa `grpc.insecure_channel`, por lo que está pensada para prácticas en un entorno de confianza, no para producción.

## 1. Estructura del repositorio

```text
video-grpc/
├── video_service.proto
├── server.py
├── client_upload.py
├── client_stream.py
├── videos/
│   └── .gitkeep
├── requirements.txt         # Se genera en el paso 3
└── README.md
```

La carpeta **`videos/`** contiene los archivos almacenados en el servidor. El método `UploadVideo` guarda ahí los videos recibidos y `StreamVideo` lee los archivos de esa misma carpeta para transmitirlos. También pueden colocarse manualmente videos compatibles (`.mp4`, `.avi`, `.mkv`, `.mov`) dentro de ella.

El servidor crea `videos/` automáticamente al iniciarse si no existe. Aun así, conviene incluir la carpeta vacía en Git mediante `videos/.gitkeep`.

**Todos los comandos siguientes se ejecutan desde la raíz del proyecto.** Esto es importante porque `server.py` utiliza la ruta relativa `videos`.

## 2. Crear y activar el entorno virtual

Crear el entorno:

**Windows (CMD):**

```cmd
python -m venv env
```

**Linux:**

```bash
python3 -m venv env
```

Activarlo:

**Windows (CMD):**

```cmd
env\Scripts\activate
```

**Linux:**

```bash
source env/bin/activate
```

Al activarlo debe aparecer `(env)` al inicio de la terminal. Para desactivarlo, en cualquiera de los dos sistemas:

```bash
deactivate
```

## 3. Instalar dependencias

Con el entorno virtual activado:

```bash
python -m pip install grpcio grpcio-tools protobuf opencv-python numpy
```

| Dependencia | Función |
| --- | --- |
| `grpcio` | Ejecutar clientes y servidores gRPC |
| `grpcio-tools` | Compilar el contrato `.proto` y generar las clases Python |
| `protobuf` | Serializar y deserializar mensajes |
| `opencv-python` | Leer, codificar y mostrar fotogramas de video |
| `numpy` | Convertir los bytes recibidos en arreglos para OpenCV |

Guardar las versiones instaladas:

```bash
python -m pip freeze > requirements.txt
```

Si el repositorio ya incluye `requirements.txt`, basta con instalar sus dependencias mediante:

```bash
python -m pip install -r requirements.txt
```

## 4. Compilar el contrato Protocol Buffers

Desde la raíz del proyecto:

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. video_service.proto
```

Se generan los archivos:

```text
video_service_pb2.py
video_service_pb2_grpc.py
```

- `video_service_pb2.py` contiene las clases de mensajes Protobuf.
- `video_service_pb2_grpc.py` contiene las clases del servicio y el stub del cliente.

**No editar manualmente los archivos generados.** Es necesario volver a ejecutar el comando cuando cambie `video_service.proto`.

> En este proyecto, los módulos generados deben quedar en la **raíz**, junto a `server.py` y los clientes, porque el código actual los importa directamente como `video_service_pb2` y `video_service_pb2_grpc`. No se requiere configurar `PYTHONPATH` ni crear una carpeta `generated/`.

## 5. Preparar la carpeta de videos

Si la carpeta todavía no existe, crearla desde la raíz:

**Windows (CMD):**

```cmd
mkdir videos
```

**Linux:**

```bash
mkdir -p videos
```

Se pueden copiar archivos `.mp4`, `.avi`, `.mkv` o `.mov` a `videos/` para probar el listado y la transmisión sin subirlos desde el cliente. El servidor también almacenará en esta carpeta los videos que reciba mediante `UploadVideo`.

Para incluir la carpeta vacía en Git sin subir videos reales, crear un archivo `.gitkeep`:

**Windows (CMD):**

```cmd
type nul > videos\.gitkeep
```

**Linux:**

```bash
touch videos/.gitkeep
```

Se recomienda agregar al archivo `.gitignore`:

```gitignore
env/
__pycache__/
*.pyc
videos/*
!videos/.gitkeep
```

Así los videos subidos durante las pruebas no se publicarán accidentalmente en el repositorio.

## 6. Ejecutar el servidor

Con el entorno virtual activado, desde la raíz:

```bash
python server.py
```

Salida esperada:

```text
[SERVER] VideoService corriendo en puerto 50051...
```

El servidor escucha en el puerto **50051**. Mantener esta terminal abierta mientras se ejecutan los clientes.

## 7. Subir un video desde el cliente

Abrir una **segunda terminal** en la raíz del proyecto y activar el entorno virtual (paso 2).

Antes de ejecutar, abrir `client_upload.py` y modificar estas líneas de la función `main()`:

```python
local_video_path = "C:/ruta/al/video/ejemplo.mp4"
video_title = "Video de prueba"
```

Sustituir la ruta por la ubicación real de un video en la computadora del cliente. En Linux, por ejemplo, podría ser `/home/usuario/Videos/ejemplo.mp4`.

**Nota:** el código original contiene una ruta absoluta a un archivo específico de otra computadora; es obligatorio cambiarla. `client_upload.py` lee un archivo local y lo envía al servidor: **no es necesario colocar ese archivo previamente en `videos/`**.

Ejecutar:

```bash
python client_upload.py
```

El cliente envía primero los metadatos y luego los bytes del archivo en bloques de **64 KiB**. El servidor lo guarda en `videos/` con su nombre original. Al finalizar, el cliente muestra si la subida fue exitosa y el nombre almacenado.

## 8. Reproducir un video por streaming

Abrir una **tercera terminal** en la raíz y activar el entorno virtual.

Verificar que `videos/` contenga al menos un video válido.

**Antes de ejecutar, revisar `client_stream.py`:** el código original contiene:

```python
selected = video_list.videos[1]
```

Este índice selecciona el **segundo video**. Si solo existe uno, producirá un error `IndexError`. Para la primera prueba, cambiarlo por:

```python
selected = video_list.videos[0]
```

Después ejecutar:

```bash
python client_stream.py
```

El cliente solicita el listado de videos, selecciona uno, pide su transmisión y muestra los fotogramas en una ventana de OpenCV.

Para cerrar la reproducción, presionar **`q`** mientras la ventana de video está activa. Se requiere un entorno gráfico capaz de mostrar ventanas de OpenCV.

## 9. Detener la ejecución

Para detener el servidor, volver a su terminal y presionar **Ctrl + C**. Para salir del entorno virtual:

```bash
deactivate
```

## 10. Aspectos para analizar

Durante la práctica, identificar:

1. ¿Qué operaciones del archivo `.proto` son unarias y cuáles utilizan streaming?
2. ¿Qué diferencia existe entre `stream UploadChunk` como entrada y `stream VideoFrame` como salida?
3. ¿Por qué el cliente de subida envía primero `VideoMetadata` y después los bloques de datos?
4. ¿Cómo se utiliza `VIDEOS_DIR` en `server.py` para almacenar, listar y recuperar los videos?
5. ¿Qué papel desempeñan `cv2.VideoCapture`, `cv2.imencode` y `cv2.imdecode`?
6. ¿Qué ocurriría si un video fuera demasiado grande o la red tuviera una latencia elevada?
7. ¿Qué limitaciones presenta esta implementación frente a un sistema de streaming de producción?

## 11. Observaciones técnicas

- Los clientes se conectan a `localhost:50051`. Para ejecutarlos en otro equipo, cambiar `localhost` por la IP o nombre del servidor y permitir la conexión al puerto 50051.
- El servidor transmite fotogramas con una pausa calculada a partir de los FPS del video; el cliente no incluye un búfer avanzado ni sincronización de audio.
- El campo `title` se envía al subir un video, pero el servidor actual no conserva ese título en un catálogo: `ListVideos` utiliza el nombre del archivo también como título.
- La subida utiliza el nombre original del archivo. Si se sube otro archivo con el mismo nombre, el servidor actual lo sobrescribe.
- Este código es una demostración académica: no incorpora autenticación, TLS, límites de tamaño ni controles completos de seguridad para archivos recibidos.
