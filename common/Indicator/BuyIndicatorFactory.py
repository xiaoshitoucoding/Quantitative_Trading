from Indicator import SimpleBuyIndicator

class BuyIndicatorFactory(object):
    # def __init__(self, kl_pd):
    #     self.kl_pd = kl_pd

    @staticmethod
    def AddVolumeRankBuyIndicator(**kwargs):
        volumeindicator_kwargs = {
                                 'xd': kwargs['xd'],
                                 'vol_rank_max': kwargs['vol_rank_max'],
                                 'vol_rank_min': kwargs['vol_rank_min']
                                 }
        return SimpleBuyIndicator.VolumeRankBuyIndicator(volumeindicator_kwargs)


    @staticmethod
    def AddIncreaseVolumeBuyIndicator(**kwargs):
        volumeindicator_kwargs = {
                                 'long_xd': kwargs['long_xd'],
                                 'short_xd': kwargs['short_xd'],
                                 'times': kwargs['times'],
                                 'price_times': kwargs['price_times'],
                                 }
        return SimpleBuyIndicator.IncreaseVolumeBuyIndicator(volumeindicator_kwargs)



    @staticmethod
    def AddRegressAngBuyIndicator(**kwargs):
        indictor_kwargs = {
                            'xd': kwargs['xd'],
                            'threshold_ang_min': kwargs['threshold_ang_min'],
                            'threshold_ang_max': kwargs['threshold_ang_max'],

                            }
        return SimpleBuyIndicator.RegressAngBuyIndicator(indictor_kwargs)

    @staticmethod
    def AddCrossMeanBuyIndicator(**kwargs):
        short_arg = 21
        long_arg = 50
        if 'short_arg' in kwargs:
            short = kwargs['short_arg']
        if 'long_arg' in kwargs:
            long_arg = kwargs['long_arg']
        indictor_kwargs = {
                            'short_arg': short_arg,
                            'long_arg': long_arg,
                            }
        return SimpleBuyIndicator.CrossMeanBuyIndicator(indictor_kwargs)

    @staticmethod
    def AddMacdBuyIndicator(**kwargs):
        short_arg = 12
        long_arg = 26
        if 'short_arg' in kwargs:
            short = kwargs['short_arg']
        if 'long_arg' in kwargs:
            long_arg = kwargs['long_arg']
        indictor_kwargs = {
                            'short_arg': short_arg,
                            'long_arg': long_arg,
                            }
        return SimpleBuyIndicator.MacdBuyIndicator(indictor_kwargs)

    @staticmethod
    def AddMacdDivergenceIndicator(**kwargs):
        xd = 5
        short_arg = 12
        long_arg = 26
        if 'xd' in kwargs:
            xd = kwargs['xd']
        if 'short_arg' in kwargs:
            short = kwargs['short_arg']
        if 'long_arg' in kwargs:
            long_arg = kwargs['long_arg']
        indictor_kwargs = {
                            'xd': xd,
                            'short_arg': short_arg,
                            'long_arg': long_arg,
                            }
        return SimpleBuyIndicator.MacdDivergenceIndicator(indictor_kwargs)

    @staticmethod
    def AddRsiBuyIndicator(**kwargs):
        indictor_kwargs = {
                            'rsi': kwargs['rsi'],
                            }
        return SimpleBuyIndicator.RsiBuyIndicator(indictor_kwargs)
        
    @staticmethod
    def AddBreakBuyIndicator(**kwargs):
        indictor_kwargs = {
                            'xd': kwargs['xd'],
                            }
        return SimpleBuyIndicator.BreakBuyIndicator(indictor_kwargs)

    @staticmethod
    def AddUpDownTrendFactor(**kwargs):
        xd = 20
        past_factor = 4
        up_deg_threshold = 3
        if 'xd' in kwargs:
            xd = kwargs['xd']
        if 'past_factor' in kwargs:
            past_factor = kwargs['past_factor']
        if 'up_deg_threshold' in kwargs:
            up_deg_threshold = kwargs['up_deg_threshold']
        indictor_kwargs = {
                            'xd': xd,
                            'past_factor': past_factor,
                            'up_deg_threshold': up_deg_threshold,
                            }
        return SimpleBuyIndicator.UpDownTrendFactor(indictor_kwargs)


    @staticmethod
    def AddDownTrendFactor(**kwargs):
        xd = 20
        up_deg_threshold = 3
        if 'xd' in kwargs:
            xd = kwargs['xd']
        if 'up_deg_threshold' in kwargs:
            up_deg_threshold = kwargs['up_deg_threshold']
        indictor_kwargs = {
                            'xd': xd,
                            'up_deg_threshold': up_deg_threshold,
                            }
        return SimpleBuyIndicator.DownTrendFactor(indictor_kwargs)


    @staticmethod
    def AddUpTrendFactor(**kwargs):
        xd = 20
        up_deg_threshold = 3
        if 'xd' in kwargs:
            xd = kwargs['xd']
        if 'up_deg_threshold' in kwargs:
            up_deg_threshold = kwargs['up_deg_threshold']
        indictor_kwargs = {
                            'xd': xd,
                            'up_deg_threshold': up_deg_threshold,
                            }
        return SimpleBuyIndicator.UpTrendFactor(indictor_kwargs)


    @staticmethod
    def AddDecrementFactor(**kwargs):
        indictor_kwargs = {
                            'xd': kwargs['xd'],
                            'decre_days': kwargs['decre_days'],
                            'vol_rank_max': kwargs['vol_rank_max'],
                            'vol_rank_min': kwargs['vol_rank_min']
                            }
        return SimpleBuyIndicator.DecrementFactor(indictor_kwargs)

    @staticmethod
    def AddDownVolumeFactor(**kwargs):
        xd = 20
        up_deg_threshold = 3
        if 'xd' in kwargs:
            xd = kwargs['xd']
        if 'up_deg_threshold' in kwargs:
            up_deg_threshold = kwargs['up_deg_threshold']
        indictor_kwargs = {
                            'xd': xd,
                            'up_deg_threshold': up_deg_threshold,
                            }
        return SimpleBuyIndicator.DownVolumeFactor(indictor_kwargs)


    @staticmethod
    def AddBollBuyFactor(**kwargs):
        indictor_kwargs = {
                            'xd': kwargs['xd'],
                            }
        return SimpleBuyIndicator.BollBuyFactor(indictor_kwargs)

    @staticmethod
    def AddVCPBuyFactor(**kwargs):
        indictor_kwargs = {
                            'xd': kwargs['xd'],
                            }
        return SimpleBuyIndicator.VCPBuyFactor(indictor_kwargs)
    
    @staticmethod
    def AddChiliPepper(**kwargs):
        indictor_kwargs = {
                            'xd': kwargs['xd'],
                            }
        return SimpleBuyIndicator.ChiliPepper(indictor_kwargs)

        