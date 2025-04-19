import os
import logging
from typing import Optional
import cv2
import numpy as np
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
from telegram_service import TelegramService
from image_processor import ImageProcessor

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Person Detection API")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация сервисов
telegram_service = TelegramService()
image_processor = ImageProcessor()

@app.get("/")
async def read_root():
    return {"message": "Сервис определения людей на изображениях"}

@app.post("/api/detect-person")
async def detect_person(
    file: UploadFile = File(...),
    api_key: Optional[str] = Header(None, alias="api-key")
):
    # Проверка API ключа
    logger.info(f"Полученные заголовки: {api_key}")
    expected_key = os.getenv("API_KEY")
    
    # Вывод всех заголовков для отладки
    if api_key is None:
        raise HTTPException(status_code=401, detail="API ключ отсутствует в заголовке. Используйте заголовок 'api-key'")
    
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail=f"Недействительный API ключ. Получено: '{api_key}', Ожидается: '{expected_key}'")
    
    try:
        # Чтение файла изображения
        contents = await file.read()
        
        # Обработка изображения
        image_bytes = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Не удалось прочитать изображение")
        
        logger.info(f"Изображение успешно загружено: {file.filename}, размер: {image.shape}")
        
        # Поиск людей на изображении и получение обработанного изображения с выделенными людьми
        has_person, processed_image = image_processor.detect_persons(image)
        
        logger.info(f"Результат обработки изображения: найден человек - {has_person}")
        
        # Отправка результата в Telegram сразу, а не асинхронно (для тестирования)
        try:
            await telegram_service.send_detection_result(
                has_person, 
                processed_image if has_person else image, 
                file.filename
            )
            logger.info("Задача отправки в Telegram выполнена напрямую")
        except Exception as telegram_error:
            logger.error(f"Ошибка при отправке в Telegram: {str(telegram_error)}")
            # Попробуем отправить только текстовое сообщение для отладки
            try:
                await telegram_service.send_text_message(
                    f"Ошибка при отправке изображения: {str(telegram_error)}\n"
                    f"Файл: {file.filename}\n"
                    f"Найден человек: {has_person}"
                )
            except Exception as text_error:
                logger.error(f"Невозможно отправить даже текстовое сообщение: {str(text_error)}")
        
        return {
            "filename": file.filename,
            "has_person": has_person,
            "message": "Человек обнаружен" if has_person else "Человек не обнаружен"
        }
        
    except Exception as e:
        logger.error(f"Ошибка при обработке изображения: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    ) 