import whatsapp_api

import time


def main():
    whats_client = whatsapp_api.WhatsappClient()
    print("Sending message now")
    whats_client.get_contact_time()
    whats_client.close_conn()


if __name__ == "__main__":
    main()
