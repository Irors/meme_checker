from excel.excel import Excel
from project import *
from data.config import *
from eth import ETHClient
from data.addLogger import logger
import itertools


def main():

    with open('data/wallets_evm.txt') as file:
        private = [row.strip() for row in file]

    with open('data/proxy.txt') as file:
        proxy = [row.strip() for row in file]
        if proxy:
            proxy = itertools.cycle(proxy)
        else:
            proxy = itertools.cycle([None])

    accounts = [ETHClient(private_key, next(proxy)) for private_key in private]
    logger.info(f'Загружено: {len(private)} аккаунтов')

    excel = Excel(meme_data)
    main_meme(accounts=accounts, excel=excel)


if __name__ == "__main__":
    main()
