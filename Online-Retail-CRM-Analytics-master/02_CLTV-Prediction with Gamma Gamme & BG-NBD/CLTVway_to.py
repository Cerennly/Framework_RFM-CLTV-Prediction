#1. Aykırı Değer (Outlier) ve Veri Baskılama Katmanı
#Mantık: CLTV modelleri olasılık dağılımları (Gamma ve Beta) üzerinden çalışır. Uç değerler, bu dağılımların "kuyruklarını" aşırı uzatarak genel kitle tahminini bozar. Burada yapılan işlem, veriyi silmek yerine belirlenen eşik değerlere (upper/lower limit) eşitlemektir.

#Python
# 1.1. Eşik Belirleme: %1 ve %99 seçilerek sadece en ekstrem değerler hedeflenir.
def outlier_thresholds(dataframe, variable):
    quartile_1 = dataframe[variable].quantile(0.01)
    quartile_3 = dataframe[variable].quantile(0.99)
    interquantile_range = quartile_3 - quartile_1
    up_limit = round(quartile_3 + 1.5 * interquantile_range)
    low_limit = round(quartile_1 - 1.5 * interquantile_range)
    return low_limit, up_limit

# 1.2. Baskılama: Veriyi silmeyip, üst limitin üzerindekileri üst limite eşitliyoruz.
def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit
#2. Metrik Dönüştürme ve Haftalık Zaman Birimi
#Mantık: Lifetimes kütüphanesi zamanı haftalık periyotlarda (/ 7) almayı tercih eder. Çünkü günlük veri çok oynaktır (hafta sonu etkisi vb.), haftalık veri ise daha stabil bir "satın alma hızı" (transaction rate) sunar.

#Recency: Müşterinin ilk ve son alışverişi arasındaki süre.

#T (Age): Müşterinin analiz tarihindeki toplam yaşı.

#Monetary: İşlem başına ortalama kâr (Gamma-Gamma için şarttır).

#Python
# Analiz tarihi olarak veri setindeki son tarihten 1-2 gün sonrası seçilir.
analysis_date = dt.datetime(2021, 6, 1)

cltv_df = pd.DataFrame()
cltv_df["customer_id"] = dataframe["master_id"]
# Haftalık birime çevrim (dt.days / 7)
cltv_df["recency_cltv_weekly"] = ((dataframe["last_order_date"] - dataframe["first_order_date"]).dt.days) / 7
cltv_df["T_weekly"] = ((analysis_date - dataframe["first_order_date"]).dt.days) / 7
cltv_df["frequency"] = dataframe["order_num_total"]
# Gamma-Gamma için ortalama değer hesaplanır
cltv_df["monetary_cltv_avg"] = dataframe["customer_value_total"] / dataframe["order_num_total"]

# Modeller en az 2 alışveriş yapan müşterilerde (frequency > 1) çalışır.
cltv_df = cltv_df[(cltv_df['frequency'] > 1)]
#3. BG/NBD: Beklenen İşlem Sayısı Katmanı
#Mantık: Bu model "Müşteri ne kadar sıklıkla gelir?" ve "Gelme ihtimali ne zaman biter?" sorularını yanıtlar.

#r ve alpha: Satın alma hızını temsil eder.

#a ve b: Churn (terk etme) olasılığını temsil eder.

#Python
# penalizer_coef: Katsayıların aşırı büyümesini (overfitting) engelleyen düzenleyici.
bgf = BetaGeoFitter(penalizer_coef=0.001)
bgf.fit(cltv_df['frequency'], cltv_df['recency_cltv_weekly'], cltv_df['T_weekly'])

# 3 ve 6 ay (12 ve 24 hafta) için adet tahmini:
cltv_df["exp_sales_3_month"] = bgf.predict(4 * 3, cltv_df['frequency'], cltv_df['recency_cltv_weekly'], cltv_df['T_weekly'])
cltv_df["exp_sales_6_month"] = bgf.predict(4 * 6, cltv_df['frequency'], cltv_df['recency_cltv_weekly'], cltv_df['T_weekly'])
#4. Gamma-Gamma: Beklenen Kârlılık Katmanı
#Mantık: Müşterinin işlem başına bırakacağı parayı tahmin eder. "Monetary" değerinin kendi içindeki varyansına bakarak, gelecekteki harcama ortalamasını belirler.

#Python
ggf = GammaGammaFitter(penalizer_coef=0.01)
ggf.fit(cltv_df['frequency'], cltv_df['monetary_cltv_avg'])

# Müşteri bazlı beklenen ortalama kâr:
cltv_df["exp_average_value"] = ggf.conditional_expected_average_profit(cltv_df['frequency'], cltv_df['monetary_cltv_avg'])
#5. CLTV ve Stratejik Segmentasyon Katmanı
#Mantık: Son aşamada iki modelin çıktıları (Adet x Birim Kâr) çarpılır. discount_rate ile paranın zaman maliyeti eklenir. qcut ile müşteriler değerlerine göre 4 gruba ayrılır.

#Python
# 6 aylık CLTV hesaplama
cltv_df["cltv"] = ggf.customer_lifetime_value(bgf,
                                             cltv_df['frequency'],
                                             cltv_df['recency_cltv_weekly'],
                                             cltv_df['T_weekly'],
                                             cltv_df['monetary_cltv_avg'],
                                             time=6, # 6 aylık projeksiyon
                                             freq="W",
                                             discount_rate=0.01) # %1 indirgeme

# Müşterileri A, B, C, D olarak 4 eşit dilime bölme
cltv_df["cltv_segment"] = pd.qcut(cltv_df["cltv"], 4, labels=["D", "C", "B", "A"])
#Bu Framework FLO'ya Ne Sağlar?
#A Segmenti (Yıldızlar): Sadakat programları ve kişiye özel asistanlık hizmetleri için hedef kitle.

#D Segmenti (Riskli/Düşük Değer): Maliyeti düşük (e-posta/push) iletişimler veya "yeniden kazanma" (win-back) kampanyaları.
#B ve C Segmentleri: Orta vadeli kampanyalar, çapraz satış (cross-sell) fırsatları.
