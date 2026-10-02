<div align="center">


# ELIOS-LAND

### UAV-Based Land Verification and Resurvey Platform

[![Live Frontend](https://img.shields.io/badge/Live%20Frontend-Vercel-black?style=for-the-badge&logo=vercel)](https://elios-land-survey.vercel.app/)
[![Backend API](https://img.shields.io/badge/Backend%20API-Render-46E3B7?style=for-the-badge&logo=render)](https://elios-land-survey.onrender.com/)
[![GitHub](https://img.shields.io/badge/Source-GitHub-181717?style=for-the-badge&logo=github)](https://github.com/prata-hp/ELIOS-LAND-SURVEY)
[![Demo](https://img.shields.io/badge/Demo-YouTube-FF0000?style=for-the-badge&logo=youtube)](https://youtu.be/dt2C5y3jEPk)

<br>

<img src="https://readme-typing-svg.demolab.com?font=Georgia&size=22&pause=1000&color=24517A&center=true&vCenter=true&width=800&lines=UAV+Survey+%7C+GIS+%7C+Photogrammetry+%7C+Boundary+Verification;Cadastral+vs+Observed+Geometry;Uncertainty-Aware+Land+Verification" />

</div>

---

<p align="center">
  <img src="https://skillicons.dev/icons?i=react,typescript,vite,python,fastapi,postgres,docker,git,github,vercel,supabase&perline=11" />
</p>
 
## Technology Stack

### Frontend
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![OpenLayers](https://img.shields.io/badge/OpenLayers-1F6B75?style=for-the-badge&logo=openlayers&logoColor=white)
![CSS](https://img.shields.io/badge/CSS-663399?style=for-the-badge&logo=css3&logoColor=white)

### Backend
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![PostGIS](https://img.shields.io/badge/PostGIS-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)

### GIS & Geospatial Processing
![QGIS](https://img.shields.io/badge/QGIS-589632?style=for-the-badge&logo=qgis&logoColor=white)
![GeoPandas](https://img.shields.io/badge/GeoPandas-139C5A?style=for-the-badge&logo=geopandas&logoColor=white)
![Shapely](https://img.shields.io/badge/Shapely-3B7A57?style=for-the-badge)
![Rasterio](https://img.shields.io/badge/Rasterio-2C5F2D?style=for-the-badge)

### Survey & Photogrammetry
![OpenDroneMap](https://img.shields.io/badge/OpenDroneMap-2D2D2D?style=for-the-badge)
![ArduPilot](https://img.shields.io/badge/ArduPilot-1E88E5?style=for-the-badge&logo=ardupilot&logoColor=white)
![QGroundControl](https://img.shields.io/badge/QGroundControl-212121?style=for-the-badge)
![RTK](https://img.shields.io/badge/RTK%2FPPK-GNSS-555555?style=for-the-badge)

### Infrastructure & Deployment
![Vercel](https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)
![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=black)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)

---

## What is ELIOS-LAND?

ELIOS-LAND is a web-based land resurvey and verification platform that connects existing cadastral records with UAV survey data.

It combines:

- UAV imagery
- GNSS / GCP survey data
- Photogrammetry
- GIS mapping
- Boundary extraction
- Cadastral comparison
- Uncertainty analysis
- Field verification
- Technical reporting

The system is designed for **technical survey verification and decision support**. It does not make legal ownership decisions.

---

## System Workflow

```text
Cadastral Record
       |
       v
Survey Project
       |
       v
UAV Images + GNSS/GCP Data
       |
       v
Photogrammetry / Orthomosaic
       |
       v
GIS Workspace
       |
       v
Boundary Delineation
       |
       v
Cadastral vs Observed Comparison
       |
       v
Uncertainty + Shift Analysis
       |
       v
Field Verification
       |
       v
Evidence + Technical Report
```

<img src="https://readme-typing-svg.demolab.com?font=Courier+Prime&size=18&pause=1200&color=2E6F40&center=true&vCenter=true&width=850&lines=Survey+%E2%86%92+Processing+%E2%86%92+GIS+%E2%86%92+Boundary+%E2%86%92+Comparison+%E2%86%92+Verification" />

---

## Core Features

| Module | Purpose |
|---|---|
| Survey Projects | Manage survey cases and project metadata |
| Data Upload | Drone images, GNSS, GCP, checkpoints and survey files |
| Photogrammetry | Generate orthomosaic and survey products |
| GIS Workspace | View and work with spatial layers |
| Boundary Delineation | AI-assisted and human-reviewed boundary extraction |
| Cadastral Comparison | Compare recorded and observed parcel geometry |
| Uncertainty Analysis | Consider survey and record uncertainty |
| Shift Analysis | Identify local vs systematic displacement |
| Field Verification | Route uncertain cases for ground verification |
| Evidence | Maintain survey and verification evidence |
| Reports | Generate technical survey reports |

---

## Technical Architecture

```text
                     ELIOS-LAND
                          |
          +---------------+---------------+
          |                               |
     Cadastral Data                  UAV Survey
          |                               |
          |                    +----------+----------+
          |                    |                     |
          |                UAV Images          GNSS / GCP
          |                    |                     |
          +--------------------+---------------------+
                               |
                               v
                     Photogrammetry
                        NodeODM
                               |
                    +----------+----------+
                    |          |          |
               Orthomosaic    DSM    Point Cloud
                    |
                    v
              ELIOS-LAND GIS
                    |
          +---------+---------+
          |                   |
     Cadastral Layer     Observed Boundary
          |                   |
          +---------+---------+
                    |
                    v
             Comparison Engine
                    |
          +---------+---------+
          |         |         |
         Area   Displacement  Shift
          |         |         |
          +---------+---------+
                    |
                    v
             Uncertainty
                    |
                    v
            Verification Case
                    |
                    v
             Evidence / Report
```

---

## Technology Stack

<div align="center">

<img src="https://skillicons.dev/icons?i=react,typescript,vite,python,fastapi,postgresql,docker,git,github,vercel&perline=10" />

</div>

### Frontend

- React
- TypeScript
- Vite
- OpenLayers
- CSS

### Backend

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- Psycopg
- GeoAlchemy2

### Geospatial

- PostgreSQL
- PostGIS
- GeoPandas
- Shapely
- PyProj
- Rasterio
- Fiona
- Pyogrio
- OpenLayers

### Survey / Processing

- NodeODM / OpenDroneMap
- UAV imagery
- GNSS / GCP data
- GeoTIFF
- DSM
- Point clouds

### Deployment

- Vercel
- Render
- Supabase PostgreSQL / PostGIS

---

## GIS Workspace

The GIS workspace provides a browser-based survey environment for:

- Orthomosaic visualization
- Cadastral overlays
- GCP and checkpoint layers
- Point, line and polygon editing
- Distance measurement
- Area measurement
- Perimeter measurement
- Feature inspection
- Boundary editing
- Raster metadata
- CRS-aware mapping

The system supports survey-scoped GIS layers rather than treating the orthomosaic as a standalone image.

---

## Verification Logic

ELIOS-LAND compares the recorded cadastral geometry with the observed survey geometry.

The analysis can include:

```text
Recorded Area
Observed Area
Area Difference
Boundary Displacement
Geometry Difference
Survey Uncertainty
Systematic Shift
```

A prototype uncertainty model uses:

```text
sigma_combined =
sqrt(
    sigma_record² +
    sigma_survey²
)
```

A displacement can then be evaluated relative to the combined uncertainty.

These calculations are intended for **technical screening and verification**, not legal tolerance determination.

---

## Boundary Delineation

The system supports an AI-assisted workflow:

```text
Orthomosaic
     |
     v
Boundary Detection
     |
     v
Polygon Generation
     |
     v
Human Review / Editing
     |
     v
Verified Observed Boundary
```

AI output is treated as an **observed physical boundary** and remains subject to human verification.

---

## Systematic Shift Detection

ELIOS-LAND can examine displacement across neighbouring parcels.

```text
Parcel A  ---> 
Parcel B  ---> 
Parcel C  ---> 
Parcel D  --->
```

When multiple parcels show a similar displacement direction and magnitude, the system can flag a possible systematic shift for georeferencing or reference-data review.

This helps distinguish a broader spatial-reference issue from an isolated parcel difference.

---

## Run Locally

### Requirements

Install:

- Python 3.10+
- Node.js 18+
- npm
- PostgreSQL
- PostGIS
- Git

NodeODM is required only when running the photogrammetry processing workflow locally.

---

### 1. Clone

```bash
git clone https://github.com/prata-hp/ELIOS-LAND-SURVEY.git
cd ELIOS-LAND-SURVEY
```

---

### 2. Backend

```bash
cd backend

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

Create the environment file:

```bash
cp .env.example .env
```

If `.env.example` is not present, create:

```bash
nano .env
```

Example:

```env
APP_NAME=ELIOS-LAND API
APP_ENV=development

DATABASE_URL=postgresql+psycopg://elios_land:elios_land_dev@localhost:5432/elios_land

STORAGE_ROOT=./storage
MAX_UPLOAD_SIZE_MB=2048
```

Start the backend:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Backend:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

---

### 3. Frontend

Open another terminal:

```bash
cd ELIOS-LAND-SURVEY/frontend

npm install
```

Create:

```bash
nano .env
```

Add:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Start:

```bash
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

### 4. Production Build

```bash
npm run build
```

The production files are generated in:

```text
frontend/dist/
```

---

## Optional: NodeODM

For local photogrammetry processing, run NodeODM separately.

The application communicates with the NodeODM service and stores processing results as survey artifacts.

Typical local architecture:

```text
ELIOS-LAND Frontend
        |
        v
FastAPI Backend
        |
        +--------> PostgreSQL / PostGIS
        |
        +--------> NodeODM
                       |
                       v
             Orthomosaic / DSM /
             Point Cloud / Models
```

---

## Live Demo

### Frontend

https://elios-land-survey.vercel.app/

### Backend API

https://elios-land-survey.onrender.com/

If the backend is temporarily unavailable because of free-tier hosting or service sleep, the frontend may not load live survey data until the API is available again.

### Source Code

https://github.com/prata-hp/ELIOS-LAND-SURVEY

### Demonstration Video

https://youtu.be/dt2C5y3jEPk

---

## Prototype Scope

The current prototype demonstrates the software workflow using survey/sample data.

The broader system architecture is designed to support:

```text
UAV Survey
     |
GNSS / GCP / Checkpoints
     |
Photogrammetry
     |
GIS
     |
AI-assisted Boundary Delineation
     |
Uncertainty Analysis
     |
Targeted Field Verification
     |
Evidence
     |
Technical Report
```

The architecture can later be integrated with approved land-record services and larger village/block-level survey operations.

---

## Project Status

```text
Frontend                  Working
FastAPI Backend           Working
PostgreSQL / PostGIS      Working
GIS Workspace             Working
GeoTIFF Visualization     Working
Survey Management         Working
Processing Integration    Working
Boundary Workflow         Prototype
Comparison Workflow       Prototype
Uncertainty Engine        Prototype
Field Verification        Architecture / Prototype
Public Demo               Deployed
```

---

<div align="center">

## ELIOS-LAND

UAV Survey + GIS + Photogrammetry + Uncertainty-Aware Verification

<br>

[Live Demo](https://elios-land-survey.vercel.app/) |
[Backend API](https://elios-land-survey.onrender.com/) |
[GitHub](https://github.com/prata-hp/ELIOS-LAND-SURVEY) |
[Demo Video](https://youtu.be/dt2C5y3jEPk)

</div>
