#!/usr/bin/env python3
"""
Скрипт для тестирования системы бронирования с агентом тестирования.
Агент тестирования имитирует поведение пользователя согласно примерам диалогов.
"""

import os
from dotenv import load_dotenv
from src.crew_atl.crew import CrewAtl

def main():
    # Загружаем переменные окружения
    load_dotenv()
    
    # Проверяем наличие API ключа
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ Ошибка: Не найден GEMINI_API_KEY в .env файле")
        print("Создайте файл .env в корне проекта с содержимым:")
        print("GEMINI_API_KEY=your_api_key_here")
        print("MODEL=gemini-1.5-pro")
        return
    
    print("🤖 Запуск системы бронирования с агентом тестирования...")
    print("=" * 60)
    
    try:
        # Создаем crew
        crew = CrewAtl()
        
        # Запускаем тестирование
        print("🧪 Агент тестирования начинает имитацию пользователя...")
        print("🤖 Агент бронирования готов к диалогу...")
        result = crew.full_testing_crew().kickoff()
        
        print("\n" + "=" * 60)
        print("🎉 Тестирование завершено!")
        print(f"📋 Результат: {result}")
        
    except Exception as e:
        print(f"❌ Ошибка при выполнении: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
