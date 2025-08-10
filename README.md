git config --local user.name "Dmitry Kitaev"
git config --local user.email "info.fleet.gdr@gmail.com"


# Создать Docker сети
docker network create myNetwork

# Создание DB
docker run --name booking_db \
    -p 6432:5432 \
    -e POSTGRES_USER=abcde \
    -e POSTGRES_PASSWORD=abcde \
    -e POSTGRES_DB=booking \
    --network=myNetwork \
    --volume pg-booking-data:/var/lib/postgresql/data \
    -d postgres:16
    
# Создание Redis
docker run --name booking_cache \
    -p 7379:6379 \
    --network=myNetwork \
    -d redis:7.4

# пересобрать docker образ для booking_image
docker build -t booking_image .

# Создание приложения Booking
docker run --name booking_back \
    -p 7777:8000 \
    --network=myNetwork \
    booking_image

# Создание Celery worker
docker run --name booking_celery_worker \
    --network=myNetwork \
    booking_image \
    celery --app=src.tasks.celery_app:celery_instance worker -l INFO

# Создание Celery beat
docker run --name booking_celery_beat \
    --network=myNetwork \
    booking_image \
    celery --app=src.tasks.celery_app:celery_instance worker -l INFO -B

