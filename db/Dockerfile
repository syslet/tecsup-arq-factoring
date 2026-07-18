FROM postgres:15-alpine

# En caso de necesitar scripts de inicialización de esquemas o datos iniciales:
# COPY init.sql /docker-entrypoint-initdb.d/

ENV POSTGRES_DB=factoring_core_db
ENV POSTGRES_USER=factoring_user
ENV POSTGRES_PASSWORD=factoring_password

EXPOSE 5432
