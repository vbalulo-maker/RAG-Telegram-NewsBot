# ======================================
# main.py — Orchestrates RSS → Summary → Telegram
# ======================================

from utils.rss_reader import fetch_new_articles
from utils.summarizer import summarize_text
from utils.telegram_bot import send_telegram_message
from utils.rag_store import add_summary_to_store

# === НОВЫЙ БЛОК: Ваши ключевые слова для фильтрации ===
# Вместо простого списка ключевых слов, сделайте для каждой темы словарь
MY_TOPICS = {
    "финтех": {
        "keywords": ["финтех", "ИИ"],
        "match": "all"  # Нужны все слова из списка
    },
    "банки и техи": {
        "keywords": ["сбер", "т-банк", "т-технологии", "альфа-банк", "авито", "яндекс", "втб"],
        "match": "any"  # Достаточно любого слова из списка
    },
    "психология": {
        "keywords": ["психология", "ИИ"],
        "match": "all"
    },
    "продуктивность": {
        "keywords": ["продуктивность", "ИИ"],
        "match": "all"
    },
    "цска": {
        "keywords": ["цска"],
        "match": "any"
    },
    "экономика": {
        "keywords": ["экономическое исследование", "поведенческая экономика", "economics", "инфляция", "ставка"],
        "match": "any"
    },
    "Клинцы": {
        "keywords": ["клинцы", "клинцовский", "клинцов", "клинчане"],
        "match": "any"
    }
}

def is_article_relevant(title, summary):
    """
    Проверяет, соответствует ли статья хотя бы одной теме из MY_TOPICS.
    Для каждой темы используется своё правило (all или any).
    """
    text_to_check = (title + " " + summary).lower()
    
    for topic, config in MY_TOPICS.items():
        keywords = config["keywords"]
        match_rule = config.get("match", "all")  # По умолчанию all, если не указано
        
        # Проверяем, сколько ключевых слов из темы найдено в тексте
        found_keywords = [kw for kw in keywords if kw in text_to_check]
        
        if match_rule == "all":
            # Для правила all: нужны все ключевые слова
            if len(found_keywords) == len(keywords):
                return True
        elif match_rule == "any":
            # Для правила any: достаточно хотя бы одного
            if len(found_keywords) > 0:
                return True
        # Можно добавить другие правила, например, "most" (большинство)
    
    return False

# === КОНЕЦ НОВОГО БЛОКА ===

def main():
    print("Starting RAG Telegram Scheduler...\n")

    # Step 1: Fetch new articles
    articles = fetch_new_articles()

    if not articles:
        print("No new articles found. Exiting.")
        return

    print(f"Found {len(articles)} new articles to process.\n")

    # Step 2: Process each article
    for idx, article in enumerate(articles, 1):
        print(f"[{idx}] Summarizing: {article['title'][:80]}...")
        summary = summarize_text(article["summary"])

        # === НОВЫЙ ШАГ: Фильтрация по темам ===
        # Если статья НЕ подходит по темам, пропускаем её (не отправляем и не сохраняем)
        if not is_article_relevant(article['title'], summary):
            print(f"  → Skipped: does not match any topic.")
            continue  # Переходим к следующей статье

        # Step 3: Format Telegram message (только для подходящих статей)
        message = (
            f"<b>{article['title']}</b>\n\n"
            f"{summary}\n\n"
            f"<a href='{article['link']}'>Read more</a>"
        )

        # Step 4: Send to Telegram
        send_telegram_message(message)

        # Step 5: Store summary in RAG store
        add_summary_to_store(article["title"], summary, article["link"])

    print("\nAll new articles summarized and sent to Telegram!")

if __name__ == "__main__":
    main()


from utils.football_fetcher import get_football_news

def main():
    # ... ваш существующий код для RSS и фильтрации ...
    
    # --- Добавьте этот блок ---
    # Получаем и отправляем футбольные результаты
    football_message = get_football_news()
    if football_message:
        # Отправляем отдельным сообщением
        send_telegram_message(football_message)
        print("Football data sent!")
    # --- Конец блока ---