# Калькулятор для зала — первая программа на Python.
# Запуск: в терминале VS Code набери   python gym.py
#
# Что делает:
#   1) спрашивает упражнение, рабочий вес и сколько повторов ты сделал;
#   2) считает разминочные подходы (сколько кг вешать на гриф);
#   3) подсказывает вес на следующую тренировку;
#   4) сохраняет результат в history.csv и в следующий раз показывает прошлый результат.

import csv
from datetime import date
from pathlib import Path

BAR = 20          # вес пустого грифа, кг
STEP = 2.5        # прибавка веса, кг
TARGET_REPS = 8   # сколько повторов считаем «выполнено»
HISTORY_FILE = Path(__file__).with_name("history.csv")  # файл лежит рядом с gym.py


def round_to_plates(weight, step=STEP):
    """Округляет вес до шага (по умолчанию 2,5 кг), чтобы его можно было собрать блинами."""
    return round(weight / step) * step


def warmup_sets(work_weight):
    """Возвращает список разминочных подходов: (вес, повторы)."""
    plan = [(0.0, 10), (0.4, 8), (0.6, 5), (0.8, 3)]  # доля от рабочего веса
    sets = []
    for share, reps in plan:
        w = max(BAR, round_to_plates(work_weight * share, step=5))  # разминка — шаг 5 кг
        if w < work_weight and (not sets or w > sets[-1][0]):
            sets.append((w, reps))
    return sets


def next_weight(work_weight, reps_done, feel):
    """Решает, добавлять ли вес на следующей тренировке."""
    if reps_done >= TARGET_REPS and feel >= 4:
        return work_weight + STEP, "Все повторы сделаны и было легко — добавляем 2,5 кг."
    if reps_done < TARGET_REPS - 2:
        return round_to_plates(work_weight * 0.9), "Повторов мало — снизим вес на 10% и наберём объём."
    return work_weight, "Оставляем вес и добиваем все повторы."


def ask_number(question):
    """Задаёт вопрос, пока не получит число. Принимает и запятую, и точку."""
    while True:
        answer = input(question).replace(",", ".").strip()
        try:
            return float(answer)
        except ValueError:
            print("  Нужно число, например 80 или 82,5. Попробуй ещё раз.")


def last_result(exercise):
    """Ищет в истории последнюю запись по упражнению. Если ничего нет — возвращает None."""
    if not HISTORY_FILE.exists():
        return None
    last = None
    with open(HISTORY_FILE, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            # сравниваем без учёта регистра: «жим лёжа» и «Жим лёжа» — одно и то же
            if row["упражнение"].lower() == exercise.lower():
                last = row  # записи идут по порядку, поэтому последняя найденная — самая свежая
    return last


def save_result(exercise, weight, reps):
    """Дописывает строку в history.csv. Если файла ещё нет — сначала пишет заголовок."""
    is_new = not HISTORY_FILE.exists()
    # utf-8-sig — чтобы Excel правильно показал русские буквы
    with open(HISTORY_FILE, "a", encoding="utf-8-sig" if is_new else "utf-8", newline="") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(["дата", "упражнение", "вес", "повторы"])
        writer.writerow([date.today().isoformat(), exercise, f"{weight:g}", reps])


def main():
    print("=== Калькулятор для зала ===")
    # убираем невидимый символ ﻿, который иногда подставляет терминал Windows
    exercise = input("Упражнение (например, Жим лёжа): ").replace("﻿", "").strip() or "Упражнение"

    last = last_result(exercise)
    if last:
        print(f"  Прошлый раз ({last['дата']}): {last['вес']} кг × {last['повторы']}")
    else:
        print("  По этому упражнению пока нет записей — это первая.")

    work = ask_number("Рабочий вес, кг: ")
    reps = int(ask_number(f"Сколько повторов сделал в последнем подходе (цель {TARGET_REPS}): "))
    feel = int(ask_number("Самочувствие от 1 до 5: "))

    print(f"\n{exercise}: разминка перед {work:g} кг")
    for i, (w, r) in enumerate(warmup_sets(work), start=1):
        per_side = (w - BAR) / 2
        plates = f"по {per_side:g} кг с каждой стороны" if per_side > 0 else "пустой гриф"
        print(f"  {i}. {w:g} кг × {r}  ({plates})")
    print(f"  Рабочие подходы: {work:g} кг × {TARGET_REPS}")

    new_w, reason = next_weight(work, reps, feel)
    print(f"\nВ следующий раз: {new_w:g} кг. {reason}")

    save_result(exercise, work, reps)
    print(f"Результат сохранён в {HISTORY_FILE.name}.")


if __name__ == "__main__":
    main()
