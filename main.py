import whatsapp_api

import time


def main():
    whats_client = whatsapp_api.WhatsappClient()

    while True:
        print("Starting contacts scan")
        whats_client.scan_users()
        time.sleep(10)

    whats_client.close_conn()


if __name__ == "__main__":
    main()
