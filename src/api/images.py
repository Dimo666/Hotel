from fastapi import APIRouter, UploadFile, BackgroundTasks

from src.services.images import ImagesService  # Сервис для работы с изображениями

router = APIRouter(prefix="/images", tags=["Изображения отелей"])


@router.post("")
def upload_image(file: UploadFile, background_tasks: BackgroundTasks):
    """
    Загрузка изображения отеля.

    - Сохраняет файл в файловую систему
    - Запускает фоновую задачу на обработку (например, ресайз)

    :param file: загружаемый файл изображения (multipart/form-data)
    :param background_tasks: менеджер фоновых задач FastAPI
    :return: статус и имя файла
    """
    ImagesService().upload_image(file, background_tasks)

    return {"status": "OK", "filename": file.filename}
