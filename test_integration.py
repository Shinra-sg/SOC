#!/usr/bin/env python3
"""
Скрипт для проверки интеграции агента тестирования без использования LLM.
"""

import os
from dotenv import load_dotenv
from src.crew_atl.crew import CrewAtl

def main():
    # Загружаем переменные окружения
    load_dotenv()
    
    print("🤖 Проверка интеграции агента тестирования...")
    print("=" * 60)
    
    try:
        # Создаем crew
        crew = CrewAtl()
        
        # Проверяем, что агент тестирования создается
        testing_agent = crew.testing_agent()
        print(f"✅ Агент тестирования создан: {testing_agent.role}")
        
        # Проверяем, что crew для тестирования создается
        testing_crew = crew.testing_crew()
        print(f"✅ Crew для тестирования создан с {len(testing_crew.agents)} агентами")
        
        # Проверяем конфигурацию агента
        print(f"✅ Роль агента: {testing_agent.role}")
        print(f"✅ Цель агента: {testing_agent.goal[:50]}...")
        
        print("\n" + "=" * 60)
        print("🎉 Интеграция агента тестирования успешна!")
        print("📋 Агент готов к тестированию системы бронирования")
        
    except Exception as e:
        print(f"❌ Ошибка при интеграции: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
