import requests
import json
import datetime
from discord_webhook import DiscordWebhook, DiscordEmbed


WISHLIST_URL = 'https://www.lamoda.ru/wishlist/?sv=dsk&page='
PROXY_LIST = [
    '45.89.60.73', '45.8.147.250', '176.125.243.228', '46.8.13.36', '62.3.63.164',
]


admin_webhook_url = 'url'
admin_webhook = DiscordWebhook(url=admin_webhook_url, rate_limit_retry=True, username="LAMODA")


product_status = {}



def monitor_wishlist():
    link_numb = 1

    while True:


        try:
            response = requests.get(f'{WISHLIST_URL}{link_numb}', headers=get_headers(), proxies=proxy)
            if link_numb != links_quanity:
                link_numb += 1
            else:
                link_numb = 1


            info = response.text.split('payload: ')[-1].split('settings: ')[0][:-6]
            json_object = json.loads(info)

            products = json_object["products"]

            for product in products:
                process_product(product)

        except Exception as ex:
            print(ex)


def process_product(product):
    name = product["model_name"]
    sizes = product["sizes"]
    img = 'https://a.lmcdn.ru/img236x341' + product["thumbnail"]
    price = product["price_amount"]
    p_link = f'https://www.lamoda.ru/p/{product["sku"]}'
    sizes_webhook = get_sizes_webhook(sizes)

    if sizes_webhook == '':
        sizes_webhook = 'OOS'

    if p_link not in product_status:
        product_status[p_link] = {"sizes": sizes_webhook, "in_stock": False}

    if sizes_webhook:
        product_status[p_link]["sizes"] = sizes_webhook
        product_status[p_link]["in_stock"] = True

    if product_status[p_link]["in_stock"]:
        action(name, p_link, img, price, sizes_webhook, product["sku"])

def action(name, p_link, img, price, sizes_webhook, sku):
    embed_success = DiscordEmbed(title=name, url=p_link, color='ffffff')
    embed_success.set_thumbnail(url=img)
    embed_success.add_embed_field(name='Price:', value=f'{price} ₽')
    embed_success.add_embed_field(name='Sizes:', value=sizes_webhook)
    embed_success.add_embed_field(name='PID:', value=sku)
    embed_success.set_footer(text='Developed by Misha Ivakhov\n' + str(datetime.datetime.now()), icon_url='URL')
    admin_webhook.add_embed(embed_success)
    admin_webhook.execute()

def get_sizes_webhook(sizes):
    sizes_webhook = ''
    for size in sizes:
        if size["is_available"]:
            size_status = ' [LAST]' if size["is_last"] else ' [2+]'
            sizes_webhook += f'\n{size["brand_size"]}{size_status}'
    return sizes_webhook

def get_headers():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
        'Cookie': 'COOKIE_DATA',
        'User-Agent': 'USER_AGENT'
    }
    return headers

if __name__ == '__main__':
    links_quanity = int(input('ENTER PAGINATION OF WISHLIST: '))
    monitor_wishlist()
