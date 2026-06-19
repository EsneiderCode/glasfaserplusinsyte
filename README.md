# Glasfaser+ Insyte - WorkOrders Agent

Sistema de gestion de ordenes de trabajo que sincroniza datos desde el portal Insyte de Glasfaser+ y los presenta en una interfaz web local con filtros, detalle de ordenes, fotos y tablero de clasificacion.

## Overview

### Que hace esta app?

1. **Sincroniza** ordenes de trabajo desde la API de Insyte (`api-imasm.insytedeutschland.de`)
2. **Almacena** los datos localmente en SQLite para consulta rapida
3. **Presenta** las ordenes en una tabla interactiva con filtros, badges de estado y columnas dinamicas
4. **Detalle** de cada orden con fotos organizadas por fase de instalacion (26 tipos)
5. **Tablero (Board)** tipo kanban para clasificar ordenes en 5 categorias

### Stack

| Capa | Tecnologia |
|------|-----------|
| Backend | Python 3.9+ / FastAPI / SQLAlchemy / SQLite |
| Frontend | Vue 3 / Vite / PrimeVue / Pinia |
| API Externa | Insyte Portal (JWT auth) |

### Estructura del proyecto

```
workorders-agent/
├── backend/
│   ├── main.py              # FastAPI app + startup migrations
│   ├── config.py            # Settings (lee de .env)
│   ├── database.py          # SQLAlchemy engine + session
│   ├── models.py            # ORM models (Order, OrderBoletin, Master)
│   ├── schemas.py           # Pydantic schemas
│   ├── routers/
│   │   ├── orders.py        # CRUD ordenes, filtros, clasificacion, board
│   │   ├── sync.py          # Sincronizacion con Insyte
│   │   └── files.py         # Descarga de archivos/fotos
│   └── services/
│       ├── auth.py          # JWT auth contra Insyte
│       ├── portal_client.py # HTTP client para Insyte API
│       ├── sync.py          # Logica de sync + label resolution
│       └── file_manager.py  # Gestion de archivos descargados
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── WorkOrdersList.vue  # Tabla principal con filtros
│   │   │   ├── WorkOrderDetail.vue # Detalle + fotos por fase
│   │   │   └── BoardView.vue       # Tablero kanban
│   │   ├── stores/
│   │   │   └── orders.js           # Pinia store
│   │   └── assets/style.css        # Estilos globales
│   └── package.json
├── data/                    # SQLite DB + archivos (ignorado en git)
├── start.sh                 # Script para levantar todo
├── requirements.txt         # Dependencias Python
└── .env                     # Credenciales (no se sube a git)
```

---

## Setup rapido

### Requisitos previos

- **Python 3.9+** (`python3 --version`)
- **Node.js 18+** (`node --version`)
- **npm** (`npm --version`)

### 1. Clonar el repo

```bash
git clone https://github.com/EsneiderCode/glasfaserplusinsyte.git
cd glasfaserplusinsyte
```

### 2. Configurar credenciales

```bash
cp .env.example .env
```

Editar `.env` con las credenciales del portal Insyte:

```
PORTAL_API_URL=https://api-imasm.insytedeutschland.de
USERNAME=UMTELKOMD
PASSWORD=tu_password_aqui
```

### 3. Instalar dependencias

**Backend (Python):**

```bash
pip3 install -r requirements.txt
```

**Frontend (Node):**

```bash
cd frontend
npm install
cd ..
```

### 4. Ejecutar

```bash
chmod +x start.sh
./start.sh
```

Esto levanta:
- **Backend API** en `http://localhost:8000`
- **Frontend** en `http://localhost:5173`

### 5. Primera sincronizacion

Una vez abierta la app en el navegador, haz click en el boton **"Sincronizar"** para descargar las ordenes desde Insyte. La primera sync toma unos minutos.

---

## Endpoints principales

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/api/orders` | Lista ordenes con filtros y paginacion |
| GET | `/api/orders/{id}` | Detalle de una orden |
| PATCH | `/api/orders/{id}/classification` | Clasificar orden |
| GET | `/api/board` | Ordenes agrupadas por clasificacion |
| POST | `/api/sync` | Sincronizar ordenes desde Insyte |
| POST | `/api/sync/fix-labels` | Re-aplicar labels desde masters |
| POST | `/api/sync/fix-boletin` | Re-enriquecer desde boletines |

---

## Notas

- La DB SQLite se crea automaticamente en `data/workorders.sqlite` al primer inicio
- Las fotos y archivos se descargan a `data/files/`
- La carpeta `data/` esta en `.gitignore` - cada instalacion genera su propia DB al sincronizar
