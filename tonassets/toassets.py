import yaml
import os
import requests
import json
from requests_cache import CachedSession
import shutil

# https://github.com/tonkeeper/ton-assets
jettons_dir = 'ton-assets/jettons/'

cached_requests = CachedSession('tmp/cache')

def get_jetton_info(address_url):
    return cached_requests.get('https://tonapi.io/v2/jettons/' + address_url).json()

def get_friendly_address(address_url):
    return cached_requests.get('https://toncenter.com/api/v2/detectAddress?address=' + address_url, headers={'X-API-Key': '<api key>'}).json()

def get_address_url(address):
    address_url = '0%3A' + address[2:] if address[0] == '0' else address
    return address_url

link_stats = {}

def update_links(metadata, result_info):
    links = metadata.get('websites', []) + metadata.get('social', [])
    if links:
        # print(links)
        website = links[0]
        links = links[1:]
        linksout = {}

        for link in links:
            was = False

            if 'https://t.me' in link and 'telegram' not in linksout:
                linksout['telegram'] = link
            elif 'https://t.me' in link and 'telegram_news' not in linksout and 'telegram' in linksout:
                linksout['telegram_news'] = link


            for social in ['github', 'whitepaper', 'twitter', 'telegram', 'telegram_news', 'medium', 'discord', 'reddit', 'facebook', 'youtube', 'coinmarketcap', 'coingecko', 'blog', 'forum', 'docs', 'source_code']:
                if social in link:
                    was = True
                    if social not in link_stats:
                        link_stats[social] = []
                    link_stats[social].append(link)
                    linksout[social] = link

            if not was and 'https://t.me' not in link:
                print('unknown: ', link)

            linksres = []
            for key, value in linksout.items():
                linksres.append({'name': key, 'url': value})

        
            result_info['website'] = website
            result_info['links'] = linksres
            # print(linksres)
    

def add_coin(coin_info, coin_yaml):
    result_info = {}
    address_url = get_address_url(coin_info['address'])
    response = get_jetton_info(address_url)
    address_friendly = get_friendly_address(address_url)
    if 'error' in address_friendly:
        print(address_friendly)
        print(coin_info['address'])
        return
    # print(coin_info)
    address_friendly = address_friendly['result']['bounceable']['b64url']
    result_info['address'] = address_friendly
    metadata = response['metadata']
    # print(metadata)
    result_info['name'] = metadata['name']
    result_info['type'] = 'TEP74'
    result_info['symbol'] = metadata['symbol']
    result_info['decimals'] = metadata['decimals']
    if 'description' in metadata:
        result_info['description'] = metadata['description']
    result_info['status'] = 'active'
    result_info['explorer'] = 'https://tonscan.org/jetton/' + address_friendly
    result_info['id'] = address_friendly
    update_links(metadata, result_info)
    thedir = 'allassets/' + address_friendly
    if not os.path.exists(thedir):
        os.makedirs(thedir)
    json.dump(result_info, open(thedir + '/info.json', 'w'), indent=4)

    image_filename = thedir + '/logo.png'
    # print(metadata['image'])
    if not os.path.exists(image_filename):
        if 'image' in metadata:
            if metadata['image'][:7] == 'ipfs://':
                metadata['image'] = 'https://ipfs.io/ipfs/' + metadata['image'][7:]
            if metadata['image'] == 'https://nft.animalsredlist.com/redc/redc.png':
                metadata['image'] = 'https://assets.dedust.io/ton/images/redx.png'
            try:
                img_data = requests.get(metadata['image']).content
                with open(image_filename, 'wb') as handler:
                    handler.write(img_data)
                print('got image', metadata['name'])
            except Exception as e:
                print(e)
                print('cant download image', metadata['image'])
                print(metadata)
                pass
        else:
            print('image not in metadata', metadata['name'])
    else:
        pass
        # print('already has image', metadata['name'])

def handle_yamls(callback):
    was = True
    for coin_yaml in os.listdir(jettons_dir):
        if was:
            with open(jettons_dir + coin_yaml, "r") as stream:
                try:
                    coin_info = (yaml.safe_load(stream))
                    if type(coin_info) == type([]):
                        for subcoin_info in coin_info:
                            callback(subcoin_info, coin_yaml)
                    else:
                        callback(coin_info, coin_yaml)

                except yaml.YAMLError as exc:
                    print(exc)

good = []
bad = []

def goodbad(coin_info, coin_yaml):
    address_url = get_address_url(coin_info['address'])
    response = get_jetton_info(address_url)
    address_friendly = get_friendly_address(address_url)
    metadata = response['metadata']
    metadata['address_friendly'] = address_friendly['result']['bounceable']['b64url']

    
    if coin_yaml in ['chesszombies_game.yaml', 'ton_chess_game.yaml', 'zeya_arena_game.yaml', 'zeya_game.yaml', 'zeya_arena_game.yaml'] \
        or coin_yaml in ['STON-fi_LPs.yaml', 'megaton-fi.yaml'] and metadata['name'] != 'Wrapped TON' \
        or 'DeDust.io JTON' in metadata['name'] and 'LP' in metadata['name']:
        bad.append(metadata)
    else:
        good.append(metadata)
    # good.append(metadata)


def first():
    handle_yamls(add_coin)
    print(link_stats)

def second():
    # if os.path.exists('assets/'):
    #     shutil.rmtree('assets/')
    # os.mkdir('assets/')
    handle_yamls(goodbad)
    print('\n\ngood tokens:\n')
    for a in good:
        if not 'name' in a or not 'description' in a or not 'symbol' in a:
            print('hueta', a)
        address = a['address_friendly']
        # shutil.copytree('allassets/' + address, 'assets/' + address)
        # print(a['address_friendly'])
        # if a['symbol'] == 'UKWN':
        #     print(a['name'])
    print('\n\nbad tokens:\n')
    for a in bad:
        # print(a)
        pass

second()
