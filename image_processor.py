import cv2
import logging
import numpy as np

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        """
        Инициализация класса обработки изображений.
        Загружает предобученную модель HOG для определения людей.
        """
        logger.info("Инициализация HOG-детектора людей")
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        
        # Отключаем режим принудительного обнаружения
        self.force_detect = False
    
    def detect_persons(self, image):
        """
        Определяет людей на изображении и выделяет их прямоугольниками.
        
        Args:
            image (np.ndarray): Исходное изображение
            
        Returns:
            tuple: (bool, np.ndarray) - флаг наличия людей и обработанное изображение
        """
        # Сохраняем оригинальное изображение
        orig_image = image.copy()
        result_image = image.copy()
        
        # Преобразование изображения в оттенки серого для улучшения детекции
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        try:
            # Используем предложенные параметры для HOG детектора
            (humans, weights) = self.hog.detectMultiScale(
                gray, 
                winStride=(10, 10),
                padding=(32, 32), 
                scale=1.1
            )
            
            # Проверяем, обнаружены ли люди
            if len(humans) > 0:
                logger.info(f"Обнаружено {len(humans)} человек на изображении")
                
                # Отрисовка рамок вокруг обнаруженных людей
                for (x, y, w, h) in humans:
                    # Добавление отступов для рамки
                    pad_w, pad_h = int(0.15 * w), int(0.01 * h)
                    
                    # Отрисовка прямоугольника
                    cv2.rectangle(
                        result_image, 
                        (x + pad_w, y + pad_h), 
                        (x + w - pad_w, y + h - pad_h), 
                        (0, 255, 0), 
                        2
                    )
                    
                    # Добавление подписи
                    cv2.putText(
                        result_image,
                        "Person",
                        (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2
                    )
                
                return True, result_image
            else:
                logger.info("Люди на изображении не обнаружены")
                return False, orig_image
                
        except Exception as e:
            logger.error(f"Ошибка при определении людей: {str(e)}")
            return False, orig_image 