from RAT_PANEL.ui.main_gui import ClientAppUI
from logic.client_logic import ClientLogic

def main():
    # יצירת לוגיקה ו-UI + חיבור דו-כיווני
    logic = ClientLogic()
    ui = ClientAppUI(logic)
    logic.attach_ui(ui)
    ui.run()

if __name__ == "__main__":
    main()
