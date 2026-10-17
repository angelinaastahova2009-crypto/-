import re
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Уютный чтец текста",
    page_icon="📖",
    layout="wide",  # Разворачиваем на весь экран
)

# --- Блокировка прокрутки экрана на телефоне ---
st.markdown(
    """
<style>
    /* Отключаем прокрутку всей страницы */
    body, html, .stApp {
        overflow: hidden !important;
        position: fixed;
        width: 100%;
        height: 100%;
    }
</style>
""",
    unsafe_allow_html=True,
)

# --- Подключение обработчика клавиш (Стрелки Влево / Вправо) ---
components.html(
    """
<script>
const doc = window.parent.document;
doc.addEventListener('keydown', function(e) {
    if (e.key === 'ArrowLeft') {
        const btns = doc.querySelectorAll('button');
        btns.forEach(btn => {
            if (btn.innerText.includes('Назад')) {
                btn.click();
            }
        });
    } else if (e.key === 'ArrowRight') {
        const btns = doc.querySelectorAll('button');
        btns.forEach(btn => {
            if (btn.innerText.includes('Вперед')) {
                btn.click();
            }
        });
    }
});
</script>
""",
    height=0,
    width=0,
)

# Состояние приложения
if "step" not in st.session_state:
  st.session_state.step = "input"
if "text_items" not in st.session_state:
  st.session_state.text_items = []
if "current_index" not in st.session_state:
  st.session_state.current_index = 0
if "treat" not in st.session_state:
  st.session_state.treat = "Мороженое"

treats = {"Мороженое": "🍦", "Пончик": "🍩", "Печенька": "🍪", "Чипсы": "🍟"}

# --- ЭКРАН ВВОДА ---
if st.session_state.step == "input":
  st.title("📖 Уютный чтец текста")
  st.write("Введите или вставьте текст с абзацами:")

  raw_text = st.text_area("Текст", height=250, label_visibility="collapsed")

  st.session_state.treat = st.selectbox(
      "Выберите цель (вкусняшку):", list(treats.keys())
  )

  if st.button("Написать текст ✨", type="primary", use_container_width=True):
    if not raw_text.strip():
      st.warning("Поле ввода пустое!")
    else:
      paragraphs = raw_text.split("\n")
      collected_items = []
      for p_idx, paragraph in enumerate(paragraphs):
        clean_p = paragraph.strip()
        if not clean_p:
          continue
        sentences = re.split(r"(?<=[.!?])\s+", clean_p)
        sentences = [s.strip() for s in sentences if s.strip()]
        for s in sentences:
          collected_items.append({"type": "sentence", "text": s})

        if p_idx < len(paragraphs) - 1:
          remaining_text = "".join(paragraphs[p_idx + 1 :]).strip()
          if remaining_text:
            collected_items.append({
                "type": "transition",
                "text": "--- Переход на новый абзац ---",
            })

      if not collected_items:
        st.warning("Не удалось обработать текст.")
      else:
        st.session_state.text_items = collected_items
        st.session_state.current_index = 0
        st.session_state.step = "viewer"
        st.rerun()

# --- ЭКРАН ПРОСМОТРА ---
elif st.session_state.step == "viewer":
  text_items = st.session_state.text_items
  idx = st.session_state.current_index
  total = len(text_items)

  # Визуализация пути человечка (развёрнутого вправо к вкусняшке)
  treat_emoji = treats.get(st.session_state.treat, "🍩")
  progress_ratio = idx / max(1, total - 1)
  track_length = 16
  human_pos = int(progress_ratio * track_length)

  left_path = "➖" * human_pos
  right_path = "➖" * (track_length - human_pos)

  # Стиль CSS для поворота человечка лицом вправо (scaleX(-1))
  human_html = (
      "<span style='display: inline-block; transform: scaleX(-1);'>🏃‍♂️</span>"
  )

  path_html = f"<div style='font-size: 28px; text-align: center;'>{left_path}{human_html}{right_path} {treat_emoji}</div>"

  st.markdown(path_html, unsafe_allow_html=True)
  st.markdown(
      f"<p style='text-align: center; color: #888; font-size: 16px;'>"
      f"Предложение {idx + 1} из {total}</p>",
      unsafe_allow_html=True,
  )

  current_item = text_items[idx]

  # Вывод предложения с крупным шрифтом на весь экран
  if current_item["type"] == "transition":
    st.markdown(
        f"<h2 style='color: #D32F2F; text-align: center; margin: 60px 20px;'>"
        f"{current_item['text']}</h2>",
        unsafe_allow_html=True,
    )
  else:
    st.markdown(
        f"<h1 style='text-align: center; margin: 60px 20px; font-size: 38px;'>"
        f"{current_item['text']}</h1>",
        unsafe_allow_html=True,
    )

  st.write("---")

  # Кнопки управления
  col1, col2, col3 = st.columns([1, 1, 1])

  with col1:
    if st.button("← Назад", disabled=(idx == 0), use_container_width=True):
      if idx > 0:
        st.session_state.current_index -= 1
        st.rerun()

  with col2:
    if st.button("Изменить текст", use_container_width=True):
      st.session_state.step = "input"
      st.rerun()

  with col3:
    if st.button("Вперед →", use_container_width=True):
      if idx < total - 1:
        st.session_state.current_index += 1
        st.rerun()
      else:
        st.session_state.step = "celebration"
        st.rerun()

# --- ФИНАЛЬНЫЙ ЭКРАН ---
elif st.session_state.step == "celebration":
  st.markdown(
      "<h1 style='text-align: center; color: #E91E63; margin-top: 50px;'>🎆🎉"
      " УРА! ТЕКСТ УСПЕШНО НАПИСАН! 🎉🎆</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<h2 style='text-align: center;'>✨ 🎇 ✨ 🎇 ✨</h2>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; font-size: 22px;'>Поздравляем! Вы прошли"
      " весь путь !</p>",
      unsafe_allow_html=True,
  )

  if st.button(
      "Написать другой текст 🔄", type="primary", use_container_width=True
  ):
    st.session_state.step = "input"
    st.rerun()