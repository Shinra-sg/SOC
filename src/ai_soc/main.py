#!/usr/bin/env python
import sys
import warnings
import os
from dotenv import load_dotenv
from datetime import datetime
import time
import random

try:
    from .crew import AISocCrew
except ImportError:
    from crew import AISocCrew
from crewai import Crew, Task, Process
from datetime import datetime
import glob
import os

load_dotenv()
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    user_message = os.getenv('CREW_TEST_MESSAGE') or 'Здравствуйте, хочу заказать билет на маршрутку'
    current_date = os.getenv('CREW_TEST_DATE') or datetime.now().strftime('%Y-%m-%d')
    inputs = {
        'user_message': user_message,
        'current_date': current_date,
    }
    
    try:
        attempts = 0
        last_err = None
        result = None
        fallback_model = "gemini-2.0-flash-lite"
        while attempts < 7:
            try:
                result = AISocCrew().crew().kickoff(inputs=inputs)
                break
            except Exception as e:
                msg = str(e)
                last_err = e
                if (
                    ("User location is not supported" in msg)
                    or ("RESOURCE_EXHAUSTED" in msg)
                    or ("RateLimitError" in msg)
                    or ("list index out of range" in msg)  # пустой/битый ответ от LLM
                    or ("503" in msg)
                    or ("UNAVAILABLE" in msg)
                    or ("overloaded" in msg.lower())
                ):
                    base = 4 if ("503" in msg or "UNAVAILABLE" in msg or "overloaded" in msg.lower()) else 2
                    wait_s = base * (2 ** attempts)
                    jitter = random.uniform(0, 3)
                    wait_total = min(60, wait_s + jitter)
                    print(f"⏳ Временная ошибка LLM ('{msg[:120]}...'), повтор через {wait_total:.1f}s")
                    time.sleep(wait_total)
                    if attempts >= 2:
                        if os.getenv('MODEL') != fallback_model:
                            os.environ['MODEL'] = fallback_model
                            print(f"🔁 Переключаюсь на резервную модель: {fallback_model}")
                    attempts += 1
                    continue
                raise
        if result is None:
            try:
                base_dir = os.path.dirname(__file__)
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                internal_dir = os.path.join(base_dir, 'logs', 'dialogues')
                os.makedirs(internal_dir, exist_ok=True)
                project_dir = os.path.normpath(os.path.join(base_dir, '..', '..', 'logs', 'dialogues'))
                os.makedirs(project_dir, exist_ok=True)
                for target_dir in (internal_dir, project_dir):
                    fail_path = os.path.join(target_dir, f'dialogue_{ts}_failed.md')
                    try:
                        with open(fail_path, 'w', encoding='utf-8') as f:
                            f.write("# Диалог (FAILED)\n\n")
                            f.write(f"Начальное сообщение пользователя: {inputs.get('user_message')}\n\n")
                            f.write(f"Текущая дата: {inputs.get('current_date')}\n\n")
                            f.write("Статус: FAILED\n\n")
                            f.write("Ошибка:\n\n")
                            f.write(str(last_err or 'Неизвестная ошибка'))
                    except Exception:
                        pass
            except Exception:
                pass
            raise last_err if last_err else Exception("Неизвестная ошибка запуска")
        print("Результат бронирования:")
        print(result)
        try:
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_dir = os.path.dirname(__file__)
            internal_dir = os.path.join(base_dir, 'logs', 'dialogues')
            project_dir = os.path.normpath(os.path.join(base_dir, '..', '..', 'logs', 'dialogues'))
            for d in (internal_dir, project_dir):
                os.makedirs(d, exist_ok=True)
                diag_path = os.path.join(d, f'dialogue_{ts}_summary.md')
                with open(diag_path, 'w', encoding='utf-8') as f:
                    f.write("# Диалог (SUMMARY)\n\n")
                    f.write(f"Начальное сообщение пользователя: {inputs.get('user_message')}\n\n")
                    f.write(f"Текущая дата: {inputs.get('current_date')}\n\n")
                    ok = bool(result and str(result).strip())
                    f.write(f"Статус: {'OK' if ok else 'EMPTY_RESULT'}\n\n")
                    f.write("Вывод агента:\n\n")
                    f.write(str(result))
        except Exception:
            pass
        base_dir = os.path.dirname(__file__)
        internal_dir = os.path.join(base_dir, 'logs', 'dialogues')
        project_dir = os.path.normpath(os.path.join(base_dir, '..', '..', 'logs', 'dialogues'))
        for d in (internal_dir, project_dir):
            os.makedirs(d, exist_ok=True)
        all_dialogues = []
        for d in (internal_dir, project_dir):
            all_dialogues.extend(glob.glob(os.path.join(d, 'dialogue_*.md')))
        all_dialogues = sorted(set(all_dialogues))
        pending = [p for p in all_dialogues if not p.endswith('_done.md') and not p.endswith('_dup.md')]
        if len(pending) >= 20:
            batch = pending[:20]
            print(f"🔎 Обнаружено {len(pending)} необработанных диалогов — запускаю пакетный анализ 20...")
            try:
                run_batch_analysis_from_files(batch)
                for p in batch:
                    done_path = p[:-3] + '_done.md'
                    try:
                        os.rename(p, done_path)
                    except Exception:
                        pass
            except Exception as _:
                print("⚠️  Пакетный анализ не выполнен — будет попытка при следующем запуске.")
        return result
    except Exception as e:
        raise Exception(f"Ошибка при запуске системы бронирования: {e}")


def train():
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        AISocCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    try:
        AISocCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    
    try:
        AISocCrew().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


def run_batch_analysis(n: int = 20):
    base_dir = os.path.dirname(__file__)
    internal_dir = os.path.join(base_dir, 'logs', 'dialogues')
    project_dir = os.path.normpath(os.path.join(base_dir, '..', '..', 'logs', 'dialogues'))
    all_files = []
    for d in (internal_dir, project_dir):
        all_files.extend(glob.glob(os.path.join(d, 'dialogue_*.md')))
    files = sorted(set(all_files))[-n:]
    if not files:
        print("Нет файлов диалогов для анализа.")
        return

    parts = []
    for p in files:
        try:
            with open(p, 'r', encoding='utf-8') as f:
                parts.append(f"# {os.path.basename(p)}\n\n" + f.read())
        except Exception:
            continue
    payload = "\n\n".join(parts)

    # Ретраи с фолбэком модели
    attempts = 0
    last_err = None
    result = None
    fallback_model = "gemini/gemini-1.5-pro"
    while attempts < 5:
        try:
            crew_wrapper = AISocCrew()
            analyzer = crew_wrapper.dialogue_analyzer()
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            analysis_dir = os.path.join(base_dir, 'logs', 'analysis')
            os.makedirs(analysis_dir, exist_ok=True)
            batch_task = Task(
                description=(
                    "Проанализируй следующие диалоги (до 20) на качество сбора данных, ошибки и упущенные шаги. "
                    "Сформируй ПРЕДМЕТНЫЕ, ТОЧЕЧНЫЕ рекомендации по улучшению промпта агента бронирования БЕЗ автоматического изменения файлов.\n\n" + payload
                ),
                expected_output=(
                    "Краткий, но практичный отчёт с конкретными вставками для промпта/YAML без изменений конфигурации."
                ),
                agent=analyzer,
                output_file=os.path.join(analysis_dir, f'batch_analysis_{ts}.md')
            )

            crew = Crew(agents=[analyzer], tasks=[batch_task], process=Process.sequential, verbose=True)
            result = crew.kickoff()
            break
        except Exception as e:
            msg = str(e)
            last_err = e
            if (
                ("User location is not supported" in msg)
                or ("RESOURCE_EXHAUSTED" in msg)
                or ("RateLimitError" in msg)
                or ("list index out of range" in msg)
                or ("503" in msg)
                or ("UNAVAILABLE" in msg)
                or ("overloaded" in msg.lower())
                or ("404" in msg)
                or ("NOT_FOUND" in msg)
            ):
                wait_s = 3 * (2 ** attempts)
                jitter = random.uniform(0, 2)
                wait_total = min(30, wait_s + jitter)
                print(f"⏳ Ошибка LLM при анализе ('{msg[:100]}...'), повтор через {wait_total:.1f}s")
                time.sleep(wait_total)
                if attempts >= 2:
                    if os.getenv('MODEL') != fallback_model:
                        os.environ['MODEL'] = fallback_model
                        print(f"🔁 Переключаюсь на резервную модель для анализа: {fallback_model}")
                attempts += 1
                continue
            raise
    
    if result is None:
        print(f"❌ Анализ не удался после {attempts} попыток: {last_err}")
        return None
        
    print("Результат пакетного анализа:")
    print(result)
    return result


def run_batch_analysis_from_files(files: list[str]):
    if not files:
        print("Нет файлов для анализа.")
        return
    base_dir = os.path.dirname(__file__)
    parts = []
    for p in files:
        try:
            with open(p, 'r', encoding='utf-8') as f:
                parts.append(f"# {os.path.basename(p)}\n\n" + f.read())
        except Exception:
            continue
    payload = "\n\n".join(parts)

    # Ретраи с фолбэком модели
    attempts = 0
    last_err = None
    result = None
    fallback_model = "gemini/gemini-1.5-pro"
    while attempts < 5:
        try:
            crew_wrapper = AISocCrew()
            analyzer = crew_wrapper.dialogue_analyzer()
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            analysis_dir = os.path.join(base_dir, 'logs', 'analysis')
            os.makedirs(analysis_dir, exist_ok=True)
            batch_task = Task(
                description=(
                    "Проанализируй следующие диалоги на качество сбора данных, ошибки и упущенные шаги. "
                    "Сформируй ПРЕДМЕТНЫЕ, ТОЧЕЧНЫЕ рекомендации по улучшению промпта агента бронирования БЕЗ автоматического изменения файлов.\n\n" + payload
                ),
                expected_output=(
                    "Краткий, но практичный отчёт с конкретными вставками для промпта/YAML без изменений конфигурации."
                ),
                agent=analyzer,
                output_file=os.path.join(analysis_dir, f'batch_analysis_{ts}.md')
            )

            crew = Crew(agents=[analyzer], tasks=[batch_task], process=Process.sequential, verbose=True)
            result = crew.kickoff()
            break
        except Exception as e:
            msg = str(e)
            last_err = e
            if (
                ("User location is not supported" in msg)
                or ("RESOURCE_EXHAUSTED" in msg)
                or ("RateLimitError" in msg)
                or ("list index out of range" in msg)
                or ("503" in msg)
                or ("UNAVAILABLE" in msg)
                or ("overloaded" in msg.lower())
                or ("404" in msg)
                or ("NOT_FOUND" in msg)
            ):
                wait_s = 3 * (2 ** attempts)
                jitter = random.uniform(0, 2)
                wait_total = min(30, wait_s + jitter)
                print(f"⏳ Ошибка LLM при анализе файлов ('{msg[:100]}...'), повтор через {wait_total:.1f}s")
                time.sleep(wait_total)
                if attempts >= 2:
                    if os.getenv('MODEL') != fallback_model:
                        os.environ['MODEL'] = fallback_model
                        print(f"🔁 Переключаюсь на резервную модель для анализа файлов: {fallback_model}")
                attempts += 1
                continue
            raise
    
    if result is None:
        print(f"❌ Анализ файлов не удался после {attempts} попыток: {last_err}")
        return None
        
    print("Результат пакетного анализа (по списку файлов):")
    print(result)
    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "batch":
            n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
            run_batch_analysis(n)
        elif sys.argv[1] == "analyze":
            n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
            print(f"🔍 Запуск анализа последних {n} диалогов...")
            result = run_batch_analysis(n)
            if result:
                print("✅ Анализ завершён успешно!")
            else:
                print("❌ Анализ завершился с ошибкой")
        else:
            print("Использование:")
            print("  python main.py                    - запуск одного диалога")
            print("  python main.py batch [N]          - запуск N тестов подряд")
            print("  python main.py analyze [N]        - анализ последних N диалогов")
    else:
        run()
