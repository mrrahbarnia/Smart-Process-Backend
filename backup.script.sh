#!/bin/bash


db_user=postgres
db_name=postgres
database_container_name=prod-db

container_backup_file=/psql.backup.sql
local_backup_file=/root/Smart-Process-Backend/backup/psql.backup.sql

docker-compose -f /root/Smart-Process-Backend/docker-compose.prod.yml exec $database_container_name sh -c "pg_dump -U $db_user -d $db_name > psql.backup.sql"
docker-compose -f /root/Smart-Process-Backend/docker-compose.prod.yml cp $database_container_name:$container_backup_file $local_backup_file

docker-compose -f /root/Smart-Process-Backend/docker-compose.prod.yml down
docker-compose -f /root/Smart-Process-Backend/docker-compose.prod.yml up