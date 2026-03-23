<<<<<<< HEAD
# obtener_indice
=======
# Obtener anexo de un archivo PDF a través de un índice
## Objetivo:
Desarrollar un algoritmo capaz de extraer secciones específicas (anexos) de un archivo PDF utilizando como "pivote" los hipervínculos integrados en su índice.

### Lógica
**Punto de Inicio**: Se identifica el destino exacto del hipervínculo en el índice.

**Punto Final**: Dado que el largo de cada apartado es variable, el sistema utiliza el inicio de la siguiente sección como el límite de la sección anterior.

### Advanced Text Cleaning / Limpieza Avanzada
**EN**: The algorithm implements advanced Regular Expressions (Regex) to strip headers from the "Periódico Oficial del Estado de Puebla", ensuring that only relevant fiscal data is processed.

**ES**: El algoritmo implementa Expresiones Regulares (Regex) avanzadas para limpiar los encabezados del Periódico Oficial del Estado de Puebla, garantizando que solo se procese la información fiscal relevante.

## Installation & Configuration / Instalación y Configuración
**EN**: Ensure you have Python 3.x installed and Oracle Database

**ES**: Asegúrate de tener instalado Python 3.x y Base de datos de Oracle

Para la conexión a la base, se usa un archivo .env.example
de ejemplo para visualizar la conexión a una base de datos de Oracle

``` env
DB_USER="usuario"
DB_PASSWORD="contraseña"
DB_NS="host"
```

## Clone and Install / Clonar e Instalar
**EN**: Clone the repository and install dependencies:

**ES**: Clona el repositorio e instala las dependencias:
```bash
git clone https://github.com/JaredFcoPO/python-sql-automation.git
cd python-sql-automation
pip install -r requirements.txt
```
The environment variables are loaded by python-dotenv, while the PDF content is parsed using PyMuPDF (fitz). Finally, the database updates are executed through oracledb.

### Environment Variables / Variables de Entorno
**EN**: This project uses a".env" file to manage sensitive database credentials securely.

**ES**: Este proyecto utiliza un archivo".env" para gestionar las credenciales sensibles de la base de datos de forma segura.

**EN**: Locate the .env.example file in the root directory.

**ES**: Localiza el archivo .env.example en el directorio raíz.

**EN**: Create a copy and rename it to .env:

**ES**: Crea una copia y cámbiale el nombre a .env:

**EN**: Open .env and fill in your local database connection details:

**ES**: Abre .env y completa los detalles de conexión de tu base de datos local:

### How to run / Cómo ejecutar
**EN**: Once configured, run the script to process the public data file and generate the SQL update scripts:

**ES**: Una vez configurado, ejecuta el script para procesar el archivo de datos públicos y generar los scripts de actualización de SQL:

## Data Source / Origen de los Datos
Este proyecto utiliza información pública del Presupuesto de Egresos de Puebla. Los archivos pueden consultarse en https://lgcg.puebla.gob.mx/marco-programatico

Estructura requerida: El archivo debe renombrarse como Etapa_Ley.pdf (ej. Aprobado_Ley.pdf o Iniciativa_Ley.pdf) y colocarse en la raíz del proyecto.

Asimismo, hay otros criterios fijos que depende de la estructura del PDF, entre ellos, saltos de página, hojas en blanco, texto fijo en el encabezado del PDF y errores en la ubicación del hipervínculo

Por otro lado, al ejecutar esta versión, se obtienen 3 productos:
* Documento csv: Con la estructura del índice del archivo PDF, su descripción y su paginado.

Bajo el supuesto que existe una base de datos donde se desea carga el índice, se usa una base de datos de Oracle como ejemplo para exponer
como sería el proceso de automatización de dos tipos de instrucciones SQL.
* SQL Updates: Scripts para actualizar la paginación en registros ya existentes en la base de datos.
* SQL Inserts: Scripts para dar de alta nuevas secciones identificadas en el índice.

Finalmente, es importante mencionar que todo el proyecto se encuentra límitado por la existencia de hipervínculos en el índice, en caso de no existir,
el aplicativo no podrá obtener el índice del archivo proporcionado y tampoco las instrucciones sql. Por ello, se desea actualizar esta versión para usar otras 
herramientas para extraer información.
>>>>>>> 2418a1c (Automatización de queries y obtención de anexo de un PDF)
