import asyncio
import aiohttp
from data.addLogger import logger
from eth import ETHClient


async def excel_write(address: str, quantity: float, excel):
    data = [address, quantity]
    excel.sheet.append(data)


async def request_send_points(account: str, excel):
    async with aiohttp.ClientSession(headers={
        'authority': 'memefarm-api.memecoin.org',
        'accept': 'application/json',
        'accept-language': 'ru',
        'authorization': 'Bearer ' + account.accessToken,
        'origin': 'https://www.memecoin.org',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/119.0.0.0 Safari/537.36'}) as session:
        response = await session.get('https://memefarm-api.memecoin.org/user/tasks', proxy='http://' + str(account.proxy))
        result = await response.json(content_type=None)
        await excel_write(address=account.address, quantity=result['points']['current'], excel=excel)


async def request_send_access(account: str, json_data: dict, excel):
    async with aiohttp.ClientSession(headers={'origin': 'https://www.memecoin.org',
                                              'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}) as session:

        response = await session.post('https://memefarm-api.memecoin.org/user/wallet-auth', json=json_data,
                                      proxy='http://' + str(account.proxy))
        result = await response.json(content_type=None)

        if 'unauthorized' in str(result):
            account.accessToken = 0
        else:
            account.accessToken = result['accessToken']
            await request_send_points(account=account, excel=excel)


async def make_param(address):
    param = {
        'address': address.lower(),
    }
    return param


async def make_json(account):
    json_data = {
        'address': account.address,
        'delegate': account.address,
        'message': account.message,
        'signature': account.signature
    }
    return json_data


async def make_request(accounts: list, excel):
    tasks = [
        request_send_access(account,
                            await make_json(account),
                            excel)
        for account in accounts]

    await asyncio.gather(*tasks)


def main_meme(accounts: list[ETHClient], excel):
    logger.info(f'Начинаю собирать информацию о поинтах...')
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(make_request(accounts, excel))

    logger.info(r'Результат сохранился в result\result_meme.xlsx')
    excel.workbook.save('result/result_meme.xlsx')
