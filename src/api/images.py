import shutil
from fastapi import APIRouter, UploadFile

from src.tasks.tasks import resize_image  # Celery-задача для ресайза изображений

router = APIRouter(prefix="/images", tags=["Изображения отелей"])


@router.post("")
def upload_image(file: UploadFile):
    # Путь для сохранения оригинального изображения
    image_path = f"src/static/images/{file.filename}"

    # Сохраняем загруженный файл
    with open(image_path, "wb+") as new_file:
        shutil.copyfileobj(file.file, new_file)

    # Запускаем фоновую задачу на ресайз изображения
    resize_image.delay(image_path)

    return {"status": "OK", "filename": file.filename}
