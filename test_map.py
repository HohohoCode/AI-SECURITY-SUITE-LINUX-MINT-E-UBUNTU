#!/usr/bin/env python3
import folium
from geopy.geocoders import Nominatim

print("Testando criação do mapa...")

# Criar mapa simples
m = folium.Map(location=[-15.7939, -47.8828], zoom_start=4)
folium.Marker([-15.7939, -47.8828], popup="Brasília").add_to(m)
m.save("/tmp/test_map.html")

print("✅ Mapa de teste criado em /tmp/test_map.html")
print("Abra no navegador: file:///tmp/test_map.html")
