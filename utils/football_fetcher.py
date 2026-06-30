# utils/football_fetcher.py

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def fetch_tournament_schedule(tournament_id: str):
    """
    Получает расписание матчей для турнира с Nagradion.ru по его ID.
    Возвращает список словарей с данными о матчах.
    """
    url = f"https://boff32.nagradion.ru/tournament{tournament_id}/calendar"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Проверяем, что запрос успешен
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при загрузке страницы {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    matches = []

    # Ищем все таблицы с расписанием
    # На сайте используется таблица с классом, или просто все таблицы в основном блоке
    # Примерный селектор: нужно будет уточнить после анализа страницы
    tables = soup.find_all("table")
    
    for table in tables:
        # Проверяем, что таблица содержит данные о матчах (например, есть колонка "Команды")
        headers = table.find_all("th")
        if not headers or "Команды" not in headers[0].text:
            continue
            
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 4:  # Если колонок меньше 4, это не строка с матчем
                continue
                
            # Извлекаем данные из ячеек
            # Порядок колонок: Дата | Команды | Счёт | Стадион
            date_cell = cells[0].text.strip()
            teams_cell = cells[1].text.strip()
            score_cell = cells[2].text.strip()
            stadium_cell = cells[3].text.strip() if len(cells) > 3 else ""
            
            # Разбираем команды (они разделены тире)
            teams = teams_cell.split("—")
            if len(teams) == 2:
                team1 = teams[0].strip().strip('"')
                team2 = teams[1].strip().strip('"')
            else:
                continue
                
            # Извлекаем дату и время из первой колонки (она может быть в формате "ДД.ММ.ГГГГ День Время")
            date_match = re.search(r"(\d{2}\.\d{2}\.\d{4})", date_cell)
            date_str = date_match.group(1) if date_match else ""
            
            # Извлекаем счет (если есть)
            score_match = re.search(r"(\d+):(\d+)", score_cell)
            if score_match:
                score1, score2 = score_match.groups()
            else:
                score1, score2 = "-", "-"

            match_data = {
                "date": date_str,
                "time": "",  # Можно извлечь отдельно, если нужно
                "team1": team1,
                "team2": team2,
                "score1": score1,
                "score2": score2,
                "stadium": stadium_cell,
                "raw_date": date_cell
            }
            matches.append(match_data)

    return matches

# Функция для получения и форматирования сообщения для Telegram
def get_football_news():
    """
    Основная функция, которую вы вызываете из main.py.
    Возвращает отформатированное сообщение с результатами последних туров.
    """
    # Получаем данные для чемпионата (ID 45046)
    league_matches = fetch_tournament_schedule("45046")
    # Для кубка (ID 45050) раскомментируйте следующую строку
    # cup_matches = fetch_tournament_schedule("45050")
    
    if not league_matches:
        return "⚽ Новых результатов матчей не найдено."
    
    # Формируем сообщение
    message = "⚽ **Последние результаты матчей:**\n\n"
    
    # Оставляем только матчи, где есть счет (уже сыгранные)
    played_matches = [m for m in league_matches if m['score1'] != '-']
    # Берем последние 10 сыгранных матчей (они в конце списка)
    recent_matches = played_matches[-10:]
    
    for match in recent_matches:
        message += f"**{match['team1']}** {match['score1']} : {match['score2']} **{match['team2']}**\n"
        message += f"📅 {match['date']} | 🏟 {match['stadium']}\n\n"
    
    return message