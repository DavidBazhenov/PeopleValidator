import os
import requests

def test_api(image_path, api_url, api_key):
    """
    Тестирование API определения людей на изображении.

    Args:
        image_path (str): Путь к изображению для тестирования
        api_url (str): URL API
        api_key (str): Ключ API
    """
    # Проверка существования файла
    if not os.path.exists(image_path):
        print(f"Ошибка: Файл {image_path} не существует.")
        return

    # Проверка формата API URL
    if not api_url.endswith('/'):
        api_url += '/'

    # Подготовка URL
    url = f"{api_url}api/detect-person"

    try:
        # Открытие изображения
        with open(image_path, 'rb') as image_file:
            # Подготовка файла для отправки
            files = {'file': (os.path.basename(image_path), image_file, 'image/jpeg')}

            # Подготовка заголовка с API ключом (используем правильное имя заголовка)
            headers = {'api-key': api_key}

            print(f"Отправка запроса на {url}...")
            print(f"Используемый API ключ: {api_key}")

            # Отправка запроса
            response = requests.post(url, files=files, headers=headers)
    except Exception as e:
        print(f"Ошибка при отправке запроса: {e}")
        return

    if response.status_code == 200:
        print("Запрос успешно выполнен.")
        # Обработка ответа
        data = response.json()
        print(f"Результат: {data}")
    else:
        print(f"Ошибка при выполнении запроса. Статус код: {response.status_code}")
        print(f"Ответ сервера: {response.text}")

    return response.status_code 