from pccom import Bot

if __name__ == "__main__":
    pccom = Bot(username="xxx", password="xxx", debug=True)
    pccom.run_item(item_url="https://www.pccomponentes.com/asus-tuf-geforce-rtx-3090-gaming-oc-24gb-gddr6x", price_limit=900)
