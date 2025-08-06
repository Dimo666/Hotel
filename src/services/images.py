import shutil

from fastapi import UploadFile, BackgroundTasks

from src.services.base import BaseService
from src.tasks.tasks import resize_image


class ImagesService(BaseService):
    """
    Сервис для загрузки и обработки изображений.
    """

    def upload_image(self, file: UploadFile, background_tasks: BackgroundTasks):
        """
        Загружает изображение и запускает фоновую задачу по его ресайзу.

        :param file: файл изображения, загружаемый пользователем
        :param background_tasks: менеджер фоновых задач FastAPI
        :return: None
        """
        # Путь для сохранения оригинального изображения
        image_path = f"src/static/images/{file.filename}"

        # Сохраняем загруженный файл в указанный путь
        with open(image_path, "wb+") as new_file:
            shutil.copyfileobj(file.file, new_file)

        # Добавляем фоновую задачу для ресайза изображения
        background_tasks.add_task(resize_image, image_path)
