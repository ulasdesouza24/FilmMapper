import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import json
from datetime import timedelta
from film_veri_yapisi import Film, format_time

# JSON dosyasından film verilerini yükle
film = Film.load_from_json("C:\\Users\\pc\Desktop\\film\\interstaller_data.json")

def analyze_character_screen_time(film):
    """Her karakterin ekranda göründüğü toplam süreyi hesaplar"""
    character_screen_time = {char.name: 0 for char in film.characters}
    
    for scene in film.scenes:
        scene_duration = scene.end_time - scene.start_time
        for character in scene.characters:
            character_screen_time[character.name] += scene_duration
    
    # Sonuçları DataFrame'e dönüştür
    df = pd.DataFrame({
        'Character': list(character_screen_time.keys()),
        'Screen Time (seconds)': list(character_screen_time.values())
    })
    
    # Ekran süresine göre sırala
    df = df.sort_values('Screen Time (seconds)', ascending=False)
    
    # Görselleştir
    plt.figure(figsize=(12, 8))
    sns.barplot(x='Screen Time (seconds)', y='Character', data=df)
    plt.title(f'Character Screen Time in {film.title}')
    plt.tight_layout()
    plt.savefig('character_screen_time.png')
    plt.close()
    
    return df

def analyze_location_usage(film):
    """Her lokasyonun kullanıldığı toplam süreyi hesaplar"""
    location_usage = {loc.name: 0 for loc in film.locations}
    
    for scene in film.scenes:
        scene_duration = scene.end_time - scene.start_time
        location_usage[scene.location.name] += scene_duration
    
    # Sonuçları DataFrame'e dönüştür
    df = pd.DataFrame({
        'Location': list(location_usage.keys()),
        'Usage Time (seconds)': list(location_usage.values())
    })
    
    # Kullanım süresine göre sırala
    df = df.sort_values('Usage Time (seconds)', ascending=False)
    
    # Görselleştir
    plt.figure(figsize=(12, 8))
    sns.barplot(x='Usage Time (seconds)', y='Location', data=df)
    plt.title(f'Location Usage in {film.title}')
    plt.tight_layout()
    plt.savefig('location_usage.png')
    plt.close()
    
    return df

def create_character_network(film):
    """Karakterler arasındaki ilişkileri gösteren bir ağ grafiği oluşturur"""
    G = nx.Graph()
    
    # Düğümleri ekle (karakterler)
    for character in film.characters:
        G.add_node(character.name, importance=character.importance)
    
    # Kenarları ekle (ilişkiler)
    for relationship in film.relationships:
        G.add_edge(
            relationship.character1.name, 
            relationship.character2.name, 
            type=relationship.type,
            strength=relationship.strength
        )
    
    # Ağı görselleştir
    plt.figure(figsize=(14, 10))
    
    # Düğüm boyutlarını karakter önemine göre ayarla
    node_sizes = [G.nodes[node]['importance'] * 100 for node in G.nodes]
    
    # Kenar kalınlıklarını ilişki gücüne göre ayarla
    edge_widths = [G[u][v]['strength'] / 2 for u, v in G.edges]
    
    # İlişki türlerine göre kenar renkleri
    relationship_types = list(set([G[u][v]['type'] for u, v in G.edges]))
    colors = plt.cm.tab10(np.linspace(0, 1, len(relationship_types)))
    color_map = {rel_type: colors[i] for i, rel_type in enumerate(relationship_types)}
    
    edge_colors = [color_map[G[u][v]['type']] for u, v in G.edges]
    
    # Ağı çiz
    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.5, edge_color=edge_colors)
    nx.draw_networkx_labels(G, pos, font_size=10)
    
    # Renk açıklamalarını ekle
    legend_elements = [Line2D([0], [0], color=color_map[rel_type], lw=4, label=rel_type) 
                      for rel_type in relationship_types]
    plt.legend(handles=legend_elements, title="Relationship Types")
    
    plt.title(f'Character Relationships in {film.title}')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('character_network.png')
    plt.close()
    
    return G

def create_timeline(film):
    """Film zaman çizelgesi oluşturur"""
    # Olayları zaman sırasına göre sırala
    events = sorted(film.events, key=lambda x: x.time)
    
    # Zaman çizelgesi oluştur
    plt.figure(figsize=(15, 8))
    
    # Olay türlerine göre renkler
    event_types = list(set([event.type for event in events]))
    colors = plt.cm.tab20(np.linspace(0, 1, len(event_types)))
    color_map = {event_type: colors[i] for i, event_type in enumerate(event_types)}
    
    # Olayları çiz
    y_positions = np.arange(len(events))
    x_positions = [event.time for event in events]
    
    plt.scatter(x_positions, y_positions, s=[event.importance * 50 for event in events], 
                c=[color_map[event.type] for event in events], alpha=0.7)
    
    # Olay isimlerini ekle
    for i, event in enumerate(events):
        plt.text(event.time, y_positions[i], f" {event.name}", 
                 verticalalignment='center', fontsize=9)
    
    # Renk açıklamalarını ekle
    legend_elements = [Line2D([0], [0], marker='o', color='w', 
                             markerfacecolor=color_map[event_type], markersize=10, 
                             label=event_type) for event_type in event_types]
    plt.legend(handles=legend_elements, title="Event Types")
    
    # Eksen etiketleri
    plt.xlabel('Time (seconds)')
    plt.ylabel('Events')
    plt.title(f'Timeline of Events in {film.title}')
    
    # X eksenini saat:dakika:saniye formatında göster
    plt.xticks([0, film.duration/4, film.duration/2, 3*film.duration/4, film.duration],
              [format_time(0), format_time(film.duration/4), 
               format_time(film.duration/2), format_time(3*film.duration/4), 
               format_time(film.duration)])
    
    plt.yticks([])  # Y eksenindeki sayıları gizle
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig('event_timeline.png')
    plt.close()

def create_character_location_heatmap(film):
    """Karakterlerin hangi lokasyonlarda ne kadar zaman geçirdiğini gösteren ısı haritası"""
    # Karakter-lokasyon matrisini oluştur
    character_names = [char.name for char in film.characters]
    location_names = [loc.name for loc in film.locations]
    
    # Matris oluştur ve sıfırla doldur
    matrix = np.zeros((len(character_names), len(location_names)))
    
    # Sahneleri dolaşarak matrisi doldur
    for scene in film.scenes:
        scene_duration = scene.end_time - scene.start_time
        location_idx = location_names.index(scene.location.name)
        
        for character in scene.characters:
            character_idx = character_names.index(character.name)
            matrix[character_idx, location_idx] += scene_duration
    
    # DataFrame'e dönüştür
    df = pd.DataFrame(matrix, index=character_names, columns=location_names)
    
    # Isı haritası oluştur
    plt.figure(figsize=(14, 10))
    sns.heatmap(df, annot=True, fmt='.0f', cmap='YlGnBu', linewidths=.5)
    plt.title(f'Character-Location Time Distribution in {film.title} (seconds)')
    plt.tight_layout()
    plt.savefig('character_location_heatmap.png')
    plt.close()
    
    return df

def create_scene_flow(film):
    """Sahnelerin akışını ve geçişlerini gösteren bir diyagram"""
    # Sahneleri zaman sırasına göre sırala
    scenes = sorted(film.scenes, key=lambda x: x.start_time)
    
    # Lokasyon renklerini belirle
    location_names = list(set([scene.location.name for scene in scenes]))
    colors = plt.cm.tab20(np.linspace(0, 1, len(location_names)))
    color_map = {loc_name: colors[i] for i, loc_name in enumerate(location_names)}
    
    # Sahne akışı grafiği oluştur
    plt.figure(figsize=(15, 6))
    
    for i, scene in enumerate(scenes):
        # Sahne bloğunu çiz
        plt.fill_between(
            [scene.start_time, scene.end_time], 
            [0], [1], 
            color=color_map[scene.location.name],
            alpha=0.7
        )
        
        # Sahne açıklamasını ekle (sadece yeterli alan varsa)
        scene_duration = scene.end_time - scene.start_time
        if scene_duration > film.duration / 50:  # Minimum genişlik kontrolü
            plt.text(
                (scene.start_time + scene.end_time) / 2, 
                0.5, 
                scene.description[:20] + ('...' if len(scene.description) > 20 else ''),
                horizontalalignment='center',
                verticalalignment='center',
                fontsize=8
            )
    
    # Renk açıklamalarını ekle
    legend_elements = [mpatches.Patch(color=color_map[loc_name], label=loc_name) 
                      for loc_name in location_names]
    plt.legend(handles=legend_elements, title="Locations")
    
    # Eksen etiketleri
    plt.xlabel('Time')
    plt.ylabel('')
    plt.title(f'Scene Flow in {film.title}')
    
    # X eksenini saat:dakika:saniye formatında göster
    plt.xticks([0, film.duration/4, film.duration/2, 3*film.duration/4, film.duration],
              [format_time(0), format_time(film.duration/4), 
               format_time(film.duration/2), format_time(3*film.duration/4), 
               format_time(film.duration)])
    
    plt.yticks([])  # Y eksenindeki sayıları gizle
    
    plt.tight_layout()
    plt.savefig('scene_flow.png')
    plt.close()

def create_emotional_intensity_chart(film):
    """Film boyunca duygusal yoğunluğu gösteren bir grafik oluşturur"""
    # Olayları zaman sırasına göre sırala
    events = sorted(film.events, key=lambda x: x.time)
    
    # Zaman çizelgesi oluştur
    plt.figure(figsize=(15, 6))
    
    # X ekseni için zaman noktaları (film süresinin %1'i aralıklarla)
    time_points = np.linspace(0, film.duration, 100)
    emotional_intensity = np.zeros(len(time_points))
    
    # Her olay için duygusal etki hesapla (önem derecesi ve mesafesine göre)
    for event in events:
        # Olayın duygusal etkisi (önem derecesine bağlı)
        impact = event.importance * 1.5
        
        # Etki mesafesi (önem derecesine bağlı)
        impact_distance = film.duration * (0.05 + (event.importance / 20))
        
        # Her zaman noktası için etki hesapla
        for i, t in enumerate(time_points):
            # Olaya olan mesafe
            distance = abs(t - event.time)
            
            # Mesafeye bağlı olarak azalan etki
            if distance < impact_distance:
                # Gaussian etki fonksiyonu
                effect = impact * np.exp(-(distance**2) / (2 * (impact_distance/3)**2))
                emotional_intensity[i] += effect
    
    # Grafiği çiz
    plt.plot(time_points, emotional_intensity, 'r-', linewidth=2)
    
    # Önemli olayları işaretle
    for event in events:
        if event.importance >= 7:  # Sadece önemli olayları göster
            plt.axvline(x=event.time, color='gray', linestyle='--', alpha=0.5)
            plt.text(event.time, max(emotional_intensity)*0.9, event.name, 
                    rotation=90, verticalalignment='top', fontsize=8)
    
    # Eksen etiketleri
    plt.xlabel('Zaman')
    plt.ylabel('Duygusal Yoğunluk')
    plt.title(f'{film.title} - Duygusal Yoğunluk Grafiği')
    
    # X eksenini saat:dakika:saniye formatında göster
    plt.xticks([0, film.duration/4, film.duration/2, 3*film.duration/4, film.duration],
              [format_time(0), format_time(film.duration/4), 
               format_time(film.duration/2), format_time(3*film.duration/4), 
               format_time(film.duration)])
    
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('emotional_intensity.png')
    plt.close()

def create_character_interaction_heatmap(film):
    """Karakterlerin birbirleriyle etkileşimlerini gösteren ısı haritası"""
    # Sadece önemli karakterleri al (önem derecesi 5 ve üzeri)
    main_characters = [char for char in film.characters if char.importance >= 5]
    char_names = [char.name for char in main_characters]
    
    # Etkileşim matrisini oluştur
    n_chars = len(main_characters)
    interaction_matrix = np.zeros((n_chars, n_chars))
    
    # Sahneleri dolaşarak etkileşimleri hesapla
    for scene in film.scenes:
        scene_chars = [char for char in scene.characters if char in main_characters]
        scene_duration = scene.end_time - scene.start_time
        
        # Sahnedeki her karakter çifti için etkileşim puanı ekle
        for i, char1 in enumerate(scene_chars):
            for j, char2 in enumerate(scene_chars):
                if i != j:  # Kendisiyle etkileşim yok
                    idx1 = main_characters.index(char1)
                    idx2 = main_characters.index(char2)
                    interaction_matrix[idx1, idx2] += scene_duration
    
    # Isı haritası oluştur
    plt.figure(figsize=(12, 10))
    mask = np.zeros_like(interaction_matrix)
    mask[np.triu_indices_from(mask)] = True  # Sadece alt üçgeni göster
    
    sns.heatmap(interaction_matrix, annot=True, fmt='.0f', cmap='YlOrRd', 
                xticklabels=char_names, yticklabels=char_names, mask=mask)
    
    plt.title(f'{film.title} - Karakter Etkileşim Isı Haritası (saniye)')
    plt.tight_layout()
    plt.savefig('character_interaction_heatmap.png')
    plt.close()

def create_character_trajectories(film):
    """Karakterlerin film boyunca lokasyonlar arasındaki hareketini gösteren grafik"""
    # Önemli karakterleri seç
    main_characters = [char for char in film.characters if char.importance >= 6]
    
    # Lokasyonları listele
    locations = film.locations
    loc_names = [loc.name for loc in locations]
    
    # Her karakter için yörünge oluştur
    plt.figure(figsize=(15, 8))
    
    # Renk paleti
    colors = plt.cm.tab10(np.linspace(0, 1, len(main_characters)))
    
    for char_idx, character in enumerate(main_characters):
        # Karakterin bulunduğu sahneleri bul ve zamanla sırala
        char_scenes = [s for s in film.scenes if character in s.characters]
        char_scenes = sorted(char_scenes, key=lambda x: x.start_time)
        
        if not char_scenes:
            continue
            
        # Zaman ve lokasyon indeksleri
        times = []
        loc_indices = []
        
        for scene in char_scenes:
            times.append(scene.start_time)
            loc_indices.append(loc_names.index(scene.location.name))
            
            times.append(scene.end_time)
            loc_indices.append(loc_names.index(scene.location.name))
        
        # Yörüngeyi çiz
        plt.plot(times, loc_indices, '-', color=colors[char_idx], 
                 label=character.name, linewidth=2, alpha=0.7)
        
        # Başlangıç ve bitiş noktalarını işaretle
        plt.scatter([times[0]], [loc_indices[0]], color=colors[char_idx], s=100, zorder=5)
        plt.scatter([times[-1]], [loc_indices[-1]], color=colors[char_idx], 
                   marker='*', s=150, zorder=5, edgecolor='black')
    
    # Eksen ayarları
    plt.yticks(range(len(loc_names)), loc_names)
    plt.xlabel('Zaman')
    plt.ylabel('Lokasyon')
    plt.title(f'{film.title} - Karakter Yörüngeleri')
    
    # X eksenini saat:dakika:saniye formatında göster
    plt.xticks([0, film.duration/4, film.duration/2, 3*film.duration/4, film.duration],
              [format_time(0), format_time(film.duration/4), 
               format_time(film.duration/2), format_time(3*film.duration/4), 
               format_time(film.duration)])
    
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=5)
    
    plt.tight_layout()
    plt.savefig('character_trajectories.png')
    plt.close()

def create_three_act_structure(film):
    """Filmin üç perde yapısını analiz eden ve gösteren bir grafik"""
    # Filmi üç perdeye böl
    act1_end = film.duration * 0.25  # 1. perde sonu (yaklaşık)
    act2_end = film.duration * 0.75  # 2. perde sonu (yaklaşık)
    
    # Olayları zaman sırasına göre sırala
    events = sorted(film.events, key=lambda x: x.time)
    
    # Perdelere göre olayları grupla
    act1_events = [e for e in events if e.time <= act1_end]
    act2_events = [e for e in events if act1_end < e.time <= act2_end]
    act3_events = [e for e in events if e.time > act2_end]
    
    # Grafik oluştur
    plt.figure(figsize=(15, 10))
    
    # Perde arka planlarını çiz
    plt.axvspan(0, act1_end, alpha=0.2, color='blue', label='1. Perde: Giriş')
    plt.axvspan(act1_end, act2_end, alpha=0.2, color='green', label='2. Perde: Gelişme')
    plt.axvspan(act2_end, film.duration, alpha=0.2, color='red', label='3. Perde: Sonuç')
    
    # Olayları çiz
    for i, event in enumerate(events):
        plt.scatter(event.time, event.importance, s=event.importance*20, 
                   alpha=0.7, zorder=5, 
                   color='blue' if event.time <= act1_end else 
                         'green' if event.time <= act2_end else 'red')
        
        # Önemli olayları etiketle
        if event.importance >= 8:
            plt.annotate(event.name, (event.time, event.importance),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=8, arrowprops=dict(arrowstyle='->', lw=1))
    
    # Eksen ayarları
    plt.xlabel('Zaman')
    plt.ylabel('Olay Önemi')
    plt.title(f'{film.title} - Üç Perde Yapısı Analizi')
    
    # X eksenini saat:dakika:saniye formatında göster
    plt.xticks([0, act1_end, act2_end, film.duration],
              [format_time(0), format_time(act1_end), 
               format_time(act2_end), format_time(film.duration)])
    
    # Perde etiketleri
    plt.text(act1_end/2, 10.5, "1. PERDE\nGİRİŞ", ha='center', fontsize=12, fontweight='bold')
    plt.text(act1_end + (act2_end-act1_end)/2, 10.5, "2. PERDE\nGELİŞME", ha='center', fontsize=12, fontweight='bold')
    plt.text(act2_end + (film.duration-act2_end)/2, 10.5, "3. PERDE\nSONUÇ", ha='center', fontsize=12, fontweight='bold')
    
    plt.ylim(0, 11)
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3)
    
    plt.tight_layout()
    plt.savefig('three_act_structure.png')
    plt.close()

def create_character_development_chart(film):
    """Karakterlerin film boyunca gelişimini gösteren grafik"""
    # Önemli karakterleri seç
    main_characters = [char for char in film.characters if char.importance >= 7]
    
    # Karakter gelişim noktalarını tanımla (manuel olarak girilmeli)
    # Bu örnek için rastgele veriler oluşturuyoruz
    # Gerçek uygulamada, bu verileri kullanıcıdan almalısınız
    character_development = {}
    
    for character in main_characters:
        # Her karakter için 5-10 gelişim noktası oluştur
        num_points = np.random.randint(5, 11)
        times = sorted(np.random.choice(range(0, film.duration), size=num_points, replace=False))
        
        # Gelişim değerleri (1-10 arası)
        # Genellikle artan bir trend gösterir
        values = np.sort(np.random.randint(1, 11, size=num_points))
        
        character_development[character.name] = {
            'times': times,
            'values': values
        }
    
    # Grafik oluştur
    plt.figure(figsize=(15, 8))
    
    # Renk paleti
    colors = plt.cm.tab10(np.linspace(0, 1, len(main_characters)))
    
    for i, character in enumerate(main_characters):
        data = character_development[character.name]
        plt.plot(data['times'], data['values'], 'o-', color=colors[i], 
                label=character.name, linewidth=2, markersize=8)
    
    # Eksen ayarları
    plt.xlabel('Zaman')
    plt.ylabel('Karakter Gelişimi (1-10)')
    plt.title(f'{film.title} - Karakter Gelişim Grafiği')
    
    # X eksenini saat:dakika:saniye formatında göster
    plt.xticks([0, film.duration/4, film.duration/2, 3*film.duration/4, film.duration],
              [format_time(0), format_time(film.duration/4), 
               format_time(film.duration/2), format_time(3*film.duration/4), 
               format_time(film.duration)])
    
    plt.ylim(0, 11)
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper left')
    
    plt.tight_layout()
    plt.savefig('character_development.png')
    plt.close()

def create_theme_analysis(film):
    """Filmdeki temaların zaman içindeki dağılımını gösteren grafik"""
    # Örnek temalar (gerçek uygulamada kullanıcıdan alınmalı)
    themes = ["Aile", "Sevgi", "Bilim", "Keşif", "Hayatta Kalma", "Fedakarlık"]
    
    # Her tema için zaman içindeki yoğunluğu tanımla (manuel olarak girilmeli)
    # Bu örnek için rastgele veriler oluşturuyoruz
    theme_intensity = {}
    
    for theme in themes:
        # Her tema için 100 zaman noktasında yoğunluk değeri
        time_points = np.linspace(0, film.duration, 100)
        
        # Yoğunluk değerleri (0-10 arası)
        # Bazı temalarda belirli bölgelerde yoğunlaşma olabilir
        base = np.random.rand(100) * 3  # Temel değer
        peak1_center = np.random.randint(20, 40)  # İlk tepe noktası
        peak2_center = np.random.randint(60, 80)  # İkinci tepe noktası
        
        # Gaussian tepeler ekle
        peak1 = 7 * np.exp(-0.01 * (np.arange(100) - peak1_center)**2)
        peak2 = 5 * np.exp(-0.01 * (np.arange(100) - peak2_center)**2)
        
        intensity = base + peak1 + peak2
        intensity = np.clip(intensity, 0, 10)  # 0-10 arasına sınırla
        
        theme_intensity[theme] = {
            'times': time_points,
            'values': intensity
        }
    
    # Grafik oluştur
    plt.figure(figsize=(15, 10))
    
    # Renk paleti
    colors = plt.cm.tab10(np.linspace(0, 1, len(themes)))
    
    for i, theme in enumerate(themes):
        data = theme_intensity[theme]
        plt.plot(data['times'], data['values'], '-', color=colors[i], 
                label=theme, linewidth=2, alpha=0.7)
    
    # Eksen ayarları
    plt.xlabel('Zaman')
    plt.ylabel('Tema Yoğunluğu (0-10)')
    plt.title(f'{film.title} - Tema Analizi')
    
    # X eksenini saat:dakika:saniye formatında göster
    plt.xticks([0, film.duration/4, film.duration/2, 3*film.duration/4, film.duration],
              [format_time(0), format_time(film.duration/4), 
               format_time(film.duration/2), format_time(3*film.duration/4), 
               format_time(film.duration)])
    
    plt.ylim(0, 11)
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3)
    
    plt.tight_layout()
    plt.savefig('theme_analysis.png')
    plt.close()

def create_parallel_storylines(film):
    """Filmdeki paralel hikaye çizgilerini gösteren grafik"""
    # Hikaye çizgileri (gerçek uygulamada kullanıcıdan alınmalı)
    storylines = ["Cooper'ın Yolculuğu", "Murph'in Dünya'daki Çalışmaları", 
                 "Mann Gezegeni Olayları", "Brand'in Yolculuğu"]
    
    # Her hikaye çizgisi için başlangıç ve bitiş zamanları (manuel olarak girilmeli)
    # Bu örnek için varsayılan değerler kullanıyoruz
    storyline_segments = {
        "Cooper'ın Yolculuğu": [
            (0, film.duration)  # Tüm film boyunca
        ],
        "Murph'in Dünya'daki Çalışmaları": [
            (film.duration * 0.3, film.duration * 0.8)
        ],
        "Mann Gezegeni Olayları": [
            (film.duration * 0.5, film.duration * 0.7)
        ],
        "Brand'in Yolculuğu": [
            (film.duration * 0.25, film.duration)
        ]
    }
    
    # Grafik oluştur
    plt.figure(figsize=(15, 6))
    
    # Renk paleti
    colors = plt.cm.tab10(np.linspace(0, 1, len(storylines)))
    
    # Y pozisyonları
    y_positions = np.arange(len(storylines))
    
    # Hikaye çizgilerini çiz
    for i, storyline in enumerate(storylines):
        segments = storyline_segments[storyline]
        
        for start, end in segments:
            plt.plot([start, end], [y_positions[i], y_positions[i]], 
                    '-', linewidth=6, color=colors[i], alpha=0.7)
            
            # Başlangıç ve bitiş noktalarını işaretle
            plt.scatter([start, end], [y_positions[i], y_positions[i]], 
                       color=colors[i], s=100, zorder=5, edgecolor='black')
    
    # Eksen ayarları
    plt.yticks(y_positions, storylines)
    plt.xlabel('Zaman')
    plt.title(f'{film.title} - Paralel Hikaye Çizgileri')
    
    # X eksenini saat:dakika:saniye formatında göster
    plt.xticks([0, film.duration/4, film.duration/2, 3*film.duration/4, film.duration],
              [format_time(0), format_time(film.duration/4), 
               format_time(film.duration/2), format_time(3*film.duration/4), 
               format_time(film.duration)])
    
    plt.grid(True, axis='x', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig('parallel_storylines.png')
    plt.close()

def create_visual_style_analysis(film):
    """Filmin görsel stilini analiz eden grafik"""
    # Görsel stil kategorileri (gerçek uygulamada kullanıcıdan alınmalı)
    style_categories = ["Yakın Çekim", "Orta Çekim", "Geniş Çekim", 
                       "Karanlık Tonlar", "Parlak Tonlar", "Mavi Tonlar", "Sıcak Tonlar"]
    
    # Her kategori için zaman içindeki dağılımı (manuel olarak girilmeli)
    # Bu örnek için rastgele veriler oluşturuyoruz
    style_distribution = {}
    
    # Zaman noktaları (film süresinin %1'i aralıklarla)
    time_points = np.linspace(0, film.duration, 100)
    
    for category in style_categories:
        # Her kategori için rastgele değerler (0-1 arası)
        values = np.zeros(100)
        
        # Bazı bölgelerde belirli stillerin yoğunlaşması
        for _ in range(3):  # 3 yoğunlaşma bölgesi
            center = np.random.randint(10, 90)
            width = np.random.randint(5, 15)
            height = np.random.random() * 0.8 + 0.2  # 0.2-1.0 arası
            
            # Gaussian yoğunlaşma
            for i in range(100):
                values[i] += height * np.exp(-0.5 * ((i - center) / width)**2)
        
        # 0-1 arasına normalize et
        values = np.clip(values, 0, 1)
        
        style_distribution[category] = values
    
    # Grafik oluştur - Isı haritası
    plt.figure(figsize=(15, 8))
    
    # Veriyi matrise dönüştür
    matrix = np.array([style_distribution[cat] for cat in style_categories])
    
    # Isı haritası çiz
    sns.heatmap(matrix, cmap='viridis', 
               xticklabels=[format_time(t) for t in np.linspace(0, film.duration, 10)],
               yticklabels=style_categories)
    
    plt.xlabel('Zaman')
    plt.ylabel('Görsel Stil Kategorisi')
    plt.title(f'{film.title} - Görsel Stil Analizi')
    
    plt.tight_layout()
    plt.savefig('visual_style_analysis.png')
    plt.close()

def create_interactive_timeline(film):
    """Bokeh kullanarak interaktif bir zaman çizelgesi oluşturur"""
    from bokeh.plotting import figure, output_file, save
    from bokeh.models import ColumnDataSource, HoverTool, LabelSet
    
    # Olayları zaman sırasına göre sırala
    events = sorted(film.events, key=lambda x: x.time)
    
    # Veri kaynağı oluştur
    source = ColumnDataSource(data=dict(
        x=[e.time for e in events],
        y=[e.importance for e in events],
        desc=[e.name for e in events],
        type=[e.type for e in events],
        chars=[", ".join([c.name for c in e.characters]) for e in events],
        loc=[e.location.name for e in events],
        size=[e.importance * 5 for e in events]
    ))
    
    # Figür oluştur
    p = figure(width=1000, height=500, title=f"{film.title} - İnteraktif Zaman Çizelgesi",
              x_axis_label="Zaman (saniye)", y_axis_label="Önem")
    
    # Noktaları çiz
    circles = p.circle('x', 'y', size='size', source=source, 
                      fill_alpha=0.6, line_color=None)
    
    # Fare üzerine gelince gösterilecek bilgiler
    hover = HoverTool(tooltips=[
        ("Olay", "@desc"),
        ("Tür", "@type"),
        ("Zaman", "@x{0,0} saniye"),
        ("Önem", "@y"),
        ("Karakterler", "@chars"),
        ("Lokasyon", "@loc")
    ])
    
    p.add_tools(hover)
    
    # HTML dosyası olarak kaydet
    output_file("interactive_timeline.html")
    save(p)
    
    print("İnteraktif zaman çizelgesi 'interactive_timeline.html' dosyasına kaydedildi.")

# Tüm analizleri çalıştır
try:
    print("Karakter ekran süresi analizi yapılıyor...")
    character_screen_time = analyze_character_screen_time(film)
    print(character_screen_time)
    
    print("\nLokasyon kullanımı analizi yapılıyor...")
    location_usage = analyze_location_usage(film)
    print(location_usage)
    
    print("\nKarakter ağı oluşturuluyor...")
    character_network = create_character_network(film)
    
    print("\nZaman çizelgesi oluşturuluyor...")
    create_timeline(film)
    
    print("\nKarakter-lokasyon ısı haritası oluşturuluyor...")
    character_location_df = create_character_location_heatmap(film)
    print(character_location_df)
    
    print("\nSahne akışı diyagramı oluşturuluyor...")
    create_scene_flow(film)

    print("Duygusal yoğunluk grafiği oluşturuluyor...")
    create_emotional_intensity_chart(film)
    
    print("Karakter etkileşim ısı haritası oluşturuluyor...")
    create_character_interaction_heatmap(film)
    
    print("Karakter yörüngeleri grafiği oluşturuluyor...")
    create_character_trajectories(film)
    
    print("Üç perde yapısı analizi oluşturuluyor...")
    create_three_act_structure(film)
    
    print("Karakter gelişim grafiği oluşturuluyor...")
    create_character_development_chart(film)
    
    print("Tema analizi grafiği oluşturuluyor...")
    create_theme_analysis(film)
    
    print("Paralel hikaye çizgileri grafiği oluşturuluyor...")
    create_parallel_storylines(film)
    
    print("Görsel stil analizi oluşturuluyor...")
    create_visual_style_analysis(film)
    
    print("İnteraktif zaman çizelgesi oluşturuluyor...")
    create_interactive_timeline(film)
    
    print("\nTüm analizler tamamlandı ve görselleştirmeler kaydedildi.")
except Exception as e:
    print(f"Hata oluştu: {e}")