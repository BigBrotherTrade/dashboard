from djchoices import DjangoChoices, C


class MarketType(DjangoChoices):
    STOCK = C(label='股票')
    FUTURE = C(label='期货')
    OPTION = C(label='期权')


class AddressType(DjangoChoices):
    TRADE = C(label='交易')
    MARKET = C(label='行情')


class OperatorType(DjangoChoices):
    TELECOM = C(label='电信')
    UNICOM = C(label='联通')
