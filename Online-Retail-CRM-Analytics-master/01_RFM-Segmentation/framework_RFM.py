#1. RFM Motoru
#Bu framework, ham işlem verilerini (transactional data) stratejik iş kararlarına dönüştürür.
## Aşama 1: Veri Ön İşleme (Data Cleaning)
#Kodundaki prepare_data metodu, analizin "hijyen" aşamasıdır.
#Python
self.dataframe["TotalPrice"] = self.dataframe["Quantity"] * self.dataframe["Price"]
self.dataframe.dropna(inplace=True)
self.dataframe = self.dataframe[~self.dataframe["Invoice"].str.contains("C", na=False)]
#•	Neden? Gürültülü veri, yanlış segmentasyon demektir.
#•	Uzman Yaklaşımı: * TotalPrice: Parasal değeri (Monetary) ölçmek için birim fiyat değil, toplam ciro gereklidir.
#o	C (Cancelled): İptal edilen işlemler bir "davranış" değil, "hata/vazgeçiştir". Eğer bunları silmezsen, alışveriş yapmayan bir müşteriyi "çok sık alışveriş yapıyor" gibi görebilirsin (Frequency yanılgısı).
________________________________________
## Aşama 2: Metriklerin Hesaplanması (Recency, Frequency, Monetary)
#calculate_rfm metodundaki groupby ve agg işlemleri, CRM analitiğinin kalbidir.
#Python
rfm = self.dataframe.groupby('Customer ID').agg({
    'InvoiceDate': lambda date: (today_date - date.max()).days, # Recency
    'Invoice': lambda num: num.nunique(),                       # Frequency
    'TotalPrice': lambda price: price.sum()                    # Monetary
})
#•	Recency (Yenilik): Müşterinin sıcaklığını ölçer. Matematiği: $Bugün - Son Alışveriş Tarihi$.
#o	Uzman Notu: R değeri ne kadar düşükse, müşteri markaya o kadar bağlıdır.
#•	Frequency (Sıklık): Müşterinin alışkanlık düzeyini ölçer. nunique() kullanman çok kritiktir; çünkü aynı gün içinde alınan 5 farklı ürün 5 alışveriş değil, 1 işlem (fatura) sayılmalıdır.
#•	Monetary (Parasal Değer): Müşterinin şirkete bıraktığı toplam yaşam boyu değerdir (LTV başlangıcı).
________________________________________
## Aşama 3: Skorlama ve qcut Mantığı
#İşte uzmanlığın konuşturulduğu yer burası. Veriyi 1'den 5'e kadar puanlıyorsun.
#Python
rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
#•	Neden qcut? Veriyi eşit büyüklükte 5 gruba (quintile) böler. Eğer bir müşteri en üst %20'lik dilimdeyse 5 puan alır. Bu, görece (relative) bir başarı ölçüsüdür.
#•	Recency Ters Orantı: Recency'de gün sayısı azaldıkça (yakın tarih) puan artar ([5, 4, 3, 2, 1]). Çünkü 1 gün önce gelen, 100 gün önce gelenden daha değerlidir.
#•	Rank Method: Eğer çok fazla müşteri aynı sayıda alışveriş yaptıysa (örneğin herkes 1 kez), qcut hata verebilir. rank(method="first") kullanarak bu çakışmaları çözüp her müşteriye adil bir skor atıyorsun.
________________________________________
## Aşama 4: Segmentasyon ve Stratejik Harita (seg_map)
#Kodun son kısmındaki seg_map, matematiksel skorları "insan diline" çevirir.
#Python
rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
#•	Champions (55): Senin en iyi müşterilerin. Onlara indirim değil, "ayrıcalık" ver (Early access, VIP etkinlik).
#•	Hibernating (11-22): "Kış uykusundakiler". Hem nadir geliyorlar hem de çok uzun süredir gelmediler. Onları geri kazanmak için büyük maliyetlere katlanmak yerine, "otomatik hatırlatma" maili atmak daha mantıklıdır.
#•	At Risk (14-24): Eskiden çok sık gelen ama son zamanlarda seni unutanlar. Bunlar rakiplerine kaçıyor olabilir! Acil müdahale gerekir.
________________________________________
## Özet: Neden Bu Framework?
#Bu kod yapısı sayesinde veri seti (ayakkabı, yazılım aboneliği, restoran verisi) ne olursa olsun şu 3 soruya cevap verirsin:
#1.	Kim benim en değerli müşterim?
#2.	Kimi kaybetmek üzereyim?
#3.	Kime hangi kampanya yapılmalı?

