import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

np.random.seed(42)

print("✅ Kütüphaneler yüklendi.")
# %%


def parametre_ureti(N, params):
    beceri = np.random.normal(params['beceri_mu'], params['beceri_sigma'], N)
    internet = np.random.exponential(params['internet_lambda'], N)
    sosyal = np.random.beta(params['sosyal_alfa'], params['sosyal_beta'], N) * 100
    zaman = np.random.gamma(params['zaman_k'], params['zaman_theta'], N)
    rekabet = np.random.uniform(params['rekabet_min'], params['rekabet_max'], N)
    yorgunluk = np.random.normal(params['yorgunluk_mu'], params['yorgunluk_sigma'], N)
    
    return {
        'beceri': np.clip(beceri, 0, 100),
        'internet': np.clip(internet, 0, 100),
        'sosyal': np.clip(sosyal, 0, 100),
        'zaman': np.clip(zaman, 30, 240),
        'rekabet': np.clip(rekabet, 0, 100),
        'yorgunluk': np.clip(yorgunluk, 0, 100)
    }

print("✅ parametre_ureti() hazır.")
# %%


def tercih_hesapla_v2(parametreler):
    N = len(parametreler['beceri'])
    
    b = parametreler['beceri'] / 100
    i = parametreler['internet'] / 100
    s = parametreler['sosyal'] / 100
    z = np.clip(parametreler['zaman'] / 120, 0, 1)
    r = parametreler['rekabet'] / 100
    y = parametreler['yorgunluk'] / 100
    
    mp_egilim = 50
    mp_egilim += i * 20
    mp_egilim += s * 25
    mp_egilim += r * 20
    mp_egilim -= y * 20
    mp_egilim -= z * 15
    mp_egilim += (b - 0.5) * 10
    
    mp_egilim = np.clip(mp_egilim, 5, 95)
    
    mp_skor = mp_egilim / 100
    sp_skor = (100 - mp_egilim) / 100
    
    sicaklik = 0.3
    p_mp = np.exp(mp_skor / sicaklik) / (np.exp(mp_skor / sicaklik) + np.exp(sp_skor / sicaklik))
    
    tercihler = np.random.random(N) < p_mp
    
    return {
        'mp_skor': mp_skor,
        'sp_skor': sp_skor,
        'mp_egilim': mp_egilim,
        'p_mp': p_mp,
        'tercih_mp': tercihler,
        'tercih': np.where(tercihler, 'MP', 'SP')
    }

print("✅ tercih_hesapla_v2() hazır.")
# %%

def senaryo_calistir_v2(N, params, senaryo_adi):
    p = parametre_ureti(N, params)
    t = tercih_hesapla_v2(p)
    
    mp_orani = np.mean(t['tercih_mp']) * 100
    sp_orani = 100 - mp_orani
    kararsiz = np.mean((t['p_mp'] > 0.35) & (t['p_mp'] < 0.65)) * 100
    
    mp_mask = t['tercih_mp']
    sp_mask = ~mp_mask
    
    print(f"\n{'='*55}")
    print(f"📊 {senaryo_adi}")
    print(f"{'='*55}")
    print(f"  🎮 MP: %{mp_orani:.1f}  |  🏠 SP: %{sp_orani:.1f}  |  🤔 Kararsız: %{kararsiz:.1f}")
    print(f"  Ort. MP Eğilim: {np.mean(t['mp_egilim']):.1f}/100")
    print(f"  {'─'*45}")
    print(f"  {'Parametre':<20} {'MP Seçen':<12} {'SP Seçen':<12} {'Fark'}")
    print(f"  {'─'*45}")
    
    for ad, key in [('Sosyal İstek', 'sosyal'), ('Rekabetçilik', 'rekabet'), 
                     ('İnternet Kal.', 'internet'), ('Yorgunluk', 'yorgunluk'),
                     ('Beceri', 'beceri'), ('Zaman (dk)', 'zaman')]:
        mp_ort = p[key][mp_mask].mean()
        sp_ort = p[key][sp_mask].mean()
        print(f"  {ad:<20} {mp_ort:<12.1f} {sp_ort:<12.1f} {mp_ort-sp_ort:+.1f}")
    
    return {
        'senaryo': senaryo_adi,
        'mp_orani': mp_orani,
        'sp_orani': sp_orani,
        'kararsiz_orani': kararsiz,
        'ort_mp_egilim': np.mean(t['mp_egilim']),
        'parametreler': p,
        'tercihler': t,
        'params_dict': params
    }

print("✅ senaryo_calistir_v2() hazır.")
# %%

senaryolar = {
    'Senaryo 1 - Mevcut Durum': {
        'beceri_mu': 50, 'beceri_sigma': 15,
        'internet_lambda': 20,
        'sosyal_alfa': 2, 'sosyal_beta': 5,
        'zaman_k': 2, 'zaman_theta': 40,
        'rekabet_min': 0, 'rekabet_max': 100,
        'yorgunluk_mu': 40, 'yorgunluk_sigma': 20
    },
    'Senaryo 2 - Pandemi': {
        'beceri_mu': 50, 'beceri_sigma': 15,
        'internet_lambda': 33,
        'sosyal_alfa': 5, 'sosyal_beta': 2,
        'zaman_k': 4, 'zaman_theta': 50,
        'rekabet_min': 0, 'rekabet_max': 100,
        'yorgunluk_mu': 30, 'yorgunluk_sigma': 15
    },
    'Senaryo 3 - Turnuva': {
        'beceri_mu': 70, 'beceri_sigma': 10,
        'internet_lambda': 15,
        'sosyal_alfa': 3, 'sosyal_beta': 3,
        'zaman_k': 3, 'zaman_theta': 60,
        'rekabet_min': 70, 'rekabet_max': 100,
        'yorgunluk_mu': 20, 'yorgunluk_sigma': 10
    }
}

print("✅ 3 senaryo tanımlandı.")
# %%

N = 10000
sonuclar = []

print("🚀 SİMÜLASYON BAŞLIYOR...")
print(f"Oyuncu Sayısı: {N}")

for senaryo_adi, params in senaryolar.items():
    sonuc = senaryo_calistir_v2(N, params, senaryo_adi)
    sonuclar.append(sonuc)

print(f"\n✅ Simülasyon tamamlandı!")
# %%

print(f"\n{'='*70}")
print("📊 FİNAL - SENARYO KARŞILAŞTIRMA")
print(f"{'='*70}")
print(f"{'Senaryo':<28} {'MP %':<8} {'SP %':<8} {'Kararsız %':<10} {'MP Eğilim'}")
print(f"{'─'*70}")

for s in sonuclar:
    kisa = s['senaryo'].replace('Senaryo 1 - ', 'S1: ').replace('Senaryo 2 - ', 'S2: ').replace('Senaryo 3 - ', 'S3: ')
    print(f"{kisa:<28} %{s['mp_orani']:<7.1f} %{s['sp_orani']:<7.1f} %{s['kararsiz_orani']:<9.1f} {s['ort_mp_egilim']:.1f}/100")

print(f"{'='*70}")

# %%

fig, ax = plt.subplots(figsize=(10, 6))
senaryo_adlari = [s['senaryo'].split(' - ')[1] for s in sonuclar]
mp_oranlar = [s['mp_orani'] for s in sonuclar]
sp_oranlar = [s['sp_orani'] for s in sonuclar]
x = np.arange(3)
ax.bar(x - 0.15, mp_oranlar, 0.3, label='Çok Oyunculu (MP)', color='#FF6B6B', edgecolor='white')
ax.bar(x + 0.15, sp_oranlar, 0.3, label='Tek Oyunculu (SP)', color='#4ECDC4', edgecolor='white')
ax.set_xticks(x)
ax.set_xticklabels(senaryo_adlari, fontsize=11)
ax.set_ylabel('Tercih Oranı (%)')
ax.set_title('Senaryolara Göre Oyun Modu Tercihi', fontweight='bold')
ax.legend()
ax.set_ylim(0, 100)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(r'C:\Users\Aya Karakoyun\Desktop\st\01_tercih_oranlari.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()

# %%

fig, axes = plt.subplots(1, 3, figsize=(16, 6))
for i, sonuc in enumerate(sonuclar):
    egilim = sonuc['tercihler']['mp_egilim']
    senaryo_kisa = sonuc['senaryo'].split(' - ')[1]
    axes[i].hist(egilim, bins=40, color='#FF6B6B', edgecolor='white', alpha=0.7, density=True)
    axes[i].axvline(50, color='black', linestyle='--', linewidth=2, label='Nötr (50)')
    axes[i].axvline(np.mean(egilim), color='blue', linestyle='-', linewidth=2, label=f'Ort: {np.mean(egilim):.1f}')
    axes[i].set_title(senaryo_kisa, fontweight='bold')
    axes[i].set_xlabel('MP Eğilim Skoru')
    axes[i].set_ylabel('Yoğunluk')
    axes[i].legend(fontsize=9)
    axes[i].set_xlim(0, 100)
plt.suptitle('MP Eğilim Skoru Dağılımı', fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(r'C:\Users\Aya Karakoyun\Desktop\st\02_mp_egilim.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()

# %%

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
axes = axes.flatten()
s1 = sonuclar[0]
p = s1['parametreler']
t = s1['tercihler']['tercih']
parametreler = ['sosyal', 'rekabet', 'internet', 'yorgunluk', 'beceri', 'zaman']
basliklar = ['Sosyal İstek', 'Rekabetçilik', 'İnternet Kalitesi', 'Yorgunluk', 'Beceri', 'Zaman (dk)']
for i, (key, title) in enumerate(zip(parametreler, basliklar)):
    mp_data = p[key][t == 'MP']
    sp_data = p[key][t == 'SP']
    bp = axes[i].boxplot([mp_data, sp_data], labels=['MP', 'SP'], patch_artist=True, widths=0.5)
    bp['boxes'][0].set_facecolor('#FF6B6B')
    bp['boxes'][1].set_facecolor('#4ECDC4')
    axes[i].set_title(title, fontweight='bold')
    axes[i].grid(axis='y', alpha=0.3)
plt.suptitle('Mevcut Durum - MP vs SP Parametre Karşılaştırması', fontweight='bold')
plt.tight_layout()
plt.savefig(r'C:\Users\Aya Karakoyun\Desktop\st\03_boxplot.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()

# %%

kategoriler = ['MP Oranı', 'MP Eğilim', 'Sosyal(MP)', 'Rekabet(MP)', 'İnternet(MP)', 'Yorgunluk(SP)']
N_k = len(kategoriler)
degerler = []
for s in sonuclar:
    p = s['parametreler']; t = s['tercihler']['tercih_mp']
    degerler.append([s['mp_orani'], s['ort_mp_egilim'], p['sosyal'][t].mean(), 
                     p['rekabet'][t].mean(), p['internet'][t].mean(), p['yorgunluk'][~t].mean()])
degerler = np.array(degerler)
degerler_norm = degerler / degerler.max(axis=0) * 100
acilar = np.linspace(0, 2*np.pi, N_k, endpoint=False).tolist() + [0]
fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
renkler = ['#FF6B6B', '#4ECDC4', '#FFD93D']
for i, (d, renk) in enumerate(zip(degerler_norm, renkler)):
    values = d.tolist() + [d[0]]
    ax.fill(acilar, values, alpha=0.15, color=renk)
    ax.plot(acilar, values, 'o-', linewidth=2, label=sonuclar[i]['senaryo'].split(' - ')[1], color=renk, markersize=8)
ax.set_xticks(acilar[:-1])
ax.set_xticklabels(kategoriler, fontsize=9)
ax.set_ylim(0, 100)
ax.set_title('Senaryo Karşılaştırması - Örümcek Ağı', fontweight='bold')
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
plt.tight_layout()
plt.savefig(r'C:\Users\Aya Karakoyun\Desktop\st\04_radar.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()

# %%

s3 = sonuclar[2]
p = s3['parametreler']; t = s3['tercihler']
df_kor = pd.DataFrame({
    'Beceri': p['beceri'], 'İnternet': p['internet'], 'Sosyal': p['sosyal'],
    'Zaman': p['zaman'], 'Rekabet': p['rekabet'], 'Yorgunluk': p['yorgunluk'],
    'MP Eğilim': t['mp_egilim'], 'MP Olasılık': t['p_mp']
})
plt.figure(figsize=(10, 8))
mask = np.triu(np.ones_like(df_kor.corr()), k=1)
sns.heatmap(df_kor.corr(), annot=True, cmap='RdBu_r', center=0, fmt='.2f', 
            square=True, mask=mask, vmin=-1, vmax=1, linewidths=0.5)
plt.title('Turnuva Senaryosu - Korelasyon Matrisi', fontweight='bold')
plt.tight_layout()
plt.savefig(r'C:\Users\Aya Karakoyun\Desktop\st\05_korelasyon.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()

# %%

fig, axes = plt.subplots(1, 3, figsize=(16, 5))
for i, sonuc in enumerate(sonuclar):
    p_mp = sonuc['tercihler']['p_mp']
    axes[i].hist(p_mp, bins=50, color='#FF6B6B', edgecolor='white', alpha=0.8)
    axes[i].axvline(0.5, color='black', linestyle='--', linewidth=2)
    axes[i].axvline(np.mean(p_mp), color='blue', linestyle='-', linewidth=2, label=f'Ort: {np.mean(p_mp):.3f}')
    axes[i].set_title(sonuc['senaryo'].split(' - ')[1], fontweight='bold')
    axes[i].set_xlabel('MP Tercih Olasılığı')
    axes[i].legend(fontsize=9)
plt.suptitle('MP Tercih Olasılığı Dağılımı (Softmax)', fontweight='bold')
plt.tight_layout()
plt.savefig(r'C:\Users\Aya Karakoyun\Desktop\st\06_softmax.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()

# %%

N = 5000
baz_params = {
    'beceri_mu': 50, 'beceri_sigma': 15,
    'internet_lambda': 20,
    'sosyal_alfa': 2, 'sosyal_beta': 5,
    'zaman_k': 2, 'zaman_theta': 40,
    'rekabet_min': 0, 'rekabet_max': 100,
    'yorgunluk_mu': 40, 'yorgunluk_sigma': 20
}
baz_p = parametre_ureti(N, baz_params)
baz_t = tercih_hesapla_v2(baz_p)
baz_mp = np.mean(baz_t['tercih_mp']) * 100

parametre_ayarlari = [
    ('Sosyal İstek ↑', {'sosyal_alfa': 4, 'sosyal_beta': 3}),
    ('Sosyal İstek ↓', {'sosyal_alfa': 1, 'sosyal_beta': 6}),
    ('Rekabet ↑', {'rekabet_min': 50}),
    ('Rekabet ↓', {'rekabet_max': 50}),
    ('İnternet ↑', {'internet_lambda': 14}),
    ('İnternet ↓', {'internet_lambda': 30}),
    ('Yorgunluk ↑', {'yorgunluk_mu': 60}),
    ('Yorgunluk ↓', {'yorgunluk_mu': 20}),
    ('Beceri ↑', {'beceri_mu': 60}),
    ('Beceri ↓', {'beceri_mu': 40}),
    ('Zaman ↑', {'zaman_theta': 60}),
    ('Zaman ↓', {'zaman_theta': 25}),
]

degisim_oranlari = []
for isim, degisiklik in parametre_ayarlari:
    test_params = baz_params.copy()
    test_params.update(degisiklik)
    p = parametre_ureti(N, test_params)
    t = tercih_hesapla_v2(p)
    mp_oran = np.mean(t['tercih_mp']) * 100
    fark = mp_oran - baz_mp
    degisim_oranlari.append({'Parametre': isim, 'Fark': fark})

fig, ax = plt.subplots(figsize=(12, 6))
isimler = [d['Parametre'] for d in degisim_oranlari]
farklar = [d['Fark'] for d in degisim_oranlari]
renkler_bar = ['#FF6B6B' if f > 0 else '#4ECDC4' for f in farklar]
bars = ax.barh(isimler, farklar, color=renkler_bar, edgecolor='white')
ax.axvline(0, color='black', linewidth=1)
ax.set_xlabel('MP Oranı Değişimi (%)')
ax.set_title('Duyarlılık Analizi', fontweight='bold')
for bar, fark in zip(bars, farklar):
    ax.text(bar.get_width() + (0.3 if fark >= 0 else -0.3), bar.get_y() + bar.get_height()/2, 
            f'%{fark:+.1f}', va='center', fontsize=9, ha='left' if fark >= 0 else 'right')
plt.tight_layout()
plt.savefig(r'C:\Users\Aya Karakoyun\Desktop\st\07_duyarlilik.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()

# %%

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# ============================================
# GRAFİK 8: Segmentasyon (DÜZGÜN)
# ============================================
s1 = sonuclar[0]
p = s1['parametreler']; t = s1['tercihler']
X = np.column_stack([p['beceri'], p['internet'], p['sosyal'], p['zaman'], p['rekabet'], p['yorgunluk']])
X_scaled = StandardScaler().fit_transform(X)
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
kumeler = kmeans.fit_predict(X_scaled)

kume_mp_oranlari = {}
for k in range(4):
    mask = kumeler == k
    kume_mp_oranlari[k] = np.mean(t['tercih_mp'][mask]) * 100

kume_sirali = sorted(kume_mp_oranlari.items(), key=lambda x: x[1], reverse=True)

isimler = ['Sosyal Rekabetci', 'Sosyal Kelebek', 'Yalniz Kurt', 'Yorgun Gezgin']
kume_isimleri = {}
for idx, (k, _) in enumerate(kume_sirali):
    kume_isimleri[k] = isimler[idx]

print("\nSegmentler:")
for k in range(4):
    mask = kumeler == k
    print(f"  {kume_isimleri[k]}: MP=%{np.mean(t['tercih_mp'][mask])*100:.1f}, "
          f"Sosyal={p['sosyal'][mask].mean():.0f}, "
          f"Rekabet={p['rekabet'][mask].mean():.0f}, "
          f"Yorgunluk={p['yorgunluk'][mask].mean():.0f}")

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
renkler = ['#FF6B6B', '#4ECDC4', '#FFD93D', '#C084FC']
for k in range(4):
    mask = kumeler == k
    axes[0].scatter(X_pca[mask, 0], X_pca[mask, 1], c=renkler[k], label=kume_isimleri[k], alpha=0.6, s=10)
axes[0].set_title('Oyuncu Segmentleri (PCA)', fontweight='bold')
axes[0].legend(fontsize=8, markerscale=3)

kume_mp = [np.mean(t['tercih_mp'][kumeler == k]) * 100 for k in range(4)]
bars = axes[1].bar([kume_isimleri[k] for k in range(4)], kume_mp, color=renkler, edgecolor='white')
axes[1].set_title('Segmentlere Gore MP Tercih Orani', fontweight='bold')
axes[1].set_ylabel('MP Tercih Orani (%)')
axes[1].set_ylim(0, 100)
axes[1].tick_params(axis='x', rotation=10)
for bar, val in zip(bars, kume_mp):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'%{val:.1f}', ha='center')
plt.suptitle('Oyuncu Segmentasyonu Analizi', fontweight='bold')
plt.tight_layout()
plt.savefig(r'C:\Users\Aya Karakoyun\Desktop\st\08_segmentasyon.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()
print("Segmentasyon kaydedildi!")
# %%
from sklearn.tree import DecisionTreeClassifier, plot_tree

s1 = sonuclar[0]
p = s1['parametreler']
t = s1['tercihler']

X = np.column_stack([
    p['sosyal'], p['rekabet'], p['internet'], 
    p['yorgunluk'], p['zaman'], p['beceri']
])
y = t['tercih_mp'].astype(int)

feature_names = ['Sosyal', 'Rekabet', 'İnternet', 'Yorgunluk', 'Zaman', 'Beceri']

dt = DecisionTreeClassifier(max_depth=4, random_state=42)
dt.fit(X, y)

onemler = dt.feature_importances_

# Sıralı yazdır
print("Parametre Önem Sıralaması:")
for i in np.argsort(onemler)[::-1]:
    print(f"  {feature_names[i]:<12}: %{onemler[i]*100:.1f}")

fig, axes = plt.subplots(1, 2, figsize=(18, 7))

# Sol: Önem bar chart
axes[0].barh(feature_names, onemler, color='#FF6B6B', edgecolor='white')
axes[0].set_title('Parametre Önem Skorları (Karar Ağacı)', fontweight='bold')
axes[0].set_xlabel('Önem Skoru')
for i, v in enumerate(onemler):
    axes[0].text(v + 0.01, i, f'%{v*100:.1f}', va='center')

# Sağ: Karar ağacı
plot_tree(dt, feature_names=feature_names, 
          class_names=['SP', 'MP'], filled=True, rounded=True,
          fontsize=9, ax=axes[1])
axes[1].set_title('Karar Ağacı Yapısı (Max Derinlik=4)', fontweight='bold')

plt.tight_layout()
plt.savefig(r'C:\Users\Aya Karakoyun\Desktop\st\08.5_karar_agaci.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()

# %%

def parametre_interpolasyon(params1, params2, alpha):
    result = {}
    for key in params1:
        result[key] = params1[key] + alpha * (params2[key] - params1[key])
    return result

s1_params = senaryolar['Senaryo 1 - Mevcut Durum']
s2_params = senaryolar['Senaryo 2 - Pandemi']
s3_params = senaryolar['Senaryo 3 - Turnuva']

N = 3000
gecis_adim = 20
gecis_mp = []

for i in range(gecis_adim + 1):
    alpha = i / gecis_adim
    if i <= gecis_adim // 2:
        a = i / (gecis_adim // 2)
        params = parametre_interpolasyon(s1_params, s2_params, a)
    else:
        a = (i - gecis_adim // 2) / (gecis_adim // 2)
        params = parametre_interpolasyon(s2_params, s3_params, a)
    p = parametre_ureti(N, params)
    t = tercih_hesapla_v2(p)
    gecis_mp.append(np.mean(t['tercih_mp']) * 100)

fig, ax = plt.subplots(figsize=(12, 5))
x = np.linspace(0, 1, gecis_adim + 1)
ax.plot(x, gecis_mp, 'o-', color='#FF6B6B', linewidth=2, markersize=4)
ax.axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='%50 Eşiği')
ax.axvspan(0, 0.5, alpha=0.1, color='blue', label='Mevcut → Pandemi')
ax.axvspan(0.5, 1, alpha=0.1, color='green', label='Pandemi → Turnuva')

# Anotasyonlar
ax.annotate(f'Mevcut Durum: %{gecis_mp[0]:.1f}', xy=(0, gecis_mp[0]), 
            xytext=(0.08, gecis_mp[0] - 6), fontsize=10, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='black'))
ax.annotate(f'Pandemi: %{gecis_mp[gecis_adim//2]:.1f}', 
            xy=(0.5, gecis_mp[gecis_adim//2]), 
            xytext=(0.42, gecis_mp[gecis_adim//2] + 8), fontsize=10, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='black'))
ax.annotate(f'Turnuva: %{gecis_mp[-1]:.1f}', xy=(1, gecis_mp[-1]), 
            xytext=(0.80, gecis_mp[-1] + 5), fontsize=10, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='black'))

ax.set_xlabel('Geçiş İlerlemesi', fontsize=12)
ax.set_ylabel('MP Tercih Oranı (%)', fontsize=12)
ax.set_title('Monte Carlo - Senaryolar Arası Kademeli Geçiş', fontweight='bold', fontsize=14)
ax.legend(fontsize=10)
ax.grid(alpha=0.3)
ax.set_ylim(40, 80)

plt.tight_layout()
plt.savefig(r'C:\Users\Aya Karakoyun\Desktop\st\09_monte_carlo.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()

print(f"\n📊 Geçiş Özeti:")
print(f"  Mevcut Durum → Pandemi: %{gecis_mp[0]:.1f} → %{gecis_mp[gecis_adim//2]:.1f} (Δ: %{gecis_mp[gecis_adim//2]-gecis_mp[0]:+.1f})")
print(f"  Pandemi → Turnuva:     %{gecis_mp[gecis_adim//2]:.1f} → %{gecis_mp[-1]:.1f} (Δ: %{gecis_mp[-1]-gecis_mp[gecis_adim//2]:+.1f})")
print(f"  Toplam Değişim:        %{gecis_mp[0]:.1f} → %{gecis_mp[-1]:.1f} (Δ: %{gecis_mp[-1]-gecis_mp[0]:+.1f})")
# %%

def bootstrap_mp_orani(params, N=3000, B=500):
    mp_oranlari = []
    for _ in range(B):
        p = parametre_ureti(N, params)
        t = tercih_hesapla_v2(p)
        mp_oranlari.append(np.mean(t['tercih_mp']) * 100)
    return np.array(mp_oranlari)

bootstrap_sonuclari = {}
for senaryo_adi, params in senaryolar.items():
    bootstrap_sonuclari[senaryo_adi] = bootstrap_mp_orani(params)

fig, ax = plt.subplots(figsize=(10, 5))
pozisyon = [1, 2, 3]
for i, (senaryo_adi, oranlar) in enumerate(bootstrap_sonuclari.items()):
    parts = ax.violinplot(oranlar, positions=[pozisyon[i]], showmeans=True, showmedians=True)
    for pc in parts['bodies']:
        pc.set_facecolor(['#FF6B6B', '#4ECDC4', '#FFD93D'][i])
        pc.set_alpha(0.7)
ax.set_xticks(pozisyon)
ax.set_xticklabels([s.split(' - ')[1] for s in bootstrap_sonuclari.keys()], fontsize=11)
ax.set_ylabel('MP Tercih Oranı (%)')
ax.set_title('Bootstrap Güven Aralıkları (500 Tekrar)', fontweight='bold')
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(r'C:\Users\Aya Karakoyun\Desktop\st\10_bootstrap.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()
# %%
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

fig, ax = plt.subplots(figsize=(8, 12))
ax.set_xlim(0, 10)
ax.set_ylim(0, 14)
ax.axis('off')

# Kutu stilleri
kutu_style = dict(boxstyle='round,pad=0.3', facecolor='#E8F0FE', edgecolor='#1a73e8', linewidth=2)
karar_style = dict(boxstyle='round,pad=0.3', facecolor='#FFF3CD', edgecolor='#f0ad4e', linewidth=2)
basla_style = dict(boxstyle='round,pad=0.3', facecolor='#D4EDDA', edgecolor='#28a745', linewidth=2)

# Oklar için fonksiyon
def ok_ekle(y1, y2, x=5):
    ax.annotate('', xy=(x, y2), xytext=(x, y1),
                arrowprops=dict(arrowstyle='->', color='#333333', lw=2))

# Başla
ax.text(5, 13.5, 'BAŞLA', ha='center', va='center', fontsize=11, fontweight='bold',
        bbox=basla_style)

# Senaryo seç
ax.text(5, 12, 'Senaryo Seç\n(1-Mevcut / 2-Pandemi / 3-Turnuva)', ha='center', va='center', fontsize=9,
        bbox=kutu_style)

# Parametre üret
ax.text(5, 10, 'Parametreleri Üret (N=10.000)\nNormal, Üstel, Beta, Gamma, Uniform', ha='center', va='center', fontsize=9,
        bbox=kutu_style)

# Normalize
ax.text(5, 8.2, 'Normalize Et\n(0-1 Aralığına Çek)', ha='center', va='center', fontsize=9,
        bbox=kutu_style)

# MP skor
ax.text(5, 6.5, 'MP Eğilim Skoru Hesapla\n(Baz:50 + Parametre Katkıları)', ha='center', va='center', fontsize=9,
        bbox=kutu_style)

# Softmax
ax.text(5, 4.8, 'Softmax ile P(MP) Hesapla\nP(MP) = e^(s_MP/τ) / (e^(s_MP/τ) + e^(s_SP/τ))', ha='center', va='center', fontsize=8,
        bbox=kutu_style)

# Karar
ax.text(5, 3.2, 'Rastgele Sayı Üret → P(MP) ile Karşılaştır\nP(MP) > rastgele → MP\nDeğilse → SP', ha='center', va='center', fontsize=9,
        bbox=karar_style)

# Kaydet
ax.text(5, 1.8, 'Sonuçları Kaydet\n(MP/SP Oranı, Eğilim, Kararsızlık)', ha='center', va='center', fontsize=9,
        bbox=kutu_style)

# Döngü kontrol
ax.text(5, 0.5, 'Tüm Senaryolar Bitti mi?\nEvet → BİTİR\nHayır → Başa Dön', ha='center', va='center', fontsize=9,
        bbox=karar_style)

# Oklar
ok_ekle(13, 12.5)
ok_ekle(11.7, 10.6)
ok_ekle(9.7, 8.6)
ok_ekle(7.9, 6.9)
ok_ekle(6.2, 5.2)
ok_ekle(4.5, 3.6)
ok_ekle(2.9, 2.1)

# Döngü oku (sağdan dolaşan)
ax.annotate('', xy=(7, 12), xytext=(7, 0.5),
            arrowprops=dict(arrowstyle='->', color='#dc3545', lw=2, connectionstyle='arc3,rad=0.5'))
ax.text(8.8, 6.5, 'Hayır\n(Tekrarla)', ha='center', va='center', fontsize=8, color='#dc3545', fontweight='bold')

# Bitiş oku
ax.annotate('', xy=(5, -0.3), xytext=(5, 0.2),
            arrowprops=dict(arrowstyle='->', color='#28a745', lw=2))
ax.text(5, -0.6, 'BİTİR', ha='center', va='center', fontsize=11, fontweight='bold', color='#28a745')

plt.title('Simülasyon Akış Diyagramı', fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig(r'C:\Users\Aya Karakoyun\Desktop\st\akis_diyagrami.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()

print("✅ Akış diyagramı kaydedildi: st/akis_diyagrami.png")
# %%


# %%

import os
kayit_klasoru = '/content/grafikler'
import os; os.makedirs(kayit_klasoru, exist_ok=True)
print("\n📁 Kaydedilen dosyalar:")
for dosya in sorted(os.listdir(kayit_klasoru)):
    if dosya.endswith('.png'):
        boyut = os.path.getsize(os.path.join(kayit_klasoru, dosya)) / 1024
        print(f"  ✅ {dosya} ({boyut:.0f} KB)")

print(f"\n📁 Kaydedilen dosyalar ({kayit_klasoru}):")
try:
    for dosya in sorted(os.listdir(kayit_klasoru)):
        if dosya.endswith('.png'):
            boyut = os.path.getsize(os.path.join(kayit_klasoru, dosya)) / 1024
            print(f"  ✅ {dosya} ({boyut:.0f} KB)")
except:
    print("  ⚠️ Klasör bulunamadı, grafikler bellekte gösterildi.")
        

        
