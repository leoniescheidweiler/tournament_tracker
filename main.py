import logic
import ui_controller

if __name__ == "__main__":
    tournament = logic.Tournament()

    ui_controller = ui_controller.Ui_controller(tournament)
    ui_controller.root.mainloop()
