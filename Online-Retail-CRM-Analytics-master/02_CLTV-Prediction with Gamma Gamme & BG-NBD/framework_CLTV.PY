#Bu framework, olasılıksal bir modelleme bütünüdür. Yani "bu müşteri kesin gelir" demez, "bu müşterinin mevcut alışkanlıklarına göre gelme olasılığı şudur" der.
#1. Veri Ön İşleme: Neden %1 ve %99?
#Kodunda quartile_1 = 0.01 ve quartile_3 = 0.99 kullanarak çok dar bir aralıkta tıraşlama yapıyorsun.
#•	Detay: Standart RFM analizlerinde genellikle %25-%75 (IQR) kullanılır. Ancak CLTV modellerinde (BG/NBD gibi) verinin varyansı çok değerlidir. Eğer çok fazla veriyi silerseniz, sadık ve yüksek harcama yapan müşterileri "normalleştirmiş" olursunuz.
#•	Kodun Mesajı: "%1'lik dilimdeki aşırı uçları ( outliers) törpüle ama müşterinin özgün harcama karakterini (geniş dağılımını) koru."
________________________________________
#2. BG/NBD: "Alive" (Canlılık) Kavramı
##Kodundaki en kritik kısım bgf.fit satırıdır. Bu model iki süreci aynı anda yönetir:
#•	Transaction Process (Satın Alma Süreci): Bir müşteri "aktif" olduğu sürece, kendi içinde bir satın alma hızı (lambda) vardır. Bu hız müşteriden müşteriye değişir.
#•	Dropout Process (Terk Etme Süreci): Her satın almadan sonra, müşterinin bizi terk etme (churn olma) ihtimali vardır.
#•	Kodun Mantığı: recency_cltv_weekly ve T_weekly arasındaki fark burada devreye girer.
#o	Eğer bir müşterinin Recency değeri (son alışveriş - ilk alışveriş) T değerine (toplam yaşı) çok yakınsa, model der ki: "Bu müşteri hala aktif, çünkü son zamanlarda da işlem yapmış."
#o	Eğer aradaki fark açılmışsa, model müşterinin "öldüğünü" (churn olduğunu) varsayar ve exp_sales değerini düşürür.
________________________________________
#3. Gamma-Gamma: "Monetary" Neden Ortalama Alınır?
#Kodunda şu satırı yazdın: cltv_df["monetary_cltv_avg"] = df["omnichannel_value"] / df["omnichannel_order"].
#•	Neden Toplam Değer Değil?: Gamma-Gamma modeli, bir müşterinin yaptığı işlemlerin değerinin, o müşterinin "ortalama işlem değeri" etrafında rastgele dağıldığını varsayar.
#•	Detay: Model, müşterinin geçmişteki harcama ortalamasını alır ve bunu popülasyonun ortalamasıyla harmanlayarak bir "beklenen ortalama" (Expected Average Profit) üretir.
#•	Kodun Mesajı: "Bu müşteri her geldiğinde bana ortalama ne kadar kazandıracak?" sorusuna yanıt arar.
________________________________________
#4. Zaman Birimleri: Neden Haftalık (/ 7)?
#Kodunda tüm tarih farklarını 7'ye bölerek haftalık birime çevirdin.
#•	Detay: lifetimes kütüphanesi ve bu modeller (BG/NBD), parametrelerini (r, alpha, a, b) genellikle haftalık periyotlarda daha kararlı hesaplar. Günlük verideki dalgalanmalar (hafta içi/hafta sonu farkları) modeli çok gürültülü hale getirebilir. Haftalık birim, bu gürültüyü "smooth" (yumuşatma) ederek modelin genel trendi yakalamasını sağlar.
________________________________________
#5. penalizer_coef=0.001 Nedir?
#Modeli kurarken BetaGeoFitter(penalizer_coef=0.001) yazdın.
#•	Detay: Bu bir L2 Regularization (düzenleme) katsayısıdır.
#•	Neden Var?: Eğer veri setinde bazı müşteriler çok az veriyle (örneğin sadece 2 işlemle) çok büyük skorlar üretiyorsa, model bu müşterilere aşırı güvenebilir (overfitting). Penalizer, modelin parametrelerinin sonsuza gitmesini engelleyerek daha "muhafazakar" ve gerçekçi tahminler yapmasını sağlar.
________________________________________
#6. CLTV Formülasyonunun Kod Arkası
#ggf.customer_lifetime_value fonksiyonu aslında şunu yapar:
#$$CLTV = \text{Cond. Exp. Sales} \times \text{Cond. Exp. Average Profit} \times \text{Discount Factor}$$
#•	Discount Rate (İndirim Oranı): Kodunda %1 (discount_rate=0.01) olarak belirlediğin bu değer, "Gelecekteki paranın bugünkü değeri" anlamına gelir. Paranın zaman maliyetini hesaba katar.
#•	Time=6: Bu sadece 6 aylık bir projeksiyondur. Müşteri 10 yıl kalacak olsa bile biz sadece önümüzdeki 180 günlük nakit akışını tahminliyoruz.
________________________________________
#7. Segmentasyon: Neden qcut?
#cltv_df["cltv_segment"] = pd.qcut(cltv_df["cltv"], 4, labels = ["D", "C", "B", "A"])
#•	Detay: qcut, verileri değerine göre değil, yoğunluğuna göre böler. Yani her segmentte (A, B, C, D) eşit sayıda müşteri (örneğin her birinde %25, yani 5000'er kişi) olmasını sağlar.
#•	Stratejik Açık: Bu, pazarlama departmanına "Bana en iyi 5000 kişiyi ver" dediğinde direkt o listeyi sunabilmeni sağlar.

