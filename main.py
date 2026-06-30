# ======================================
# main.py — Orchestrates RSS → Summary → Telegram
# ======================================

from utils.rss_reader import fetch_new_articles
from utils.summarizer import summarize_text
from utils.telegram_bot import send_telegram_message
from utils.rag_store import add_summary_to_store

# === НОВЫЙ БЛОК: Ваши ключевые слова для фильтрации ===
# Добавьте сюда все ваши темы и их синонимы (на русском и английском)
MY_TOPICS = {
    "финтех и ИИ": ["финтех", "ИИ"],
    "психология и ИИ": ["психология", "ИИ"],
    "продуктивность и ИИ": ["продуктивность", "ИИ"],
    "исследования и ИИ": ["экономические исследования", "ИИ"],
    "поведенческая экономика": ["поведенческая экономика"],
    "клинцы": ["клинцы", "клинцовский", "клинцовском", "клинцов", "клинчане"],
    "цска": ["цска", "cska"]
}

def is_article_relevant(title, summary):
    """
    Проверяет, соответствует ли статья хотя бы одной теме из MY_TOPICS.
    Возвращает True, если статья подходит.
    """
    # Объединяем заголовок и краткое содержание для поиска
    text_to_check = (title + " " + summary).lower()
    
    for topic, keywords in MY_TOPICS.items():
        # Проверяем, есть ли в тексте ВСЕ слова из текущей темы
        # (например, для "финтех" должны быть и "финтех", и "fintech"? 
        # Если нужно ИЛИ, замените all на any)
        if all(keyword in text_to_check for keyword in keywords):
            return True
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