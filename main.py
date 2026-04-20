import customtkinter as ctk
import json
import os
import requests
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- CONFIGURAÇÕES ---
URL_GITHUB = "https://raw.githubusercontent.com/WalterrLS/analisador-xps/refs/heads/main/meu_banco_xps.json"
ARQUIVO_LOCAL = "meu_banco_xps.json"

class XPSApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Simulador de Espectros XPS")
        self.geometry("1100x750")
        ctk.set_appearance_mode("dark")
        
        # Tenta carregar o ícone se ele existir
        try:
            self.iconbitmap("logo.ico")
        except:
            pass

        self.dados_elemento_atual = None

        if not os.path.exists(ARQUIVO_LOCAL):
            with open(ARQUIVO_LOCAL, 'w', encoding='utf-8') as f:
                json.dump({}, f)

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(self.sidebar, text="Ajustes de Simulação", font=("Arial", 18, "bold")).pack(pady=20)
        
        self.btn_sync = ctk.CTkButton(self.sidebar, text="Sincronizar Nuvem ↻", 
                                      fg_color="#28a745", hover_color="#218838",
                                      command=self.sincronizar_banco)
        self.btn_sync.pack(pady=(10, 5), padx=20)
        
        self.label_status_sync = ctk.CTkLabel(self.sidebar, text="Aguardando...", font=("Arial", 11, "italic"))
        self.label_status_sync.pack(pady=(0, 10))

        # Busca
        self.frame_busca = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.frame_busca.pack(pady=10, fill="x", padx=10)
        self.entry_elemento = ctk.CTkEntry(self.frame_busca, placeholder_text="Ex: Si", width=80)
        self.entry_elemento.pack(side="left", padx=5)
        self.btn_buscar = ctk.CTkButton(self.frame_busca, text="Listar", width=100, command=self.carregar_dados)
        self.btn_buscar.pack(side="left", padx=5)

        self.combo_orbitais = ctk.CTkComboBox(self.sidebar, values=["..."], command=self.ao_selecionar_orbital)
        self.combo_orbitais.pack(pady=10, fill="x", padx=20)

        # Sliders
        ctk.CTkLabel(self.sidebar, text="Ajuste de FWHM (eV)").pack(pady=(20, 0))
        self.label_fwhm_val = ctk.CTkLabel(self.sidebar, text="1.20", text_color="#3498db", font=("Arial", 12, "bold"))
        self.label_fwhm_val.pack()
        self.slider_fwhm = ctk.CTkSlider(self.sidebar, from_=0.1, to=4.0, command=self.atualizar_fwhm)
        self.slider_fwhm.set(1.2)
        self.slider_fwhm.pack(pady=5, padx=20)

        # Slider de Ruído (Contagem para Poisson)
        ctk.CTkLabel(self.sidebar, text="Energia de Passagem (eV)").pack(pady=(15, 0))
        self.label_ruido_val = ctk.CTkLabel(self.sidebar, text="5.0", text_color="#e74c3c", font=("Arial", 12, "bold"))
        self.label_ruido_val.pack()
        self.slider_ruido = ctk.CTkSlider(self.sidebar, from_=0.1, to=50, command=self.atualizar_ruido)
        self.slider_ruido.set(5)
        self.slider_ruido.pack(pady=5, padx=20)

        # --- ÁREA DO GRÁFICO ---
        self.main_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=15)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=15)

    def atualizar_fwhm(self, valor):
        self.label_fwhm_val.configure(text=f"{valor:.2f}")
        self.replotar()

    def atualizar_ruido(self, valor):
        self.label_ruido_val.configure(text=f"{valor:.1f}")
        self.replotar()

    def sincronizar_banco(self):
        self.label_status_sync.configure(text="Sincronizando...", text_color="yellow")
        self.update_idletasks()
        try:
            r = requests.get(URL_GITHUB, timeout=8)
            if r.status_code == 200:
                with open(ARQUIVO_LOCAL, 'w', encoding='utf-8') as f:
                    json.dump(r.json(), f, indent=4)
                self.label_status_sync.configure(text="✔ Banco sincronizado", text_color="#28a745")
            else:
                self.label_status_sync.configure(text=f"✖ Erro HTTP: {r.status_code}", text_color="#dc3545")
        except:
            self.label_status_sync.configure(text="✖ Falha na internet", text_color="#dc3545")

    def carregar_dados(self):
        elem = self.entry_elemento.get().strip().upper()
        try:
            with open(ARQUIVO_LOCAL, 'r', encoding='utf-8') as f:
                banco = json.load(f)
            if elem in banco:
                orbitais = list(banco[elem]["orbitais"].keys())
                self.combo_orbitais.configure(values=orbitais)
                self.combo_orbitais.set(orbitais[0])
                self.ao_selecionar_orbital(orbitais[0])
            else:
                self.label_status_sync.configure(text=f"Elemento {elem} não existe", text_color="orange")
        except:
            self.label_status_sync.configure(text="Erro ao ler arquivo", text_color="red")

    def ao_selecionar_orbital(self, orbital_escolhido):
        elem = self.entry_elemento.get().strip().upper()
        try:
            with open(ARQUIVO_LOCAL, 'r', encoding='utf-8') as f:
                banco = json.load(f)
                self.dados_elemento_atual = banco[elem]["orbitais"][orbital_escolhido]
                self.dados_elemento_atual["nome"] = f"{elem} {orbital_escolhido}"
            self.replotar()
        except:
            pass

    def calcular_shirley(self, y):
        y = np.array(y)
        bg = np.linspace(y[0], y[-1], len(y))
        for _ in range(3):
            area_total = np.sum(y - bg)
            if area_total <= 0: break
            new_bg = np.zeros_like(y)
            for i in range(len(y)):
                area_parcial = np.sum(y[i:] - bg[i:])
                new_bg[i] = y[-1] + (y[0] - y[-1]) * (area_parcial / area_total)
            bg = new_bg
        return bg

    def replotar(self):
        if not self.dados_elemento_atual:
            return
        
        self.ax.clear()
        self.ax.set_facecolor('#ffffff')
        self.ax.grid(True, linestyle='--', alpha=0.3)

        be = self.dados_elemento_atual["be"]
        asf = self.dados_elemento_atual["asf"]
        fwhm = self.slider_fwhm.get()
        
        x = np.linspace(be + 10, be - 10, 400)
        sigma = fwhm / 2.3548
        
        # 1. Geração do Sinal Puro
        y_teorico_max = (asf * 1000)
        y_puro = y_teorico_max * np.exp(-(x - be)**2 / (2 * sigma**2))
        
        # 2. Estatística de Poisson (Shot Noise)
        # fator_intensidade simula o tempo de contagem (mais alto = menos ruído relativo)
        fator_intensidade = max(self.slider_ruido.get(), 0.1)
        y_final = np.random.poisson(np.maximum(y_puro, 0) * fator_intensidade) / fator_intensidade
        
        # 3. Tratamento Shirley
        bg = self.calcular_shirley(y_final)
        
        # Desenho do gráfico
        self.ax.fill_between(x, bg, y_final, color='#3498db', alpha=0.3, label="Área")
        self.ax.scatter(x, y_final, s=2, color='black', alpha=0.6, label="Sinal Simulado")
        self.ax.plot(x, bg, color='#e74c3c', lw=2, label="Fundo de Shirley")
        
        # Balão identificador
        y_pico_real = np.max(y_final)
        self.ax.annotate(f"{self.dados_elemento_atual['nome']}\n{be:.2f} eV", 
                         xy=(be, y_pico_real), 
                         xytext=(0, 15), 
                         textcoords="offset points",
                         ha='center', va='bottom',
                         fontsize=10, fontweight='bold', color='#2c3e50',
                         bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#3498db", alpha=0.9))

        self.ax.invert_xaxis()
        self.ax.set_title("Simulação do Espectro", pad=20, fontsize=14, fontweight='bold')
        self.ax.set_xlabel("Binding Energy (eV)")
        self.ax.set_ylabel("Intensity (counts)")
        self.ax.legend(fontsize='x-small', loc='upper right')
        
        self.canvas.draw_idle()

if __name__ == "__main__":
    app = XPSApp()
    app.mainloop()