from Indicator import SimpleSellIndicator

class SellIndicatorFactory(object):
    
    @staticmethod
    def AddMacdSellIndicator(**kwargs):
        short_arg = 12
        long_arg = 26
        if 'short_arg' in kwargs:
            short = kwargs['short_arg']
        if 'long_arg' in kwargs:
            long_arg = kwargs['long_arg']
        regressang_kwargs = {
                            'short_arg': short_arg,
                            'long_arg': long_arg,
                            }
        return SimpleSellIndicator.MacdSellIndicator(regressang_kwargs)
        