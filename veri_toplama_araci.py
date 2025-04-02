import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import timedelta
from film_veri_yapisi import Film, Character, Location, Scene, Relationship, Event, format_time

class FilmDataCollector:
    def __init__(self, root):
        self.root = root
        self.root.title("Film Veri Toplama Aracı")
        self.root.geometry("1200x800")
        
        # Film verisi
        self.film = None
        self.current_time = 0  # saniye cinsinden
        
        # Ana çerçeve
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Film bilgileri çerçevesi
        self.film_frame = ttk.LabelFrame(self.main_frame, text="Film Bilgileri")
        self.film_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Film adı ve süresi
        ttk.Label(self.film_frame, text="Film Adı:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.film_name_var = tk.StringVar()
        ttk.Entry(self.film_frame, textvariable=self.film_name_var, width=30).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(self.film_frame, text="Film Süresi (dakika):").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.film_duration_var = tk.IntVar(value=120)
        ttk.Spinbox(self.film_frame, from_=1, to=300, textvariable=self.film_duration_var, width=5).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        ttk.Button(self.film_frame, text="Film Oluştur", command=self.create_film).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(self.film_frame, text="Kaydet", command=self.save_film).grid(row=0, column=5, padx=5, pady=5)
        ttk.Button(self.film_frame, text="Yükle", command=self.load_film).grid(row=0, column=6, padx=5, pady=5)
        
        # Zaman kontrolü
        self.time_frame = ttk.LabelFrame(self.main_frame, text="Zaman Kontrolü")
        self.time_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.time_frame, text="Şu anki zaman:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.current_time_label = ttk.Label(self.time_frame, text="00:00:00")
        self.current_time_label.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Button(self.time_frame, text="-1 dk", command=lambda: self.adjust_time(-60)).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(self.time_frame, text="-10 sn", command=lambda: self.adjust_time(-10)).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(self.time_frame, text="+10 sn", command=lambda: self.adjust_time(10)).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(self.time_frame, text="+1 dk", command=lambda: self.adjust_time(60)).grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Label(self.time_frame, text="Zamana Git (hh:mm:ss):").grid(row=0, column=6, padx=5, pady=5, sticky=tk.W)
        self.goto_time_var = tk.StringVar(value="00:00:00")
        ttk.Entry(self.time_frame, textvariable=self.goto_time_var, width=8).grid(row=0, column=7, padx=5, pady=5, sticky=tk.W)
        ttk.Button(self.time_frame, text="Git", command=self.goto_time).grid(row=0, column=8, padx=5, pady=5)
        
        # Notebook (sekmeli arayüz)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Karakter sekmesi
        self.character_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.character_frame, text="Karakterler")
        self.setup_character_tab()
        
        # Lokasyon sekmesi
        self.location_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.location_frame, text="Lokasyonlar")
        self.setup_location_tab()
        
        # Sahne sekmesi
        self.scene_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.scene_frame, text="Sahneler")
        self.setup_scene_tab()
        
        # İlişki sekmesi
        self.relationship_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.relationship_frame, text="İlişkiler")
        self.setup_relationship_tab()
        
        # Olay sekmesi
        self.event_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.event_frame, text="Olaylar")
        self.setup_event_tab()
        
    def create_film(self):
        """Film nesnesini oluşturur"""
        film_name = self.film_name_var.get().strip()
        if not film_name:
            messagebox.showerror("Hata", "Film adı boş olamaz!")
            return
            
        film_duration = self.film_duration_var.get() * 60  # dakikayı saniyeye çevir
        
        self.film = Film(film_name, film_duration)
        messagebox.showinfo("Bilgi", f"'{film_name}' filmi oluşturuldu.")
        
        # Mevcut listeleri temizle
        self.refresh_character_list()
        self.refresh_location_list()
        self.refresh_scene_list()
        self.refresh_relationship_list()
        self.refresh_event_list()
    
    def save_film(self):
        """Film verisini JSON dosyasına kaydeder"""
        if not self.film:
            messagebox.showerror("Hata", "Önce bir film oluşturmalısınız!")
            return
            
        filename = f"{self.film.title.replace(' ', '_').lower()}_data.json"
        self.film.save_to_json(filename)
        messagebox.showinfo("Bilgi", f"Film verisi '{filename}' dosyasına kaydedildi.")
    
    def load_film(self):
        """Film verisini JSON dosyasından yükler"""
        import tkinter.filedialog as filedialog
        
        filename = filedialog.askopenfilename(
            title="Film Verisi Yükle",
            filetypes=[("JSON Dosyaları", "*.json"), ("Tüm Dosyalar", "*.*")]
        )
        
        if not filename:
            return
            
        try:
            self.film = Film.load_from_json(filename)
            self.film_name_var.set(self.film.title)
            self.film_duration_var.set(self.film.duration // 60)  # saniyeyi dakikaya çevir
            
            messagebox.showinfo("Bilgi", f"'{self.film.title}' filmi yüklendi.")
            
            # Listeleri güncelle
            self.refresh_character_list()
            self.refresh_location_list()
            self.refresh_scene_list()
            self.refresh_relationship_list()
            self.refresh_event_list()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya yüklenirken hata oluştu: {str(e)}")
    
    def adjust_time(self, seconds):
        """Mevcut zamanı belirtilen saniye kadar ayarlar"""
        if not self.film:
            messagebox.showerror("Hata", "Önce bir film oluşturmalısınız!")
            return
            
        self.current_time += seconds
        
        # Sınırları kontrol et
        if self.current_time < 0:
            self.current_time = 0
        elif self.current_time > self.film.duration:
            self.current_time = self.film.duration
            
        self.update_time_display()
    
    def goto_time(self):
        """Belirtilen zamana gider"""
        if not self.film:
            messagebox.showerror("Hata", "Önce bir film oluşturmalısınız!")
            return
            
        time_str = self.goto_time_var.get()
        try:
            # hh:mm:ss formatını saniyeye çevir
            h, m, s = map(int, time_str.split(':'))
            seconds = h * 3600 + m * 60 + s
            
            if 0 <= seconds <= self.film.duration:
                self.current_time = seconds
                self.update_time_display()
            else:
                messagebox.showerror("Hata", f"Zaman film süresinin dışında! (0-{format_time(self.film.duration)})")
        except:
            messagebox.showerror("Hata", "Geçersiz zaman formatı! hh:mm:ss kullanın.")
    
    def update_time_display(self):
        """Zaman göstergesini günceller"""
        self.current_time_label.config(text=format_time(self.current_time))
    
    # Karakter sekmesi
    def setup_character_tab(self):
        """Karakter sekmesini hazırlar"""
        # Sol panel - karakter listesi
        left_frame = ttk.Frame(self.character_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(left_frame, text="Karakterler:").pack(anchor=tk.W)
        
        self.character_listbox = tk.Listbox(left_frame, height=15)
        self.character_listbox.pack(fill=tk.BOTH, expand=True)
        self.character_listbox.bind('<<ListboxSelect>>', self.on_character_select)
        
        # Sağ panel - karakter detayları
        right_frame = ttk.Frame(self.character_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(right_frame, text="Karakter Adı:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.character_name_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.character_name_var, width=30).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(right_frame, text="Karakter Türü:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.character_type_var = tk.StringVar()
        ttk.Combobox(right_frame, textvariable=self.character_type_var, values=["protagonist", "antagonist", "supporting", "minor"]).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(right_frame, text="Önem (1-10):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.character_importance_var = tk.IntVar(value=5)
        ttk.Spinbox(right_frame, from_=1, to=10, textvariable=self.character_importance_var, width=5).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(right_frame, text="Karakter Özellikleri:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.character_traits_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.character_traits_var, width=30).grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Label(right_frame, text="(virgülle ayırın)").grid(row=3, column=2, padx=5, pady=5, sticky=tk.W)
        
        # Butonlar
        button_frame = ttk.Frame(right_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Ekle", command=self.add_character).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Güncelle", command=self.update_character).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Sil", command=self.delete_character).pack(side=tk.LEFT, padx=5)
    
    def refresh_character_list(self):
        """Karakter listesini günceller"""
        self.character_listbox.delete(0, tk.END)
        
        if self.film and self.film.characters:
            for character in self.film.characters:
                self.character_listbox.insert(tk.END, character.name)
    
    def on_character_select(self, event):
        """Karakter seçildiğinde detayları gösterir"""
        if not self.film:
            return
            
        selection = self.character_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        if index < len(self.film.characters):
            character = self.film.characters[index]
            self.character_name_var.set(character.name)
            self.character_type_var.set(character.type)
            self.character_importance_var.set(character.importance)
            self.character_traits_var.set(", ".join(character.traits))
    
    def add_character(self):
        """Yeni karakter ekler"""
        if not self.film:
            messagebox.showerror("Hata", "Önce bir film oluşturmalısınız!")
            return
            
        name = self.character_name_var.get().strip()
        if not name:
            messagebox.showerror("Hata", "Karakter adı boş olamaz!")
            return
            
        # Aynı isimde karakter var mı kontrol et
        if any(c.name == name for c in self.film.characters):
            messagebox.showerror("Hata", f"'{name}' adında bir karakter zaten var!")
            return
            
        character_type = self.character_type_var.get()
        importance = self.character_importance_var.get()
        traits_str = self.character_traits_var.get().strip()
        traits = [t.strip() for t in traits_str.split(",")] if traits_str else []
        
        character = self.film.add_character(Character(name, character_type))
        character.importance = importance
        character.traits = traits
        
        self.refresh_character_list()
        messagebox.showinfo("Bilgi", f"'{name}' karakteri eklendi.")
    
    def update_character(self):
        """Seçili karakteri günceller"""
        if not self.film:
            return
            
        selection = self.character_listbox.curselection()
        if not selection:
            messagebox.showerror("Hata", "Güncellenecek karakteri seçin!")
            return
            
        index = selection[0]
        if index < len(self.film.characters):
            character = self.film.characters[index]
            
            name = self.character_name_var.get().strip()
            if not name:
                messagebox.showerror("Hata", "Karakter adı boş olamaz!")
                return
                
            # İsim değişiyorsa ve aynı isimde başka karakter varsa kontrol et
            if name != character.name and any(c.name == name for c in self.film.characters):
                messagebox.showerror("Hata", f"'{name}' adında bir karakter zaten var!")
                return
                
            character.name = name
            character.type = self.character_type_var.get()
            character.importance = self.character_importance_var.get()
            
            traits_str = self.character_traits_var.get().strip()
            character.traits = [t.strip() for t in traits_str.split(",")] if traits_str else []
            
            self.refresh_character_list()
            messagebox.showinfo("Bilgi", f"'{name}' karakteri güncellendi.")
    
    def delete_character(self):
        """Seçili karakteri siler"""
        if not self.film:
            return
            
        selection = self.character_listbox.curselection()
        if not selection:
            messagebox.showerror("Hata", "Silinecek karakteri seçin!")
            return
            
        index = selection[0]
        if index < len(self.film.characters):
            character = self.film.characters[index]
            
            # Karakter başka yerlerde kullanılıyor mu kontrol et
            used_in_scenes = any(character in scene.characters for scene in self.film.scenes)
            used_in_relationships = any(character.name in [rel.character1.name, rel.character2.name] for rel in self.film.relationships)
            used_in_events = any(character in event.characters for event in self.film.events)
            
            if used_in_scenes or used_in_relationships or used_in_events:
                messagebox.showerror("Hata", f"'{character.name}' karakteri sahnelerde, ilişkilerde veya olaylarda kullanılıyor. Önce bunları güncelleyin.")
                return
                
            self.film.characters.remove(character)
            self.refresh_character_list()
            messagebox.showinfo("Bilgi", f"'{character.name}' karakteri silindi.")
    
    # Lokasyon sekmesi
    def setup_location_tab(self):
        """Lokasyon sekmesini hazırlar"""
        # Sol panel - lokasyon listesi
        left_frame = ttk.Frame(self.location_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(left_frame, text="Lokasyonlar:").pack(anchor=tk.W)
        
        self.location_listbox = tk.Listbox(left_frame, height=15)
        self.location_listbox.pack(fill=tk.BOTH, expand=True)
        self.location_listbox.bind('<<ListboxSelect>>', self.on_location_select)
        
        # Sağ panel - lokasyon detayları
        right_frame = ttk.Frame(self.location_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(right_frame, text="Lokasyon Adı:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.location_name_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.location_name_var, width=30).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(right_frame, text="Lokasyon Türü:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.location_type_var = tk.StringVar()
        ttk.Combobox(right_frame, textvariable=self.location_type_var, values=["indoor", "outdoor", "fictional", "real"]).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Butonlar
        button_frame = ttk.Frame(right_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Ekle", command=self.add_location).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Güncelle", command=self.update_location).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Sil", command=self.delete_location).pack(side=tk.LEFT, padx=5)
    
    def refresh_location_list(self):
        """Lokasyon listesini günceller"""
        self.location_listbox.delete(0, tk.END)
        
        if self.film and self.film.locations:
            for location in self.film.locations:
                self.location_listbox.insert(tk.END, location.name)
    
    def on_location_select(self, event):
        """Lokasyon seçildiğinde detayları gösterir"""
        if not self.film:
            return
            
        selection = self.location_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        if index < len(self.film.locations):
            location = self.film.locations[index]
            self.location_name_var.set(location.name)
            self.location_type_var.set(location.type)
    
    def add_location(self):
        """Yeni lokasyon ekler"""
        if not self.film:
            messagebox.showerror("Hata", "Önce bir film oluşturmalısınız!")
            return
            
        name = self.location_name_var.get().strip()
        if not name:
            messagebox.showerror("Hata", "Lokasyon adı boş olamaz!")
            return
            
        # Aynı isimde lokasyon var mı kontrol et
        if any(l.name == name for l in self.film.locations):
            messagebox.showerror("Hata", f"'{name}' adında bir lokasyon zaten var!")
            return
            
        location_type = self.location_type_var.get()
        
        self.film.add_location(Location(name, location_type))
        self.refresh_location_list()
        messagebox.showinfo("Bilgi", f"'{name}' lokasyonu eklendi.")
    
    def update_location(self):
        """Seçili lokasyonu günceller"""
        if not self.film:
            return
            
        selection = self.location_listbox.curselection()
        if not selection:
            messagebox.showerror("Hata", "Güncellenecek lokasyonu seçin!")
            return
            
        index = selection[0]
        if index < len(self.film.locations):
            location = self.film.locations[index]
            
            name = self.location_name_var.get().strip()
            if not name:
                messagebox.showerror("Hata", "Lokasyon adı boş olamaz!")
                return
                
            # İsim değişiyorsa ve aynı isimde başka lokasyon varsa kontrol et
            if name != location.name and any(l.name == name for l in self.film.locations):
                messagebox.showerror("Hata", f"'{name}' adında bir lokasyon zaten var!")
                return
                
            location.name = name
            location.type = self.location_type_var.get()
            
            self.refresh_location_list()
            messagebox.showinfo("Bilgi", f"'{name}' lokasyonu güncellendi.")
    
    def delete_location(self):
        """Seçili lokasyonu siler"""
        if not self.film:
            return
            
        selection = self.location_listbox.curselection()
        if not selection:
            messagebox.showerror("Hata", "Silinecek lokasyonu seçin!")
            return
            
        index = selection[0]
        if index < len(self.film.locations):
            location = self.film.locations[index]
            
            # Lokasyon başka yerlerde kullanılıyor mu kontrol et
            used_in_scenes = any(location.name == scene.location.name for scene in self.film.scenes)
            used_in_events = any(location.name == event.location.name for event in self.film.events)
            
            if used_in_scenes or used_in_events:
                messagebox.showerror("Hata", f"'{location.name}' lokasyonu sahnelerde veya olaylarda kullanılıyor. Önce bunları güncelleyin.")
                return
                
            self.film.locations.remove(location)
            self.refresh_location_list()
            messagebox.showinfo("Bilgi", f"'{location.name}' lokasyonu silindi.")
    
    # Sahne sekmesi
    def setup_scene_tab(self):
        """Sahne sekmesini hazırlar"""
        # Sol panel - sahne listesi
        left_frame = ttk.Frame(self.scene_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(left_frame, text="Sahneler:").pack(anchor=tk.W)
        
        self.scene_listbox = tk.Listbox(left_frame, height=15, width=50)
        self.scene_listbox.pack(fill=tk.BOTH, expand=True)
        self.scene_listbox.bind('<<ListboxSelect>>', self.on_scene_select)
        
        # Sağ panel - sahne detayları
        right_frame = ttk.Frame(self.scene_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Başlangıç zamanı
        ttk.Label(right_frame, text="Başlangıç Zamanı:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.scene_start_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.scene_start_var, width=10).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Button(right_frame, text="Şu anki zaman", command=lambda: self.scene_start_var.set(format_time(self.current_time))).grid(row=0, column=2, padx=5, pady=5)
        
        # Bitiş zamanı
        ttk.Label(right_frame, text="Bitiş Zamanı:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.scene_end_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.scene_end_var, width=10).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Button(right_frame, text="Şu anki zaman", command=lambda: self.scene_end_var.set(format_time(self.current_time))).grid(row=1, column=2, padx=5, pady=5)
        
        # Lokasyon
        ttk.Label(right_frame, text="Lokasyon:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.scene_location_var = tk.StringVar()
        self.scene_location_combo = ttk.Combobox(right_frame, textvariable=self.scene_location_var, width=20)
        self.scene_location_combo.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # Karakterler
        ttk.Label(right_frame, text="Karakterler:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.scene_characters_frame = ttk.Frame(right_frame)
        self.scene_characters_frame.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        self.scene_character_vars = []
        
        # Açıklama
        ttk.Label(right_frame, text="Açıklama:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.scene_description_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.scene_description_var, width=40).grid(row=4, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # Butonlar
        button_frame = ttk.Frame(right_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Ekle", command=self.add_scene).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Güncelle", command=self.update_scene).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Sil", command=self.delete_scene).pack(side=tk.LEFT, padx=5)
    
    def refresh_scene_list(self):
        """Sahne listesini günceller"""
        self.scene_listbox.delete(0, tk.END)
        
        if self.film and self.film.scenes:
            # Sahneleri başlangıç zamanına göre sırala
            sorted_scenes = sorted(self.film.scenes, key=lambda x: x.start_time)
            
            for scene in sorted_scenes:
                desc = scene.description[:30] + "..." if len(scene.description) > 30 else scene.description
                self.scene_listbox.insert(tk.END, f"{format_time(scene.start_time)} - {format_time(scene.end_time)}: {desc}")
        
        # Lokasyon combobox'ını güncelle
        self.scene_location_combo['values'] = [loc.name for loc in self.film.locations] if self.film else []
        
        # Karakter checkbutton'larını güncelle
        for widget in self.scene_characters_frame.winfo_children():
            widget.destroy()
        
        self.scene_character_vars = []
        if self.film and self.film.characters:
            for i, character in enumerate(self.film.characters):
                var = tk.BooleanVar(value=False)
                self.scene_character_vars.append((character, var))
                
                cb = ttk.Checkbutton(self.scene_characters_frame, text=character.name, variable=var)
                cb.grid(row=i//2, column=i%2, sticky=tk.W, padx=5)
    
    def on_scene_select(self, event):
        """Sahne seçildiğinde detayları gösterir"""
        if not self.film:
            return
            
        selection = self.scene_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        # Sahneleri başlangıç zamanına göre sırala
        sorted_scenes = sorted(self.film.scenes, key=lambda x: x.start_time)
        
        if index < len(sorted_scenes):
            scene = sorted_scenes[index]
            
            self.scene_start_var.set(format_time(scene.start_time))
            self.scene_end_var.set(format_time(scene.end_time))
            self.scene_location_var.set(scene.location.name)
            self.scene_description_var.set(scene.description)
            
            # Karakter checkbutton'larını güncelle
            for character, var in self.scene_character_vars:
                var.set(character in scene.characters)
    
    def add_scene(self):
        """Yeni sahne ekler"""
        if not self.film:
            messagebox.showerror("Hata", "Önce bir film oluşturmalısınız!")
            return
            
        # Zamanları kontrol et
        try:
            start_time_str = self.scene_start_var.get()
            h, m, s = map(int, start_time_str.split(':'))
            start_time = h * 3600 + m * 60 + s
            
            end_time_str = self.scene_end_var.get()
            h, m, s = map(int, end_time_str.split(':'))
            end_time = h * 3600 + m * 60 + s
            
            if start_time >= end_time:
                messagebox.showerror("Hata", "Başlangıç zamanı bitiş zamanından önce olmalıdır!")
                return
                
            if end_time > self.film.duration:
                messagebox.showerror("Hata", f"Bitiş zamanı film süresinden ({format_time(self.film.duration)}) büyük olamaz!")
                return
        except:
            messagebox.showerror("Hata", "Geçersiz zaman formatı! hh:mm:ss kullanın.")
            return
        
        # Lokasyonu kontrol et
        location_name = self.scene_location_var.get()
        location = next((loc for loc in self.film.locations if loc.name == location_name), None)
        if not location:
            messagebox.showerror("Hata", "Geçerli bir lokasyon seçin!")
            return
        
        # Karakterleri al
        selected_characters = [char for char, var in self.scene_character_vars if var.get()]
        
        # Açıklamayı kontrol et
        description = self.scene_description_var.get().strip()
        if not description:
            messagebox.showerror("Hata", "Sahne açıklaması boş olamaz!")
            return
        
        # Sahneyi ekle
        # Burada doğrudan Film sınıfındaki add_scene metodunu kullanıyoruz
        self.film.add_scene(start_time, end_time, location, selected_characters, description)
        
        self.refresh_scene_list()
        messagebox.showinfo("Bilgi", "Sahne eklendi.")
    
    def update_scene(self):
        """Seçili sahneyi günceller"""
        if not self.film:
            return
            
        selection = self.scene_listbox.curselection()
        if not selection:
            messagebox.showerror("Hata", "Güncellenecek sahneyi seçin!")
            return
            
        index = selection[0]
        # Sahneleri başlangıç zamanına göre sırala
        sorted_scenes = sorted(self.film.scenes, key=lambda x: x.start_time)
        
        if index < len(sorted_scenes):
            scene = sorted_scenes[index]
            
            # Zamanları kontrol et
            try:
                start_time_str = self.scene_start_var.get()
                h, m, s = map(int, start_time_str.split(':'))
                start_time = h * 3600 + m * 60 + s
                
                end_time_str = self.scene_end_var.get()
                h, m, s = map(int, end_time_str.split(':'))
                end_time = h * 3600 + m * 60 + s
                
                if start_time >= end_time:
                    messagebox.showerror("Başlangıç zamanı bitiş zamanından önce olmalıdır!") 
                    messagebox.showerror("Başlangıç zamanı bitiş zamanından önce olmalıdır!")
                    return
                    
                if end_time > self.film.duration:
                    messagebox.showerror("Hata", f"Bitiş zamanı film süresinden ({format_time(self.film.duration)}) büyük olamaz!")
                    return
            except:
                messagebox.showerror("Hata", "Geçersiz zaman formatı! hh:mm:ss kullanın.")
                return
            
            # Lokasyonu kontrol et
            location_name = self.scene_location_var.get()
            location = next((loc for loc in self.film.locations if loc.name == location_name), None)
            if not location:
                messagebox.showerror("Hata", "Geçerli bir lokasyon seçin!")
                return
            
            # Karakterleri al
            selected_characters = [char for char, var in self.scene_character_vars if var.get()]
            
            # Açıklamayı kontrol et
            description = self.scene_description_var.get().strip()
            if not description:
                messagebox.showerror("Hata", "Sahne açıklaması boş olamaz!")
                return
            
            # Sahneyi güncelle
            scene.start_time = start_time
            scene.end_time = end_time
            scene.location = location
            scene.characters = selected_characters
            scene.description = description
            
            self.refresh_scene_list()
            messagebox.showinfo("Bilgi", "Sahne güncellendi.")
    
    def delete_scene(self):
        """Seçili sahneyi siler"""
        if not self.film:
            return
            
        selection = self.scene_listbox.curselection()
        if not selection:
            messagebox.showerror("Hata", "Silinecek sahneyi seçin!")
            return
            
        index = selection[0]
        # Sahneleri başlangıç zamanına göre sırala
        sorted_scenes = sorted(self.film.scenes, key=lambda x: x.start_time)
        
        if index < len(sorted_scenes):
            scene = sorted_scenes[index]
            self.film.scenes.remove(scene)
            
            self.refresh_scene_list()
            messagebox.showinfo("Bilgi", "Sahne silindi.")
    
    # İlişki sekmesi
    def setup_relationship_tab(self):
        """İlişki sekmesini hazırlar"""
        # Sol panel - ilişki listesi
        left_frame = ttk.Frame(self.relationship_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(left_frame, text="İlişkiler:").pack(anchor=tk.W)
        
        self.relationship_listbox = tk.Listbox(left_frame, height=15, width=50)
        self.relationship_listbox.pack(fill=tk.BOTH, expand=True)
        self.relationship_listbox.bind('<<ListboxSelect>>', self.on_relationship_select)
        
        # Sağ panel - ilişki detayları
        right_frame = ttk.Frame(self.relationship_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Karakter 1
        ttk.Label(right_frame, text="Karakter 1:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.relationship_char1_var = tk.StringVar()
        self.relationship_char1_combo = ttk.Combobox(right_frame, textvariable=self.relationship_char1_var, width=20)
        self.relationship_char1_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Karakter 2
        ttk.Label(right_frame, text="Karakter 2:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.relationship_char2_var = tk.StringVar()
        self.relationship_char2_combo = ttk.Combobox(right_frame, textvariable=self.relationship_char2_var, width=20)
        self.relationship_char2_combo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # İlişki türü
        ttk.Label(right_frame, text="İlişki Türü:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.relationship_type_var = tk.StringVar()
        ttk.Combobox(right_frame, textvariable=self.relationship_type_var, 
                    values=["friend", "enemy", "family", "romantic", "professional", "mentor"]).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Başlangıç zamanı
        ttk.Label(right_frame, text="Başlangıç Zamanı:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.relationship_start_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.relationship_start_var, width=10).grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Button(right_frame, text="Şu anki zaman", command=lambda: self.relationship_start_var.set(format_time(self.current_time))).grid(row=3, column=2, padx=5, pady=5)
        
        # Bitiş zamanı
        ttk.Label(right_frame, text="Bitiş Zamanı (opsiyonel):").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.relationship_end_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.relationship_end_var, width=10).grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Button(right_frame, text="Şu anki zaman", command=lambda: self.relationship_end_var.set(format_time(self.current_time))).grid(row=4, column=2, padx=5, pady=5)
        
        # İlişki gücü
        ttk.Label(right_frame, text="İlişki Gücü (1-10):").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        self.relationship_strength_var = tk.IntVar(value=5)
        ttk.Spinbox(right_frame, from_=1, to=10, textvariable=self.relationship_strength_var, width=5).grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Butonlar
        button_frame = ttk.Frame(right_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Ekle", command=self.add_relationship).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Güncelle", command=self.update_relationship).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Sil", command=self.delete_relationship).pack(side=tk.LEFT, padx=5)
    
    def refresh_relationship_list(self):
        """İlişki listesini günceller"""
        self.relationship_listbox.delete(0, tk.END)
        
        if self.film and self.film.relationships:
            for rel in self.film.relationships:
                end_time = f" - {format_time(rel.end_time)}" if rel.end_time is not None else ""
                self.relationship_listbox.insert(tk.END, f"{rel.character1.name} - {rel.character2.name} ({rel.type}) {format_time(rel.start_time)}{end_time}")
        
        # Karakter combobox'larını güncelle
        char_names = [char.name for char in self.film.characters] if self.film else []
        self.relationship_char1_combo['values'] = char_names
        self.relationship_char2_combo['values'] = char_names
    
    def on_relationship_select(self, event):
        """İlişki seçildiğinde detayları gösterir"""
        if not self.film:
            return
            
        selection = self.relationship_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        if index < len(self.film.relationships):
            rel = self.film.relationships[index]
            
            self.relationship_char1_var.set(rel.character1.name)
            self.relationship_char2_var.set(rel.character2.name)
            self.relationship_type_var.set(rel.type)
            self.relationship_start_var.set(format_time(rel.start_time))
            self.relationship_end_var.set(format_time(rel.end_time) if rel.end_time is not None else "")
            self.relationship_strength_var.set(rel.strength)
    
    def add_relationship(self):
        """Yeni ilişki ekler"""
        if not self.film:
            messagebox.showerror("Hata", "Önce bir film oluşturmalısınız!")
            return
            
        # Karakterleri kontrol et
        char1_name = self.relationship_char1_var.get()
        char2_name = self.relationship_char2_var.get()
        
        if char1_name == char2_name:
            messagebox.showerror("Hata", "İki farklı karakter seçmelisiniz!")
            return
            
        char1 = next((c for c in self.film.characters if c.name == char1_name), None)
        char2 = next((c for c in self.film.characters if c.name == char2_name), None)
        
        if not char1 or not char2:
            messagebox.showerror("Hata", "Geçerli karakterler seçin!")
            return
        
        # İlişki türünü kontrol et
        rel_type = self.relationship_type_var.get()
        if not rel_type:
            messagebox.showerror("Hata", "İlişki türü seçin!")
            return
        
        # Zamanları kontrol et
        try:
            start_time_str = self.relationship_start_var.get()
            h, m, s = map(int, start_time_str.split(':'))
            start_time = h * 3600 + m * 60 + s
            
            end_time = None
            end_time_str = self.relationship_end_var.get().strip()
            if end_time_str:
                h, m, s = map(int, end_time_str.split(':'))
                end_time = h * 3600 + m * 60 + s
                
                if start_time >= end_time:
                    messagebox.showerror("Hata", "Başlangıç zamanı bitiş zamanından önce olmalıdır!")
                    return
                    
                if end_time > self.film.duration:
                    messagebox.showerror("Hata", f"Bitiş zamanı film süresinden ({format_time(self.film.duration)}) büyük olamaz!")
                    return
        except:
            messagebox.showerror("Hata", "Geçersiz zaman formatı! hh:mm:ss kullanın.")
            return
        
        # İlişki gücünü al
        strength = self.relationship_strength_var.get()
        
        # İlişkiyi ekle
        relationship = Relationship(char1, char2, rel_type, start_time, end_time, strength)
        self.film.add_relationship(relationship)
        
        self.refresh_relationship_list()
        messagebox.showinfo("Bilgi", f"{char1_name} ve {char2_name} arasında ilişki eklendi.")
    
    def update_relationship(self):
        """Seçili ilişkiyi günceller"""
        if not self.film:
            return
            
        selection = self.relationship_listbox.curselection()
        if not selection:
            messagebox.showerror("Hata", "Güncellenecek ilişkiyi seçin!")
            return
            
        index = selection[0]
        if index < len(self.film.relationships):
            rel = self.film.relationships[index]
            
            # Karakterleri kontrol et
            char1_name = self.relationship_char1_var.get()
            char2_name = self.relationship_char2_var.get()
            
            if char1_name == char2_name:
                messagebox.showerror("Hata", "İki farklı karakter seçmelisiniz!")
                return
                
            char1 = next((c for c in self.film.characters if c.name == char1_name), None)
            char2 = next((c for c in self.film.characters if c.name == char2_name), None)
            
            if not char1 or not char2:
                messagebox.showerror("Hata", "Geçerli karakterler seçin!")
                return
            
            # İlişki türünü kontrol et
            rel_type = self.relationship_type_var.get()
            if not rel_type:
                messagebox.showerror("Hata", "İlişki türü seçin!")
                return
            
            # Zamanları kontrol et
            try:
                start_time_str = self.relationship_start_var.get()
                h, m, s = map(int, start_time_str.split(':'))
                start_time = h * 3600 + m * 60 + s
                
                end_time = None
                end_time_str = self.relationship_end_var.get().strip()
                if end_time_str:
                    h, m, s = map(int, end_time_str.split(':'))
                    end_time = h * 3600 + m * 60 + s
                    
                    if start_time >= end_time:
                        messagebox.showerror("Hata", "Başlangıç zamanı bitiş zamanından önce olmalıdır!")
                        return
                        
                    if end_time > self.film.duration:
                        messagebox.showerror("Hata", f"Bitiş zamanı film süresinden ({format_time(self.film.duration)}) büyük olamaz!")
                        return
            except:
                messagebox.showerror("Hata", "Geçersiz zaman formatı! hh:mm:ss kullanın.")
                return
            
            # İlişki gücünü al
            strength = self.relationship_strength_var.get()
            
            # İlişkiyi güncelle
            rel.character1 = char1
            rel.character2 = char2
            rel.type = rel_type
            rel.start_time = start_time
            rel.end_time = end_time
            rel.strength = strength
            
            self.refresh_relationship_list()
            messagebox.showinfo("Bilgi", "İlişki güncellendi.")
    
    def delete_relationship(self):
        """Seçili ilişkiyi siler"""
        if not self.film:
            return
            
        selection = self.relationship_listbox.curselection()
        if not selection:
            messagebox.showerror("Hata", "Silinecek ilişkiyi seçin!")
            return
            
        index = selection[0]
        if index < len(self.film.relationships):
            rel = self.film.relationships[index]
            self.film.relationships.remove(rel)
            
            self.refresh_relationship_list()
            messagebox.showinfo("Bilgi", "İlişki silindi.")
    
    # Olay sekmesi
    def setup_event_tab(self):
        """Olay sekmesini hazırlar"""
        # Sol panel - olay listesi
        left_frame = ttk.Frame(self.event_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(left_frame, text="Olaylar:").pack(anchor=tk.W)
        
        self.event_listbox = tk.Listbox(left_frame, height=15, width=50)
        self.event_listbox.pack(fill=tk.BOTH, expand=True)
        self.event_listbox.bind('<<ListboxSelect>>', self.on_event_select)
        
        # Sağ panel - olay detayları
        right_frame = ttk.Frame(self.event_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Olay adı
        ttk.Label(right_frame, text="Olay Adı:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.event_name_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.event_name_var, width=30).grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # Zaman
        ttk.Label(right_frame, text="Zaman:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.event_time_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.event_time_var, width=10).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Button(right_frame, text="Şu anki zaman", command=lambda: self.event_time_var.set(format_time(self.current_time))).grid(row=1, column=2, padx=5, pady=5)
        
        # Lokasyon
        ttk.Label(right_frame, text="Lokasyon:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.event_location_var = tk.StringVar()
        self.event_location_combo = ttk.Combobox(right_frame, textvariable=self.event_location_var, width=20)
        self.event_location_combo.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # Karakterler
        ttk.Label(right_frame, text="Karakterler:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.event_characters_frame = ttk.Frame(right_frame)
        self.event_characters_frame.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        self.event_character_vars = []
        
        # Önem
        ttk.Label(right_frame, text="Önem (1-10):").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.event_importance_var = tk.IntVar(value=5)
        ttk.Spinbox(right_frame, from_=1, to=10, textvariable=self.event_importance_var, width=5).grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Olay türü
        ttk.Label(right_frame, text="Olay Türü:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        self.event_type_var = tk.StringVar()
        ttk.Combobox(right_frame, textvariable=self.event_type_var, 
                    values=["plot point", "plot twist", "revelation", "action", "dialogue", "character development"]).grid(row=5, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # Butonlar
        button_frame = ttk.Frame(right_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Ekle", command=self.add_event).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Güncelle", command=self.update_event).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Sil", command=self.delete_event).pack(side=tk.LEFT, padx=5)
    
    def refresh_event_list(self):
        """Olay listesini günceller"""
        self.event_listbox.delete(0, tk.END)
        
        if self.film and self.film.events:
            # Olayları zamana göre sırala
            sorted_events = sorted(self.film.events, key=lambda x: x.time)
            
            for event in sorted_events:
                self.event_listbox.insert(tk.END, f"{format_time(event.time)}: {event.name} ({event.type})")
        
        # Lokasyon combobox'ını güncelle
        self.event_location_combo['values'] = [loc.name for loc in self.film.locations] if self.film else []
        
        # Karakter checkbutton'larını güncelle
        for widget in self.event_characters_frame.winfo_children():
            widget.destroy()
        
        self.event_character_vars = []
        if self.film and self.film.characters:
            for i, character in enumerate(self.film.characters):
                var = tk.BooleanVar(value=False)
                self.event_character_vars.append((character, var))
                
                cb = ttk.Checkbutton(self.event_characters_frame, text=character.name, variable=var)
                cb.grid(row=i//2, column=i%2, sticky=tk.W, padx=5)
    
    def on_event_select(self, event):
        """Olay seçildiğinde detayları gösterir"""
        if not self.film:
            return
            
        selection = self.event_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        # Olayları zamana göre sırala
        sorted_events = sorted(self.film.events, key=lambda x: x.time)
        
        if index < len(sorted_events):
            event = sorted_events[index]
            
            self.event_name_var.set(event.name)
            self.event_time_var.set(format_time(event.time))
            self.event_location_var.set(event.location.name)
            self.event_importance_var.set(event.importance)
            self.event_type_var.set(event.type)
            
            # Karakter checkbutton'larını güncelle
            for character, var in self.event_character_vars:
                var.set(character in event.characters)
    
    def add_event(self):
        """Yeni olay ekler"""
        if not self.film:
            messagebox.showerror("Hata", "Önce bir film oluşturmalısınız!")
            return
            
        # Olay adını kontrol et
        name = self.event_name_var.get().strip()
        if not name:
            messagebox.showerror("Hata", "Olay adı boş olamaz!")
            return
        
        # Zamanı kontrol et
        try:
            time_str = self.event_time_var.get()
            h, m, s = map(int, time_str.split(':'))
            time = h * 3600 + m * 60 + s
            
            if time > self.film.duration:
                messagebox.showerror("Hata", f"Zaman film süresinden ({format_time(self.film.duration)}) büyük olamaz!")
                return
        except:
            messagebox.showerror("Hata", "Geçersiz zaman formatı! hh:mm:ss kullanın.")
            return
        
        # Lokasyonu kontrol et
        location_name = self.event_location_var.get()
        location = next((loc for loc in self.film.locations if loc.name == location_name), None)
        if not location:
            messagebox.showerror("Hata", "Geçerli bir lokasyon seçin!")
            return
        
        # Karakterleri al
        selected_characters = [char for char, var in self.event_character_vars if var.get()]
        
        # Önem ve türü al
        importance = self.event_importance_var.get()
        event_type = self.event_type_var.get()
        if not event_type:
            messagebox.showerror("Hata", "Olay türü seçin!")
            return
        
        # Olayı ekle
        event = Event(name, time, location, selected_characters, importance, event_type)
        self.film.add_event(event)
        
        self.refresh_event_list()
        messagebox.showinfo("Bilgi", f"'{name}' olayı eklendi.")
    
    def update_event(self):
        """Seçili olayı günceller"""
        if not self.film:
            return
            
        selection = self.event_listbox.curselection()
        if not selection:
            messagebox.showerror("Hata", "Güncellenecek olayı seçin!")
            return
            
        index = selection[0]
        # Olayları zamana göre sırala
        sorted_events = sorted(self.film.events, key=lambda x: x.time)
        
        if index < len(sorted_events):
            event = sorted_events[index]
            
            # Olay adını kontrol et
            name = self.event_name_var.get().strip()
            if not name:
                messagebox.showerror("Hata", "Olay adı boş olamaz!")
                return
            
            # Zamanı kontrol et
            try:
                time_str = self.event_time_var.get()
                h, m, s = map(int, time_str.split(':'))
                time = h * 3600 + m * 60 + s
                
                if time > self.film.duration:
                    messagebox.showerror("Hata", f"Zaman film süresinden ({format_time(self.film.duration)}) büyük olamaz!")
                    return
            except:
                messagebox.showerror("Hata", "Geçersiz zaman formatı! hh:mm:ss kullanın.")
                return
            
            # Lokasyonu kontrol et
            location_name = self.event_location_var.get()
            location = next((loc for loc in self.film.locations if loc.name == location_name), None)
            if not location:
                messagebox.showerror("Hata", "Geçerli bir lokasyon seçin!")
                return
            
            # Karakterleri al
            selected_characters = [char for char, var in self.event_character_vars if var.get()]
            
            # Önem ve türü al
            importance = self.event_importance_var.get()
            event_type = self.event_type_var.get()
            if not event_type:
                messagebox.showerror("Hata", "Olay türü seçin!")
                return
            
            # Olayı güncelle
            event.name = name
            event.time = time
            event.location = location
            event.characters = selected_characters
            event.importance = importance
            event.type = event_type
            
            self.refresh_event_list()
            messagebox.showinfo("Bilgi", f"'{name}' olayı güncellendi.")
    
    def delete_event(self):
        """Seçili olayı siler"""
        if not self.film:
            return
            
        selection = self.event_listbox.curselection()
        if not selection:
            messagebox.showerror("Hata", "Silinecek olayı seçin!")
            return
            
        index = selection[0]
        # Olayları zamana göre sırala
        sorted_events = sorted(self.film.events, key=lambda x: x.time)
        
        if index < len(sorted_events):
            event = sorted_events[index]
            self.film.events.remove(event)
            
            self.refresh_event_list()
            messagebox.showinfo("Bilgi", f"'{event.name}' olayı silindi.")

# Ana uygulama
if __name__ == "__main__":
    root = tk.Tk()
    app = FilmDataCollector(root)
    root.mainloop()