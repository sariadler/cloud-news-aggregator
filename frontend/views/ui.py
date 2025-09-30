# frontend/views/ui.py
import gradio as gr
from typing import Callable, Tuple, List, Any

"""
הקונטרולר צריך לספק שתי פונקציות:

update_all_with_state(category, limit, q, sort_by, order, page, page_size)
  -> Tuple[
       str,                  # cards_md
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

def build_ui(update_all_with_state: UpdateWithStateFn, detail_by_index: DetailFn) -> gr.Blocks:
    CATEGORIES = ["all", "tech", "politics", "sport", "business", "world", "health"]
    SORT_FIELDS = ["publishedAt", "score", "title"]
    ORDERS = ["asc", "desc"]

    with gr.Blocks(title="Cloud News Aggregator") as demo:
        gr.Markdown("## 📰 Cloud News Aggregator")

        # קלטים עליונים
        with gr.Row():
            category = gr.Dropdown(CATEGORIES, value="all", label="קטגוריה")
            limit = gr.Slider(5, 100, value=50, step=5, label="מקסימום תוצאות (לפני עימוד)")
            query = gr.Textbox(label="חיפוש")
        with gr.Row():
            sort_by = gr.Dropdown(SORT_FIELDS, value="publishedAt", label="מיון לפי")
            order = gr.Radio(ORDERS, value="desc", label="סדר")
            page_size = gr.Slider(5, 50, value=10, step=5, label="לכל עמוד")

        # מצב מערכת
        data_state = gr.State([])   # פריטי העמוד הנוכחי (dict לכל כתבה)
        page_state = gr.State(1)    # עמוד נוכחי (int)

        # יציאות: כרטיסיות/טבלה/פרטים/מידע עמודים
        with gr.Tabs():
            with gr.Tab("כרטיסיות"):
                cards_md = gr.Markdown()
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

        # --- פונקציות עזר מקומיות ---

        def _update_all(cat, lim, q, sb, ord_, page, psize):
            cards, tbl, data, titles, total = update_all_with_state(cat, lim, q, sb, ord_, page, psize)
            total_text = f"סה\"כ תוצאות: {total} | עמוד {page}"
            return (
                cards,              # cards_md
                tbl,                # table
                data,               # data_state
                gr.update(choices=titles, value=(titles[0] if titles else None)),  # chosen
                total_text          # total_md
            )

        def _on_choose(title, data):
            if not data or not title:
                return "לא נבחרה כתבה."
            idx = next((i for i, a in enumerate(data) if a.get("title", "") == title), -1)
            return detail_by_index(data, idx)

        def _set_loading():
            return gr.update(visible=True, value="⏳ טוען חדשות...")

        def _clear_loading():
            return gr.update(visible=False)

        def _next(page):
            return page + 1

        def _prev(page):
            return max(1, page - 1)

        # ניקוי שדה החיפוש
        clear_btn.click(lambda: "", None, query)

        # --- חיווט: טעינה ראשונית / שינויי קלט / עימוד / רענון ---

        # טעינה ראשונית
        demo.load(_set_loading, None, [loading_md]).then(
            _update_all,
            inputs=[category, limit, query, sort_by, order, page_state, page_size],
            outputs=[cards_md, table, data_state, chosen, total_md]
        ).then(_clear_loading, None, [loading_md])

        # רענון ידני
        refresh.click(_set_loading, None, [loading_md]).then(
            _update_all,
            inputs=[category, limit, query, sort_by, order, page_state, page_size],
            outputs=[cards_md, table, data_state, chosen, total_md]
        ).then(_clear_loading, None, [loading_md])

        # שינויי פרמטרים → עמוד חוזר ל-1
        def _reset_page():
            return 1

        for comp in (category, limit, query, sort_by, order, page_size):
            comp.change(_reset_page, None, page_state).then(
                _set_loading, None, [loading_md]
            ).then(
                _update_all,
                inputs=[category, limit, query, sort_by, order, page_state, page_size],
                outputs=[cards_md, table, data_state, chosen, total_md]
            ).then(_clear_loading, None, [loading_md])

        # פרטי כתבה
        chosen.change(_on_choose, inputs=[chosen, data_state], outputs=[detail_md])

        # עימוד: הבא/הקודם
        next_btn.click(_next, inputs=[page_state], outputs=[page_state]).then(
            _set_loading, None, [loading_md]
        ).then(
            _update_all,
            inputs=[category, limit, query, sort_by, order, page_state, page_size],
            outputs=[cards_md, table, data_state, chosen, total_md]
        ).then(_clear_loading, None, [loading_md])

        prev_btn.click(_prev, inputs=[page_state], outputs=[page_state]).then(
            _set_loading, None, [loading_md]
        ).then(
            _update_all,
            inputs=[category, limit, query, sort_by, order, page_state, page_size],
            outputs=[cards_md, table, data_state, chosen, total_md]
        ).then(_clear_loading, None, [loading_md])

        # Polling אוטומטי כל 15 שניות
        poller = gr.Timer(15.0)
        poller.tick(
            _update_all,
            inputs=[category, limit, query, sort_by, order, page_state, page_size],
            outputs=[cards_md, table, data_state, chosen, total_md]
        )

    return demo
