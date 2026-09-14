#!/usr/bin/env python3
"""
Тестовый скрипт для системы бронирования билетов
"""

import os
import sys
from dotenv import load_dotenv

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Загружаем переменные из .env файла
load_dotenv()

def test_booking_system():
    """
    Тестирование системы бронирования
    """
    print("🚌 Тестирование системы бронирования билетов на маршрутки...")
    print("=" * 60)
    
    # Проверяем переменные окружения
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ Ошибка: Не установлена переменная GEMINI_API_KEY")
        print("Создайте .env файл с:")
        print("MODEL=google/gemini-2.0-flash-lite")
        print("GEMINI_API_KEY=your_api_key_here")
        return
    
    if not os.getenv("MODEL"):
        print("⚠️  Предупреждение: Переменная MODEL не установлена, используется значение по умолчанию")
    
    try:
        from src.crew_atl.main import run
        
        print("✅ Система готова к работе!")
        print("🤖 Запуск агентов бронирования...")
        
        # Запускаем систему
        result = run()
        
        print("\n🎉 Система успешно завершила работу!")
        print("📋 Результат:", result)
        
    except Exception as e:
        print(f"❌ Ошибка при запуске системы: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_booking_system()
