import whatsapp_api

import time


def main():
    whats_client = whatsapp_api.WhatsappClient(initialize=True)

    while True:
        print("Starting contacts scan")
        whats_client.scan_users()
        time.sleep(0.5)

    whats_client.close_conn()


if __name__ == "__main__":
    main()
