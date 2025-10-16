# Descripción

**LMS API** es un microservicio desarrollado con **Django REST Framework (DRF)** que modela una plataforma de cursos en línea.  
Expone endpoints CRUD para:

- **users** → solo lectura y acceso de administrador  
- **profiles** → perfil de usuario 
- **courses** → título, descripción, nivel, idioma, precio y estado de publicación  
- **lessons** → lecciones por curso  
- **enrollments** → inscripciones de usuarios a cursos  
- **comments** → comentarios y calificaciones  

Incluye documentación automática con Swagger y Redoc, y se ejecuta completamente dentro de Docker

---

## Screenshots Swagger

<img width="2370" height="1888" alt="image" src="https://github.com/user-attachments/assets/ce91451e-8989-4c8e-ac8c-793d36f7626d" />




<img width="2400" height="1926" alt="image" src="https://github.com/user-attachments/assets/2a40fec6-1296-4ff3-b980-21a65ad6cf03" />





## ⚙️ Instrucciones para levantar el servicio


```bash
# 1 Construir e iniciar contenedores
docker compose build
docker compose up -d

# 2  Ejecutar migraciones y crear superusuario
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
