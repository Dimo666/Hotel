# Создание папки migrations + alembic.ini
# Обезательно создавать в корневой дериктрории
alembic init src/migrations 

# Создать миграции + название миграции
alembic revision --autogenerate -m "initial migration"

# Послать миграции 
alembic upgrade head