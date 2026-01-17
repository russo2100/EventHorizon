import streamlit as st
import requests
import json
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# Настройка страницы
st.set_page_config(
    page_title="EventHorizon - RAG Analytics",
    page_icon="🌌",
    layout="wide"
)

# Заголовок
st.title("🌌 EventHorizon")
st.markdown("**Платформа для анализа событий с использованием RAG (Retrieval-Augmented Generation)**")

# Боковая панель
with st.sidebar:
    st.header("⚙️ Настройки")
    
    # Проверка здоровья системы
    try:
        health = requests.get(f"{API_URL}/health").json()
        if health["status"] == "healthy":
            st.success("✅ Система активна")
            st.info(f"🤖 LLM: {health.get('llm_engine', 'N/A')}")
        else:
            st.error("❌ Система недоступна")
    except:
        st.error("❌ API недоступен. Запустите сервер:\n`python -m src.api.main`")
    
    st.divider()
    
    # Добавление событий
    st.subheader("📥 Добавить событие")
    with st.form("add_event_form"):
        event_content = st.text_area("Текст события", height=100)
        event_source = st.text_input("Источник", placeholder="EIA, Bloomberg...")
        event_date = st.date_input("Дата")
        
        submitted = st.form_submit_button("Добавить")
        if submitted and event_content:
            try:
                response = requests.post(
                    f"{API_URL}/ingest/",
                    json={
                        "content": event_content,
                        "metadata": {
                            "source": event_source,
                            "date": str(event_date)
                        }
                    }
                )
                if response.status_code == 200:
                    st.success(f"✅ Событие добавлено (ID: {response.json()['event_id']})")
                else:
                    st.error("❌ Ошибка при добавлении")
            except Exception as e:
                st.error(f"❌ {e}")

# Основная область - Анализ
st.header("🔍 RAG-Анализ")

query = st.text_input(
    "Введите запрос для анализа:",
    placeholder="Например: Какие факторы влияют на цены на газ?"
)

limit = st.slider("Количество релевантных событий:", 1, 10, 5)

if st.button("🚀 Запустить анализ", type="primary"):
    if not query:
        st.warning("⚠️ Введите запрос")
    else:
        with st.spinner("⏳ Анализирую..."):
            try:
                response = requests.post(
                    f"{API_URL}/analyze/",
                    json={"query": query, "limit": limit}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Результат анализа
                    st.subheader("📊 Результат анализа")
                    st.markdown(result["analysis"])
                    
                    # Релевантные события
                    if result["relevant_events"]:
                        st.divider()
                        st.subheader("📚 Релевантные события")
                        
                        for i, event in enumerate(result["relevant_events"], 1):
                            with st.expander(f"Событие {i} (релевантность: {event['score']:.2%})"):
                                st.write(event["text"])
                                st.caption(f"ID: {event['id']}")
                    else:
                        st.info("Релевантных событий не найдено")
                        
                else:
                    st.error(f"❌ Ошибка API: {response.text}")
                    
            except Exception as e:
                st.error(f"❌ Ошибка: {e}")

# Поиск событий
st.divider()
st.header("🔎 Поиск событий")

search_query = st.text_input(
    "Поиск в базе событий:",
    placeholder="Введите ключевые слова..."
)

if st.button("Поиск"):
    if search_query:
        with st.spinner("Ищу..."):
            try:
                response = requests.post(
                    f"{API_URL}/search/",
                    json={"query": search_query, "limit": 10}
                )
                
                if response.status_code == 200:
                    results = response.json()
                    
                    if results:
                        st.success(f"✅ Найдено событий: {len(results)}")
                        
                        for i, result in enumerate(results, 1):
                            with st.container():
                                col1, col2 = st.columns([4, 1])
                                with col1:
                                    st.markdown(f"**{i}.** {result['text']}")
                                with col2:
                                    st.metric("Релевантность", f"{result['score']:.2%}")
                                st.divider()
                    else:
                        st.info("Событий не найдено")
                        
            except Exception as e:
                st.error(f"❌ Ошибка: {e}")

# Футер
st.divider()
st.caption("💡 Powered by txtai + DeepSeek R1 + FastAPI | EventHorizon v2.0")
