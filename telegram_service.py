import os
import cv2
import logging
from io import BytesIO
import numpy as np
from dotenv import load_dotenv
from telegram import Bot
import asyncio

logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

class TelegramService:
    def __init__(self):
        """
        Инициализация сервиса для отправки сообщений в Telegram.
        Использует переменные окружения TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID.
        """
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not self.token:
            logger.error("TELEGRAM_BOT_TOKEN не задан в переменных окружения")
        else:
            logger.info(f"TELEGRAM_BOT_TOKEN найден: {self.token[:4]}...{self.token[-4:]}")
        
        if not self.chat_id:
            logger.error("TELEGRAM_CHAT_ID не задан в переменных окружения")
        else:
            logger.info(f"TELEGRAM_CHAT_ID найден: {self.chat_id}")
        
        try:
            self.bot = Bot(token=self.token) if self.token else None
            if self.bot:
                logger.info("Бот Telegram успешно инициализирован")
        except Exception as e:
            logger.error(f"Ошибка при инициализации бота Telegram: {str(e)}")
            self.bot = None
    
    async def send_detection_result(self, has_person, image, filename):
        """
        Отправляет результат обнаружения в Telegram.
        
        Args:
            has_person (bool): Найден ли человек на изображении
            image (np.ndarray): Обработанное изображение
            filename (str): Имя исходного файла
        """
        if not self.bot or not self.chat_id:
            logger.error("Не удается отправить сообщение в Telegram: токен или chat_id не настроены")
            return
        
        logger.info(f"Подготовка отправки результата в Telegram. Найден человек: {has_person}")
        
        try:
            # Проверка типа данных изображения
            if image is None:
                logger.error("Изображение пустое (None)")
                return
                
            logger.info(f"Размер изображения: {image.shape}")
            
            # Конвертация изображения в формат для отправки
            success, buffer = cv2.imencode('.jpg', image)
            if not success:
                logger.error("Ошибка кодирования изображения")
                return
                
            # Создание объекта BytesIO для отправки файла
            bio = BytesIO(buffer)
            bio.name = f"processed_{filename}" if filename else "processed_image.jpg"
            logger.info(f"Изображение подготовлено для отправки: {bio.name}")
            
            # Текст сообщения
            caption = f"✅ Человек обнаружен на изображении" if has_person else "❌ Человек не обнаружен на изображении"
            
            # Отправка сообщения с фото
            logger.info(f"Отправка сообщения в чат {self.chat_id}")
            await self.bot.send_photo(
                chat_id=self.chat_id, 
                photo=bio, 
                caption=caption
            )
            
            logger.info(f"Сообщение успешно отправлено в Telegram: {caption}")
            
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения в Telegram: {str(e)}")
            # Отправим текстовое сообщение об ошибке для отладки
            try:
                await self.send_text_message(f"Произошла ошибка при отправке изображения: {str(e)}")
            except Exception as inner_e:
                logger.error(f"Не удалось отправить сообщение об ошибке: {str(inner_e)}")
    
    async def send_text_message(self, message):
        """
        Отправляет текстовое сообщение в Telegram.
        
        Args:
            message (str): Текст сообщения
        """
        if not self.bot or not self.chat_id:
            logger.error("Не удается отправить сообщение в Telegram: токен или chat_id не настроены")
            return
        
        try:
            logger.info(f"Отправка текстового сообщения в чат {self.chat_id}")
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message
            )
            logger.info(f"Текстовое сообщение успешно отправлено в Telegram")
        except Exception as e:
            logger.error(f"Ошибка при отправке текстового сообщения в Telegram: {str(e)}") 