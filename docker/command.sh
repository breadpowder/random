docker run --rm -p 5432:5432 --name pg_test docker_postgresql
source ~/.bash_profile
PGPASSWORD=docker psql -h localhost -U docker docker -a -f scripts/table_ddl.sql
