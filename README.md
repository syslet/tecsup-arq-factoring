# Sistema de Descuento de Letras y Facturas (Factoring)

Este proyecto consiste en el desarrollo del módulo **Core de Factoring** para una plataforma de descuento de facturas comerciales y letras de cambio, diseñado como un proyecto para el curso de Arquitectura de Software de Tecsup.

El sistema se enfoca en resolver los problemas de liquidez de las empresas B2B (Giradores), permitiéndoles registrar lotes de facturas, validarlas a través de la SUNAT, calcular la tasa de descuento (*pricing*) según el perfil de riesgo del deudor (Aceptante) y solicitar el desembolso correspondiente.

---

## 1. Arquitectura del Proyecto

El backend del sistema implementa **Onion Architecture** (Arquitectura de Cebolla) en Python, asegurando el aislamiento del dominio (las reglas del factoring) de las dependencias externas (bases de datos, APIs de terceros y frameworks):

*   **Capa de Dominio:** Entidades puras y reglas de negocio.
*   **Capa de Aplicación:** Casos de uso e interfaces de almacenamiento/servicios.
*   **Capa de Infraestructura:** Implementaciones de base de datos (PostgreSQL), clientes externos (SUNAT mock) y utilitarios.
*   **Capa de Presentación:** API REST implementada con FastAPI.

El frontend se desarrolla como una aplicación SPA utilizando **React + Vite** con estilos hechos en **Vanilla CSS** para asegurar una estética fintech premium.

---

## 2. Estructura del Monorepo

```
tecsup-arq-factoring/
├── backend/            # Aplicación Backend en Python (FastAPI)
├── frontend/           # Aplicación Frontend en React/Vite
├── db_data/            # Datos persistidos de base de datos local (Ignorado en Git)
├── .localbrain/        # Cerebro local de la IA (Ignorado en Git)
├── CLAUDE.md           # Guía de indexación e instrucciones para IA (Ignorado en Git)
├── README.md           # Este archivo (Guía para humanos)
└── docker-compose.yml  # Orquestador del entorno de desarrollo local
```

---

## 3. Requisitos Previos

Antes de ejecutar el proyecto, asegúrese de tener instalado:
*   [Docker](https://docs.docker.com/get-docker/)
*   [Docker Compose](https://docs.docker.com/compose/install/)

---

## 4. Cómo Iniciar el Entorno de Desarrollo

Para levantar todos los contenedores (Frontend, Backend y Base de datos PostgreSQL) en tu máquina local, ejecuta el siguiente comando en la raíz del repositorio:

```bash
docker compose up --build
```

Una vez que los servicios estén corriendo, podrás acceder a:
*   **Frontend (React/Vite):** [http://localhost:5173](http://localhost:5173)
*   **Backend API (FastAPI):** [http://localhost:8000](http://localhost:8000)
*   **Documentación de API (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
*   **Base de datos (PostgreSQL):** Puerto local `5432`

---

## 5. Instrucciones Adicionales

*   Para los desarrolladores de Inteligencia Artificial (IAs/Agentes), consulte el archivo [CLAUDE.md](file:///home/mdcast/Escritorio/PrivateProjects/tecsup-arq-factoring/CLAUDE.md) para comprender el protocolo de navegación e indexación del proyecto.
