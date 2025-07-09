from time import sleep

from src.tasks.celery_app import celery_instance


@celery_instance.task
def test_tasks():
    sleep(5)
    print("Я МОЛОДЕЦ")
