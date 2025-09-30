# frontend/app.py
import os
from .views.ui import build_ui
from .controllers.news_controller import update_all_with_state, detail_by_index

def main():
    app = build_ui(update_all_with_state, detail_by_index)
    port = int(os.getenv("PORT", "7860"))
    # הדפסה ידידותית לפני ההרצה (כדי שתראי ב-log של Docker/טרמינל)
    url = f"http://localhost:{port}"
    print(f"🚀 Interface available at: {url}")
    app.launch(server_name="0.0.0.0", server_port=port, show_api=False, share=False)

if __name__ == "__main__":
    main()
