import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import os
import webbrowser
from datetime import datetime

# Tentar importar folium
try:
    import folium
    from folium.plugins import HeatMap
    MAP_AVAILABLE = True
except ImportError:
    MAP_AVAILABLE = False

class MapTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='#0a0a1a')
        self.app = app
        self.ip_locations = {}
        self.map_file = os.path.expanduser("~/.ai-security-suite/blocked_ips_map.html")
        os.makedirs(os.path.dirname(self.map_file), exist_ok=True)
        self.setup_ui()
        
        if MAP_AVAILABLE:
            self.update_map()
            self.start_auto_update()
        else:
            self.show_install_instructions()
        
    def setup_ui(self):
        # Título "IPS BLOQUEADOS" no topo
        title_frame = tk.Frame(self, bg='#0a0a1a')
        title_frame.pack(fill='x', pady=10, padx=30)
        tk.Label(title_frame, text="🌍 IPS BLOQUEADOS", font=('Arial', 22, 'bold'),
                bg='#0a0a1a', fg='#ff4444').pack()
        
        # Frame do mapa
        map_frame = tk.Frame(self, bg='#16213e', relief='ridge', bd=2)
        map_frame.pack(fill='both', expand=True, padx=30, pady=10)
        
        # Label para exibir informações do mapa
        self.map_info = tk.Text(map_frame, bg='#0a0a1a', fg='#00ff88', 
                                 font=('Courier', 11), wrap='word', height=15)
        self.map_info.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Botões
        btn_frame = tk.Frame(map_frame, bg='#16213e')
        btn_frame.pack(pady=10)
        
        self.update_btn = tk.Button(btn_frame, text="🔄 ATUALIZAR MAPA", command=self.update_map,
                 bg='#0f3460', fg='white', font=('Arial', 11, 'bold'), padx=20, pady=8, cursor='hand2')
        self.update_btn.pack(side='left', padx=10)
        
        self.open_btn = tk.Button(btn_frame, text="🗺️ ABRIR MAPA NO NAVEGADOR", command=self.open_map,
                 bg='#00ff88', fg='#0a0a1a', font=('Arial', 11, 'bold'), padx=20, pady=8, cursor='hand2')
        self.open_btn.pack(side='left', padx=10)
        
        # Status
        self.status_label = tk.Label(map_frame, text="", bg='#16213e', fg='#888', font=('Arial', 9))
        self.status_label.pack(pady=5)
        
        # Lista de IPs
        list_frame = tk.LabelFrame(self, text="📋 LISTA DE IPS BLOQUEADOS", bg='#16213e', fg='#ff4444', font=('Arial', 11, 'bold'))
        list_frame.pack(fill='x', padx=30, pady=10)
        
        list_container = tk.Frame(list_frame, bg='#16213e')
        list_container.pack(fill='x', padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(list_container)
        scrollbar.pack(side='right', fill='y')
        
        self.ip_listbox = tk.Listbox(list_container, bg='#0a0a1a', fg='#ff8888', 
                                      font=('Courier', 10), height=5,
                                      yscrollcommand=scrollbar.set)
        self.ip_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.ip_listbox.yview)
        
        self.update_ip_list()
        
    def show_install_instructions(self):
        """Mostra instruções quando o mapa não está disponível"""
        self.map_info.delete('1.0', 'end')
        self.map_info.insert('1.0', """
╔══════════════════════════════════════════════════════════════╗
║                    ⚠️ MAPA NÃO DISPONÍVEL ⚠️                  ║
╚══════════════════════════════════════════════════════════════╝

Para ativar o mapa mundial, instale no terminal:

    pip3 install folium geopy

Depois reinicie o programa.

────────────────────────────────────────────────────────────────

✅ Funcionalidades disponíveis:
   • Lista de IPs bloqueados
   • Estatísticas de bloqueios
   • Informações de localização

────────────────────────────────────────────────────────────────

💡 Após instalar, clique em "ATUALIZAR MAPA" e depois em "ABRIR NO NAVEGADOR"
        """)
        self.update_btn.config(state='disabled')
        self.open_btn.config(state='disabled')
        
    def get_ip_location(self, ip):
        """Obtém localização do IP via API"""
        if ip in self.ip_locations:
            return self.ip_locations[ip]
        
        try:
            import urllib.request
            import json
            url = f"http://ip-api.com/json/{ip}"
            response = urllib.request.urlopen(url, timeout=5)
            data = json.loads(response.read().decode())
            
            if data.get('status') == 'success':
                location = {
                    'lat': data.get('lat', 0),
                    'lon': data.get('lon', 0),
                    'country': data.get('country', 'Desconhecido'),
                    'city': data.get('city', 'Desconhecida'),
                    'isp': data.get('isp', 'Desconhecido'),
                    'countryCode': data.get('countryCode', '')
                }
                self.ip_locations[ip] = location
                return location
        except Exception as e:
            print(f"Erro ao geolocalizar {ip}: {e}")
        
        return None
    
    def create_map(self):
        """Cria o mapa HTML"""
        if not MAP_AVAILABLE:
            return None
            
        blocked_ips = self.app.defense_engine.get_blocked_ips() if self.app.defense_engine else []
        
        if not blocked_ips:
            self.map_info.delete('1.0', 'end')
            self.map_info.insert('1.0', "📊 Nenhum IP bloqueado ainda.\n\nAguardando a defesa detectar e bloquear ameaças...")
            self.status_label.config(text="Nenhum IP bloqueado", fg='#ffaa00')
            return None
        
        self.status_label.config(text=f"Gerando mapa para {len(blocked_ips)} IPs...", fg='#00ff88')
        
        # Criar mapa
        world_map = folium.Map(location=[20, 0], zoom_start=2, tiles='CartoDB positron')
        
        # Adicionar título
        title_html = '<h3 align="center" style="font-size:14px; color:#00ff88;">🌍 IPs Bloqueados pelo AI Security Suite</h3>'
        world_map.get_root().html.add_child(folium.Element(title_html))
        
        countries = set()
        locations = []
        
        for ip in blocked_ips:
            location = self.get_ip_location(ip)
            if location and location.get('lat') and location.get('lon'):
                countries.add(location.get('country', 'Desconhecido'))
                locations.append([location['lat'], location['lon']])
                
                # Cor do marcador
                country_code = location.get('countryCode', '')
                if country_code in ['RU', 'CN', 'KP', 'IR']:
                    color = 'red'
                elif country_code in ['US', 'GB', 'DE']:
                    color = 'blue'
                else:
                    color = 'orange'
                
                popup_text = f"""
                <div style="font-family:Arial; font-size:12px;">
                    <b>🖥️ IP:</b> {ip}<br>
                    <b>📍 País:</b> {location.get('country', 'Desconhecido')}<br>
                    <b>🏙️ Cidade:</b> {location.get('city', 'Desconhecida')}<br>
                    <b>🏢 ISP:</b> {location.get('isp', 'Desconhecido')}
                </div>
                """
                
                folium.Marker(
                    location=[location['lat'], location['lon']],
                    popup=folium.Popup(popup_text, max_width=300),
                    icon=folium.Icon(color=color, icon='info-sign', prefix='glyphicon'),
                    tooltip=f"{ip} - {location.get('country', 'Desconhecido')}"
                ).add_to(world_map)
        
        # Adicionar heatmap se houver muitos IPs
        if len(locations) >= 3:
            HeatMap(locations, radius=25, blur=15, min_opacity=0.5).add_to(world_map)
        
        # Salvar mapa
        world_map.save(self.map_file)
        
        # Mostrar informações no texto
        self.map_info.delete('1.0', 'end')
        self.map_info.insert('1.0', f"""
╔══════════════════════════════════════════════════════════════╗
║                    ✅ MAPA GERADO COM SUCESSO!               ║
╚══════════════════════════════════════════════════════════════╝

📊 ESTATÍSTICAS:
   • Total de IPs bloqueados: {len(blocked_ips)}
   • Países atingidos: {len(countries)}
   • Marcadores no mapa: {len(locations)}

🌍 Clique em "ABRIR MAPA NO NAVEGADOR" para visualizar o mapa.

📍 Cada marcador representa um invasor bloqueado.
   Clique nos marcadores para ver detalhes do IP.

📁 Arquivo do mapa: {self.map_file}
        """)
        
        self.status_label.config(text=f"Mapa gerado! {len(blocked_ips)} IPs, {len(countries)} países", fg='#00ff88')
        self.open_btn.config(state='normal')
        
        return self.map_file
    
    def open_map(self):
        """Abre o mapa no navegador"""
        if not MAP_AVAILABLE:
            messagebox.showerror("Erro", "Folium não instalado. Execute: pip3 install folium geopy")
            return
            
        if os.path.exists(self.map_file):
            webbrowser.open(f'file://{self.map_file}')
            self.app.logs_tab.add_log("🌍 Mapa aberto no navegador", "info")
        else:
            messagebox.showinfo("Info", "Clique em 'ATUALIZAR MAPA' primeiro.")
    
    def update_map(self):
        """Atualiza o mapa"""
        if not MAP_AVAILABLE:
            messagebox.showerror("Erro", "Instale folium: pip3 install folium geopy")
            return
            
        def run():
            self.create_map()
            self.update_ip_list()
            self.app.logs_tab.add_log("🗺️ Mapa atualizado", "info")
        threading.Thread(target=run, daemon=True).start()
    
    def update_ip_list(self):
        """Atualiza a lista de IPs bloqueados"""
        self.ip_listbox.delete(0, 'end')
        blocked_ips = self.app.defense_engine.get_blocked_ips() if self.app.defense_engine else []
        
        if blocked_ips:
            for ip in blocked_ips:
                location = self.get_ip_location(ip)
                country = location.get('country', 'Desconhecido') if location else 'Desconhecido'
                self.ip_listbox.insert('end', f"{ip} - {country}")
        else:
            self.ip_listbox.insert('end', "Nenhum IP bloqueado ainda")
    
    def start_auto_update(self):
        """Atualização automática do mapa a cada 60 segundos"""
        def update_loop():
            while True:
                if self.winfo_exists():
                    self.update_map()
                time.sleep(60)
        threading.Thread(target=update_loop, daemon=True).start()
