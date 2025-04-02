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

# Film verilerini depolamak için sınıflar oluşturalım
class Film:
    def __init__(self, title, duration_minutes):
        self.title = title
        self.duration = duration_minutes
        self.characters = []
        self.locations = []
        self.scenes = []
        self.relationships = []
        self.events = []
        
    def add_character(self, character):
        self.characters.append(character)
        return character
        
    def add_location(self, location):
        self.locations.append(location)
        return location
        
    def add_scene(self, start_time, end_time, location, characters, description):
        scene = Scene(start_time, end_time, location, characters, description)
        self.scenes.append(scene)
        return scene
    
    def add_relationship(self, relationship):
        self.relationships.append(relationship)
        return relationship
    
    def add_event(self, event):
        self.events.append(event)
        return event
    
    def to_dict(self):
        return {
            "title": self.title,
            "duration": self.duration,
            "characters": [c.to_dict() for c in self.characters],
            "locations": [l.to_dict() for l in self.locations],
            "scenes": [s.to_dict() for s in self.scenes],
            "relationships": [r.to_dict() for r in self.relationships],
            "events": [e.to_dict() for e in self.events]
        }
    
    def save_to_json(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=4)
    
    @classmethod
    def load_from_json(cls, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        film = cls(data["title"], data["duration"])
        
        # Önce karakterleri ve lokasyonları yükle
        character_map = {}
        for char_data in data["characters"]:
            character = Character(char_data["name"], char_data["type"])
            character.importance = char_data["importance"]
            character.traits = char_data["traits"]
            film.characters.append(character)
            character_map[char_data["name"]] = character
            
        location_map = {}
        for loc_data in data["locations"]:
            location = Location(loc_data["name"], loc_data["type"])
            film.locations.append(location)
            location_map[loc_data["name"]] = location
        
        # Sonra sahneleri yükle
        for scene_data in data["scenes"]:
            characters = [character_map[name] for name in scene_data["character_names"]]
            location = location_map[scene_data["location_name"]]
            scene = Scene(
                scene_data["start_time"], 
                scene_data["end_time"],
                location,
                characters,
                scene_data["description"]
            )
            film.scenes.append(scene)
        
        # İlişkileri yükle
        for rel_data in data["relationships"]:
            char1 = character_map[rel_data["character1_name"]]
            char2 = character_map[rel_data["character2_name"]]
            relationship = Relationship(
                char1,
                char2,
                rel_data["type"],
                rel_data["start_time"],
                rel_data["end_time"] if "end_time" in rel_data else None,
                rel_data["strength"]
            )
            film.relationships.append(relationship)
        
        # Olayları yükle
        for event_data in data["events"]:
            characters = [character_map[name] for name in event_data["character_names"]]
            location = location_map[event_data["location_name"]]
            event = Event(
                event_data["name"],
                event_data["time"],
                location,
                characters,
                event_data["importance"],
                event_data["type"]
            )
            film.events.append(event)
            
        return film

class Character:
    def __init__(self, name, character_type):
        self.name = name
        self.type = character_type  # protagonist, antagonist, supporting, etc.
        self.importance = 0  # 1-10 scale
        self.traits = []  # character traits
        
    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "importance": self.importance,
            "traits": self.traits
        }

class Location:
    def __init__(self, name, location_type):
        self.name = name
        self.type = location_type  # indoor, outdoor, fictional, real, etc.
        
    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type
        }

class Scene:
    def __init__(self, start_time, end_time, location, characters, description):
        self.start_time = start_time  # in seconds from the beginning
        self.end_time = end_time  # in seconds from the beginning
        self.location = location
        self.characters = characters
        self.description = description
        
    def to_dict(self):
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "location_name": self.location.name,
            "character_names": [c.name for c in self.characters],
            "description": self.description
        }

class Relationship:
    def __init__(self, character1, character2, relationship_type, start_time, end_time=None, strength=5):
        self.character1 = character1
        self.character2 = character2
        self.type = relationship_type  # friend, enemy, family, etc.
        self.start_time = start_time  # when the relationship starts (in seconds)
        self.end_time = end_time  # when the relationship ends (in seconds), None if it doesn't end
        self.strength = strength  # 1-10 scale
        
    def to_dict(self):
        result = {
            "character1_name": self.character1.name,
            "character2_name": self.character2.name,
            "type": self.type,
            "start_time": self.start_time,
            "strength": self.strength
        }
        if self.end_time is not None:
            result["end_time"] = self.end_time
        return result

class Event:
    def __init__(self, name, time, location, characters, importance, event_type):
        self.name = name
        self.time = time  # in seconds from the beginning
        self.location = location
        self.characters = characters
        self.importance = importance  # 1-10 scale
        self.type = event_type  # plot twist, revelation, action, etc.
        
    def to_dict(self):
        return {
            "name": self.name,
            "time": self.time,
            "location_name": self.location.name,
            "character_names": [c.name for c in self.characters],
            "importance": self.importance,
            "type": self.type
        }

# Saniye cinsinden süreyi saat:dakika:saniye formatına dönüştürür
def format_time(seconds):
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

# Örnek bir film oluşturalım (bu kısmı kendi filminize göre değiştirmelisiniz)
if __name__ == "__main__":
    film = Film("Interstellar", 169 * 60)  # 169 dakika

    # Karakterler
    cooper = film.add_character(Character("Cooper", "protagonist"))
    cooper.importance = 10
    cooper.traits = ["determined", "intelligent", "loving father"]

    murph = film.add_character(Character("Murphy", "supporting"))
    murph.importance = 8
    murph.traits = ["curious", "intelligent", "persistent"]

    # Lokasyonlar
    earth = film.add_location(Location("Earth", "real"))
    spaceship = film.add_location(Location("Endurance", "fictional"))

    # Sahneler
    film.add_scene(300, 600, earth, [cooper, murph], "Cooper discovers NASA coordinates")

    # İlişkiler
    film.add_relationship(Relationship(cooper, murph, "family", 0, None, 10))

    # Önemli olaylar
    film.add_event(Event("Discovery of coordinates", 400, earth, [cooper, murph], 9, "plot point"))

    # Veriyi JSON olarak kaydet
    film.save_to_json("interstellar_data.json")

    print(f"Film: {film.title}")
    print(f"Süre: {format_time(film.duration)}")
    print(f"Karakter sayısı: {len(film.characters)}")
    print(f"Lokasyon sayısı: {len(film.locations)}")
    print(f"Sahne sayısı: {len(film.scenes)}")
    print(f"İlişki sayısı: {len(film.relationships)}")
    print(f"Olay sayısı: {len(film.events)}")