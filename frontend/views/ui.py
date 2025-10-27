import gradio as gr
from typing import Callable, Tuple, List, Any

"""
הקונטרולר צריך לספק שתי פונקציות:

update_all_with_state(category, limit, q, sort_by, order, page, page_size)
  -> Tuple[
       str,                  # cards_html (HTML מוכן לכרטיסיות)
       List[List[Any]],      # table rows
       List[dict],           # data_state (page items)
       List[str],            # titles (page items)
       int                   # total (all items count before paging)
     ]

detail_by_index(data_state: List[dict], index: int) -> str
"""

UpdateWithStateFn = Callable[[str, int, str, str, str, int, int],
                             Tuple[str, List[List[Any]], List[dict], List[str], int]]
DetailFn = Callable[[List[dict], int], str]

# CSS מותאם אישית
custom_css = """
/* רקע כללי */
.gradio-container { background: #f9fbfd; }

/* טקסט כותרות */
h2, h3 { font-family: "Segoe UI", Arial, sans-serif; }

/* עיצוב כרטיסיות */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-top: 15px;
}
.card {
  background: #fff;
  border-radius: 12px;
  padding: 15px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.08);
}
.card h3 { color: #1d4ed8; margin-bottom: 8px; }
.card img { width: 100%; border-radius: 8px; margin-bottom: 10px; }
.card .meta { font-size: 0.85em; color: #555; margin-bottom: 6px; }
.card a {
  display:inline-block;
  margin-top:8px;
  background:linear-gradient(90deg,#6366f1,#3b82f6);
  color:#fff;
  padding:6px 12px;
  border-radius:6px;
  font-weight:600;
  text-decoration:none;
}
.card a:hover { filter: brightness(1.1); }
"""

theme = gr.themes.Soft(primary_hue="blue", neutral_hue="slate")


def build_ui(update_all_with_state: UpdateWithStateFn, detail_by_index: DetailFn) -> gr.Blocks:
    CATEGORIES = ["all", "tech", "politics", "sport", "business", "world", "health"]
    SORT_FIELDS = ["publishedAt", "score", "title"]
    ORDERS = ["asc", "desc"]

    with gr.Blocks(title="Cloud News Aggregator", css=custom_css, theme=theme) as demo:
        gr.Markdown("## 📰 Cloud News Aggregator")

        # קלטים עליונים
        with gr.Row():
            category = gr.Dropdown(CATEGORIES, value="all", label="קטגוריה")
            limit = gr.Slider(5, 100, value=50, step=5, label="מקסימום תוצאות (לפני עימוד)")
            query = gr.Textbox(label="חיפוש")
        with gr.Row():
            sort_by = gr.Dropdown(SORT_FIELDS, value="publishedAt", label="מיון לפי")
            order = gr.Radio(ORDERS, value="desc", label="סדר")
            page_size = gr.Slider(5, 50, value=9, step=3, label="לכל עמוד")

        # State פנימי
        data_state = gr.State([])   # נתוני עמוד
        page_state = gr.State(1)    # מספר עמוד

        # יציאות
        with gr.Tabs():
            with gr.Tab("כרטיסיות"):
                cards_html = gr.HTML()  # HTML במקום Markdown
            with gr.Tab("טבלה"):
                table = gr.Dataframe(
                    headers=["כותרת", "קטגוריה", "ציון", "תאריך", "קישור"],
                    row_count=10,
                    wrap=True
                )
            with gr.Tab("פרטים"):
                with gr.Row():
                    chosen = gr.Dropdown(choices=[], label="בחרי כתבה")
                detail_md = gr.Markdown("בחרי כתבה מהרשימה.")

        with gr.Row():
            refresh = gr.Button("רענון")
            clear_btn = gr.Button("נקה חיפוש")
            prev_btn = gr.Button("◀ הקודם")
            next_btn = gr.Button("▶ הבא")
            total_md = gr.Markdown()  # “סה"כ תוצאות | עמוד X”

        # מצב טעינה
        loading_md = gr.Markdown(visible=False)

        # --- פונקציות עזר ---

        def update_all(cat, lim, q, sb, ord, page, psize):
            cards, tbl, data, titles, total = update_all_with_state(cat, lim, q, sb, ord, page, psize)
            total_text = f"סה\"כ תוצאות: {total} | עמוד {page}"
            return (
                cards, tbl, data,
                gr.update(choices=titles, value=(titles[0] if titles else None)),
                total_text
            )

        def _on_choose(title, data):
            if not data or not title:
                return "לא נבחרה כתבה."
            idx = next((i for i, a in enumerate(data) if a.get("title", "") == title), -1)
            return detail_by_index(data, idx)

        def _set_loading(): return gr.update(visible=True, value="⏳ טוען חדשות...")
        def _clear_loading(): return gr.update(visible=False)
        def _next(page): return page + 1
        def _prev(page): return max(1, page - 1)
        def _reset_page(): return 1

        clear_btn.click(lambda: "", None, query)

        # טעינה ראשונית
        demo.load(_set_loading, None, [loading_md]).then(
            update_all,
            inputs=[category, limit, query, sort_by, order, page_state, page_size],
            outputs=[cards_html, table, data_state, chosen, total_md]
        ).then(_clear_loading, None, [loading_md])

        # רענון
        refresh.click(_set_loading, None, [loading_md]).then(
            update_all,
            inputs=[category, limit, query, sort_by, order, page_state, page_size],
            outputs=[cards_html, table, data_state, chosen, total_md]
        ).then(_clear_loading, None, [loading_md])

        # שינוי פרמטרים → עמוד חוזר ל־1
        for comp in (category, limit, query, sort_by, order, page_size):
            comp.change(_reset_page, None, page_state).then(
                _set_loading, None, [loading_md]
            ).then(
                update_all,
                inputs=[category, limit, query, sort_by, order, page_state, page_size],
                outputs=[cards_html, table, data_state, chosen, total_md]
            ).then(_clear_loading, None, [loading_md])

        # פרטים
        chosen.change(_on_choose, inputs=[chosen, data_state], outputs=[detail_md])

        # עימוד
        next_btn.click(_next, inputs=[page_state], outputs=[page_state]).then(
            _set_loading, None, [loading_md]
        ).then(
            update_all,
            inputs=[category, limit, query, sort_by, order, page_state, page_size],
            outputs=[cards_html, table, data_state, chosen, total_md]
        ).then(_clear_loading, None, [loading_md])

        prev_btn.click(_prev, inputs=[page_state], outputs=[page_state]).then(
            _set_loading, None, [loading_md]
        ).then(
            update_all,
            inputs=[category, limit, query, sort_by, order, page_state, page_size],
            outputs=[cards_html, table, data_state, chosen, total_md]
        ).then(_clear_loading, None, [loading_md])

        # Polling
        poller = gr.Timer(15.0)
        poller.tick(
            update_all,
            inputs=[category, limit, query, sort_by, order, page_state, page_size],
            outputs=[cards_html, table, data_state, chosen, total_md]
        )

    return demo