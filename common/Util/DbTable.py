from CoreBase import Env
stock_data_db = 'stock_data.db'

stock_table_name = 'STOCK_KDATA'
stock_index = 'CODEID'
stock_kdata_table = '''CREATE TABLE STOCK_KDATA
      (CODEID   CHAR(64)       NOT NULL,
       K_TYPE   CHAR(16)          NOT NULL,     
       TIME     CHAR(64)     NOT NULL,
       OPEN     FLOAT     NOT NULL,
       CLOSE     FLOAT     NOT NULL,
       HIGH     FLOAT     NOT NULL,
       LOW     FLOAT     NOT NULL,
       PERATIO     FLOAT     ,
       TURNOVERRATE     FLOAT    ,
       VOLUME     FLOAT     ,
       TURNOVER     FLOAT     ,
       CHANGERATE     FLOAT     ,
       LASTCLOSE     FLOAT    ,
       PRIMARY KEY(CODEID, TIME));'''

stock_data_columns = ['code', 'k_type', 'time_key', 'open', 'close', 'high', 'low', 'pe_ratio', 'turnover_rate', 'volume',  'turnover', 'change_rate', 'last_code']



######################################################################################################################
######################################################################################################################


plate_stockname_table_name = 'PLATE_STOCKNAME'
plate_stockname_index = 'CODEID'
plate_stockname_table= '''CREATE TABLE PLATE_STOCKNAME
      (CODEID   CHAR(64)       NOT NULL,
       LOT_SIZE   INT      ,     
       STOCK_NAME     CHAR(64)     NOT NULL,
       STOCK_TYPE     CHAR(64)     NOT NULL     ,
       LIST_TIME     CHAR(64)     NOT NULL,
       STOCK_ID     CHAR(64)     NOT NULL     ,
       MAIN_CONTRACT     BOOL,
       LAST_TRADE_TIME     CHAR(64) ,
       PLATE_NAME     CHAR(64)     NOT NULL,
       PLATE_ID     CHAR(64)     NOT NULL,
       MARKET_TYPE     CHAR(64)     NOT NULL,
       PRIMARY KEY(CODEID, PLATE_ID));'''

plate_stockname_table_columns = 'CODEID, LOT_SIZE, STOCK_NAME, STOCK_TYPE, LIST_TIME, STOCK_ID, MAIN_CONTRACT, LAST_TRADE_TIME, PLATE_NAME, PLATE_ID, MARKET_TYPE '
plate_stockname_columns = ['code', 'lot_size', 'stock_name', 'stock_type', 'list_time', 'stock_id', 'main_contract', 'last_trade_time', 'plate_name', 'plate_id', 'market_type']

######################################################################################################################
######################################################################################################################

usa_stock_table_name = 'USA_STOCK_KDATA'
usa_stock_index = 'CODEID'
usa_stock_kdata_table = '''CREATE TABLE USA_STOCK_KDATA
      (CODEID   CHAR(64)       NOT NULL,
       K_TYPE   CHAR(16)          NOT NULL,     
       TIME     CHAR(64)     NOT NULL,
       OPEN     FLOAT     NOT NULL,
       CLOSE     FLOAT     NOT NULL,
       HIGH     FLOAT     NOT NULL,
       LOW     FLOAT     NOT NULL,
       VOLUME     FLOAT     ,
       PRIMARY KEY(CODEID, TIME));'''

usa_stock_data_columns = ['code', 'k_type', 'time_key', 'open', 'close', 'high', 'low', 'volume']


######################################################################################################################
######################################################################################################################




usa_stock_financials_table_name = 'USA_STOCK_FINANCIALS'
usa_stock_financials_index = 'ticker'
usa_stock_financials_table = '''CREATE TABLE USA_STOCK_FINANCIALS
(ticker   CHAR(64)       NOT NULL,
period    CHAR ,
calendarDate    CHAR ,
reportPeriod    CHAR ,
updated    CHAR ,
dateKey    CHAR ,
accumulatedOtherComprehensiveIncome    CHAR ,
assets    CHAR ,
assetsAverage    CHAR ,
assetsCurrent    CHAR ,
assetsNonCurrent    CHAR ,
assetTurnover    CHAR ,
bookValuePerShare    CHAR ,
capitalExpenditure    CHAR ,
cashAndEquivalents    CHAR ,
cashAndEquivalentsUSD    CHAR ,
costOfRevenue    CHAR ,
consolidatedIncome    CHAR ,
currentRatio    CHAR ,
debtToEquityRatio    CHAR ,
debt    CHAR ,
debtCurrent    CHAR ,
debtNonCurrent    CHAR ,
debtUSD    CHAR ,
deferredRevenue    CHAR ,
depreciationAmortizationAndAccretion    CHAR ,
deposits    CHAR ,
dividendYield    CHAR ,
dividendsPerBasicCommonShare    CHAR ,
earningBeforeInterestTaxes    CHAR ,
earningsBeforeInterestTaxesDepreciationAmortization    CHAR ,
EBITDAMargin    CHAR ,
earningsBeforeInterestTaxesDepreciationAmortizationUSD    CHAR ,
earningBeforeInterestTaxesUSD    CHAR ,
earningsBeforeTax    CHAR ,
earningsPerBasicShare    CHAR ,
earningsPerDilutedShare    CHAR ,
earningsPerBasicShareUSD    CHAR ,
shareholdersEquity    CHAR ,
averageEquity    CHAR ,
shareholdersEquityUSD    CHAR ,
enterpriseValue    CHAR ,
enterpriseValueOverEBIT    CHAR ,
enterpriseValueOverEBITDA    CHAR ,
freeCashFlow    CHAR ,
freeCashFlowPerShare    CHAR ,
foreignCurrencyUSDExchangeRate    CHAR ,
grossProfit    CHAR ,
grossMargin    CHAR ,
goodwillAndIntangibleAssets    CHAR ,
interestExpense    CHAR ,
investedCapital    CHAR ,
investedCapitalAverage    CHAR ,
inventory    CHAR ,
investments    CHAR ,
investmentsCurrent    CHAR ,
investmentsNonCurrent    CHAR ,
totalLiabilities    CHAR ,
currentLiabilities    CHAR ,
liabilitiesNonCurrent    CHAR ,
marketCapitalization    CHAR ,
netCashFlow    CHAR ,
netCashFlowBusinessAcquisitionsDisposals    CHAR ,
issuanceEquityShares    CHAR ,
issuanceDebtSecurities    CHAR ,
paymentDividendsOtherCashDistributions    CHAR ,
netCashFlowFromFinancing    CHAR ,
netCashFlowFromInvesting    CHAR ,
netCashFlowInvestmentAcquisitionsDisposals    CHAR ,
netCashFlowFromOperations    CHAR ,
effectOfExchangeRateChangesOnCash    CHAR ,
netIncome    CHAR ,
netIncomeCommonStock    CHAR ,
netIncomeCommonStockUSD    CHAR ,
netLossIncomeFromDiscontinuedOperations    CHAR ,
netIncomeToNonControllingInterests    CHAR ,
profitMargin    CHAR ,
operatingExpenses    CHAR ,
operatingIncome    CHAR ,
tradeAndNonTradePayables    CHAR ,
payoutRatio    CHAR ,
priceToBookValue    CHAR ,
priceEarnings    CHAR ,
priceToEarningsRatio    CHAR ,
propertyPlantEquipmentNet    CHAR ,
preferredDividendsIncomeStatementImpact    CHAR ,
sharePriceAdjustedClose    CHAR ,
priceSales    CHAR ,
priceToSalesRatio    CHAR ,
tradeAndNonTradeReceivables    CHAR ,
accumulatedRetainedEarningsDeficit    CHAR ,
revenues    CHAR ,
revenuesUSD    CHAR ,
researchAndDevelopmentExpense    CHAR ,
returnOnAverageAssets    CHAR ,
returnOnAverageEquity    CHAR ,
returnOnInvestedCapital    CHAR ,
returnOnSales    CHAR ,
shareBasedCompensation    CHAR ,
sellingGeneralAndAdministrativeExpense    CHAR ,
shareFactor    CHAR ,
shares    CHAR ,
weightedAverageShares    CHAR ,
weightedAverageSharesDiluted    CHAR ,
salesPerShare    CHAR ,
tangibleAssetValue    CHAR ,
taxAssets    CHAR ,
incomeTaxExpense    CHAR ,
taxLiabilities    CHAR ,
tangibleAssetsBookValuePerShare    CHAR ,
workingCapital    CHAR ,
PRIMARY KEY(ticker, updated));'''



######################################################################################################################
######################################################################################################################

cn_stock_table_name = 'CN_STOCK_KDATA'
cn_stock_index = 'CODEID'
cn_stock_kdata_table = '''CREATE TABLE CN_STOCK_KDATA
      (CODEID   CHAR(64)       NOT NULL,
       K_TYPE   CHAR(16)          NOT NULL,     
       TIME     CHAR(64)     NOT NULL,
       OPEN     FLOAT     NOT NULL,
       CLOSE     FLOAT     NOT NULL,
       HIGH     FLOAT     NOT NULL,
       LOW     FLOAT     NOT NULL,
       VOLUME     FLOAT     ,
       AMOUNT     FLOAT     ,
       ADJUSTFLAG     FLOAT     ,
       TURN     CHAR(64)     ,
       TRADESTATUS     FLOAT     ,
       PCTCHG     FLOAT     ,
       PETTM     FLOAT     ,
       PBMRQ     FLOAT     ,
       PSTTM     FLOAT     ,
       PCFNCFTTM     FLOAT     ,
       ISST     FLOAT     ,
       PRIMARY KEY(CODEID, TIME));'''

cn_stock_data_columns = ['code', 'k_type', 'time_key', 'open', 'high', 'low', 'close', 'volume', 'amount','adjustflag','turn','tradestatus','pctChg','peTTM','pbMRQ','psTTM','pcfNcfTTM','isST']


######################################################################################################################
######################################################################################################################

cn_stock_financials_table_name = 'CN_STOCK_FINANCIALS'
cn_stock_financials_index = 'CODEID'
cn_stock_financials_table = '''CREATE TABLE CN_STOCK_FINANCIALS
(CODEID   CHAR(64)       NOT NULL,
performanceExpPubDate    CHAR ,
performanceExpStatDate    CHAR ,
performanceExpUpdateDate    CHAR ,
performanceExpressTotalAsset    CHAR ,
performanceExpressNetAsset    CHAR ,
performanceExpressEPSChgPct    CHAR ,
performanceExpressROEWa    CHAR ,
performanceExpressEPSDiluted    CHAR ,
performanceExpressGRYOY    CHAR ,
performanceExpressOPYOY    CHAR ,
PRIMARY KEY(CODEID, performanceExpPubDate));'''


######################################################################################################################
######################################################################################################################

cn_stock_plat_table_name = 'CN_STOCK_PLATINFO'
cn_stock_plat_index = 'CODEID'
cn_stock_plat_table = '''CREATE TABLE CN_STOCK_PLATINFO
(CODEID   CHAR(64)       NOT NULL,
updateDate    CHAR ,
code_name    CHAR ,
industry    CHAR ,
industryClassification    CHAR ,
PRIMARY KEY(CODEID, updateDate));'''


######################################################################################################################
######################################################################################################################

select_table_name = usa_stock_table_name
select_stock_data_columns = usa_stock_data_columns

