import whatsapp_api
from threading import Thread
import easygui

import time

BUTTON_OPTIONS = [
    ["Stop Scan", "Start Scan"],
    ["Hide Scan", "Show Scan"],
]


def gui_main(whats_client):
    easygui.buttonbox(
        (
            "Welcome to the Whatsapp Hacker Control Panel!\n"
            "Click the button below to get started"
        ),
        "WH4t5apP HAck3R", ["Initialize Scan"]
    )
    whats_client.init_scan = True

    while True:
        buttons = list(whats_client.get_scan_mode())

        for i in range(len(BUTTON_OPTIONS)):
            buttons[i] = BUTTON_OPTIONS[i][not buttons[i]]

        ans = easygui.buttonbox(
            (
                "Welcome to the Whatsapp Hacker Control Panel!\n"
                "Choose one of the options below to get started"
            ),
            "WH4t5apP HAck3R", buttons + ["Kill Scan"]
        )

        print(ans)

        if ans in BUTTON_OPTIONS[0]:
            whats_client.play_scan = not whats_client.play_scan
        elif ans in BUTTON_OPTIONS[1]:
            whats_client.show_scan = not whats_client.show_scan
        else:
            whats_client.kill_scan = True
            return


def main():
    whats_client = whatsapp_api.WhatsappClient()

    p = Thread(target=gui_main, args=(whats_client,))
    p.start()

    while not whats_client.init_scan:
        time.sleep(1)

    whats_client.initialize(initialize=False)

    while not whats_client.kill_scan:
        print("Starting contacts scan")
        whats_client.scan_users()
        time.sleep(0.5)

    whats_client.close_conn()

    p.join()


if __name__ == "__main__":
    main()
