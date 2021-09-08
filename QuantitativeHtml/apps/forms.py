from django import forms


class VolumesForm(forms.Form):
    total_asset = forms.CharField(label="公司市值(亿)", initial='100', max_length=128)
    short_xd = forms.CharField(label="短期平均成交量天数(天)", initial='5', max_length=128)
    long_xd = forms.CharField(label="长期平均成交量天数(天)", initial='60', max_length=128)
    times = forms.CharField(label="短期平均成交量是长期的倍数", initial='5', max_length=128)
    price_times = forms.CharField(label="短期平均价格是长期的倍数", initial='1.0', max_length=128)


class BreakAndVolume(forms.Form):
    total_asset = forms.CharField(label="公司市值(亿)", max_length=128)
    xd = forms.CharField(label="价格突破周期(天)", max_length=128)
    volume_rank_min = forms.CharField(label="突破当天成交量的排名最小值(排名范围:-1 ~ 1. 将突破周期内的成交量进行排序)", max_length=128)
    # volume_rank_max = forms.CharField(label="突破当天成交量的排名最大值(排名范围:-1 ~ 1. 将突破周期内的成交量进行排序)", max_length=128)

class StockShapeForm(forms.Form):
    total_asset = forms.CharField(label="公司市值(亿)", max_length=128)
    xd = forms.CharField(label=">周期(天)", max_length=128)
    # volume_rank_max = forms.CharField(label="突破当天成交量的排名最大值(排名范围:-1 ~ 1. 将突破周期内的成交量进行排序)", max_length=128)

class IndustryInfoForm(forms.Form):
    xd = forms.CharField(label=">周期(天)", max_length=128)

class ChilliPepperForm(forms.Form):
    total_asset = forms.CharField(label="公司市值(亿)", initial='50', max_length=128)
    xd = forms.CharField(label="下跌周期(天)", initial='60', max_length=128)
    up_deg_threshold = forms.CharField(label="下跌角度", initial='10', max_length=128)