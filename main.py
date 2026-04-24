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

class PeriodicTableWindow(ctk.CTkToplevel):
    def __init__(self, parent, banco_dados, callback_selecao):
        super().__init__(parent)
        self.title("Tabela Periódica - Selecione um Elemento")
        self.geometry("950x600")
        self.grab_set()
        
        self.banco_dados = banco_dados
        self.callback_selecao = callback_selecao

        for i in range(10): self.grid_rowconfigure(i, weight=1)
        for j in range(18): self.grid_columnconfigure(j, weight=1)

        self.renderizar_tabela()

    def renderizar_tabela(self):
        for simbolo, info in self.banco_dados.items():
            try:
                row, col = info["pos"]
                btn = ctk.CTkButton(
                    self, 
                    text=simbolo, 
                    width=48, height=48,
                    fg_color="#34495e",
                    hover_color="#3498db",
                    font=("Arial", 12, "bold"),
                    command=lambda s=simbolo: self.selecionar(s)
                )
                btn.grid(row=row, column=col, padx=2, pady=2)
            except:
                continue

    def selecionar(self, simbolo):
        self.callback_selecao(simbolo)
        self.destroy()

class XPSApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Simulador de Espectros XPS - v1.3")
        self.geometry("1150x800")
        ctk.set_appearance_mode("dark")
        
        self.banco_dados = {}
        self.dados_elemento_atual = None
        self.carregar_banco_local()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(self.sidebar, text="Ajustes de Simulação", font=("Arial", 20, "bold")).pack(pady=20)
        
        self.btn_abrir_tabela = ctk.CTkButton(
            self.sidebar, text="Selecionar Elemento ⊞", height=45,
            fg_color="#3498db", hover_color="#2980b9",
            font=("Arial", 14, "bold"), command=self.abrir_tabela
        )
        self.btn_abrir_tabela.pack(pady=10, padx=20, fill="x")

        self.label_elemento_sel = ctk.CTkLabel(self.sidebar, text="Nenhum elemento selecionado", font=("Arial", 13, "italic"))
        self.label_elemento_sel.pack(pady=5)

        ctk.CTkLabel(self.sidebar, text="Orbital:").pack(pady=(10, 0))
        self.combo_orbitais = ctk.CTkComboBox(self.sidebar, values=["..."], command=self.ao_selecionar_orbital)
        self.combo_orbitais.pack(pady=5, fill="x", padx=20)

        ctk.CTkFrame(self.sidebar, height=2, fg_color="#555").pack(fill="x", padx=20, pady=25)

        ctk.CTkLabel(self.sidebar, text="Largura do Pico [FWHM] (eV)").pack(pady=(5, 0))
        self.label_fwhm_val = ctk.CTkLabel(self.sidebar, text="1.20", text_color="#3498db", font=("Arial", 12, "bold"))
        self.label_fwhm_val.pack()
        self.slider_fwhm = ctk.CTkSlider(self.sidebar, from_=0.1, to=4.0, command=self.atualizar_fwhm)
        self.slider_fwhm.set(1.2)
        self.slider_fwhm.pack(pady=5, padx=20)

        ctk.CTkLabel(self.sidebar, text="Qualidade de Sinal (SNR)").pack(pady=(15, 0))
        self.label_ruido_val = ctk.CTkLabel(self.sidebar, text="5.0", text_color="#e74c3c", font=("Arial", 12, "bold"))
        self.label_ruido_val.pack()
        self.slider_ruido = ctk.CTkSlider(self.sidebar, from_=0.1, to=50, command=self.atualizar_ruido)
        self.slider_ruido.set(5)
        self.slider_ruido.pack(pady=5, padx=20)

        self.btn_sync = ctk.CTkButton(self.sidebar, text="Sincronizar Banco ↻", 
                                      fg_color="transparent", border_width=1,
                                      command=self.sincronizar_banco)
        self.btn_sync.pack(side="bottom", pady=20, padx=20)

        # --- ÁREA DO GRÁFICO ---
        self.main_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=15)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.fig, self.ax = plt.subplots(figsize=(6, 5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=15)

    # --- LÓGICA ---
    def carregar_banco_local(self):
        if os.path.exists(ARQUIVO_LOCAL):
            try:
                with open(ARQUIVO_LOCAL, 'r', encoding='utf-8') as f:
                    self.banco_dados = json.load(f)
            except: self.banco_dados = {}

    def abrir_tabela(self):
        if not self.banco_dados: self.sincronizar_banco()
        PeriodicTableWindow(self, self.banco_dados, self.processar_selecao_elemento)

    def processar_selecao_elemento(self, simbolo):
        self.label_elemento_sel.configure(text=f"Elemento: {simbolo}", font=("Arial", 13, "bold"))
        orbitais = list(self.banco_dados[simbolo]["orbitais"].keys())
        self.combo_orbitais.configure(values=orbitais)
        self.combo_orbitais.set(orbitais[0])
        self.ao_selecionar_orbital(orbitais[0], simbolo)

    def ao_selecionar_orbital(self, orbital_escolhido, simbolo=None):
        if not simbolo:
            simbolo = self.label_elemento_sel.cget("text").replace("Elemento: ", "")
        if simbolo in self.banco_dados:
            self.dados_elemento_atual = self.banco_dados[simbolo]["orbitais"][orbital_escolhido]
            self.dados_elemento_atual["nome_simbolo"] = simbolo
            self.dados_elemento_atual["tipo_orbital"] = orbital_escolhido
            self.replotar()

    def pseudo_voigt(self, x, be, fwhm, eta=0.3):
        sigma = fwhm / 2.3548
        gamma = fwhm / 2.0
        g = np.exp(-(x - be)**2 / (2 * sigma**2))
        l = (gamma**2) / ((x - be)**2 + gamma**2)
        return (1 - eta) * g + eta * l

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
        if not self.dados_elemento_atual: return
        
        self.ax.clear()
        self.ax.set_facecolor('#ffffff')
        self.ax.grid(True, linestyle='--', alpha=0.3)

        be_ref = self.dados_elemento_atual["be"]
        asf = self.dados_elemento_atual["asf"]
        split = self.dados_elemento_atual.get("split", 0)
        orbital_nome = self.dados_elemento_atual["tipo_orbital"].lower()
        fwhm = self.slider_fwhm.get()
        
        # --- LÓGICA FÍSICA DE SPIN-ORBIT ---
        # ratio = Intensidade(Pico Menor) / Intensidade(Pico Maior)
        ratio = 0
        suffix_principal = ""
        suffix_satelite = ""

        if 'p' in orbital_nome: 
            ratio = 0.5    # 1:2 (p1/2 : p3/2)
            suffix_principal = "3/2"
            suffix_satelite = "1/2"
        elif 'd' in orbital_nome: 
            ratio = 0.66   # 2:3 (d3/2 : d5/2)
            suffix_principal = "5/2"
            suffix_satelite = "3/2"
        elif 'f' in orbital_nome: 
            ratio = 0.75   # 3:4 (f5/2 : f7/2)
            suffix_principal = "7/2"
            suffix_satelite = "5/2"

        # No XPS, o componente com menor J (satélite) tem MAIOR Binding Energy
        be_principal = be_ref
        be_satelite = be_ref + split 

        margem = 8 + split
        x = np.linspace(be_principal + margem, be_principal - 10, 600)
        
        # Soma dos picos
        y_puro = (asf * 1000) * self.pseudo_voigt(x, be_principal, fwhm)
        if split > 0:
            y_puro += (asf * 1000 * ratio) * self.pseudo_voigt(x, be_satelite, fwhm)

        # Ruído e Fundo
        fator_ruido = max(self.slider_ruido.get(), 0.1)
        y_final = np.random.poisson(np.maximum(y_puro, 0) * fator_ruido) / fator_ruido
        bg = self.calcular_shirley(y_final)
        
        # Plotagem
        self.ax.fill_between(x, bg, y_final, color='#3498db', alpha=0.3)
        self.ax.scatter(x, y_final, s=2, color='black', alpha=0.6, label="Sinal Simulado")
        self.ax.plot(x, bg, color='#e74c3c', lw=2, label="Fundo Shirley")
        
        # Anotação no Pico Principal
        y_max = np.max(y_final)
        label_text = f"{self.dados_elemento_atual['nome_simbolo']} {orbital_nome}{suffix_principal}\n{be_principal:.2f} eV"
        
        self.ax.annotate(label_text, 
                         xy=(be_principal, (asf * 1000)), # Aponta para o topo teórico do principal
                         xytext=(0, 30), 
                         textcoords="offset points", ha='center',
                         bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="#3498db", alpha=0.9),
                         arrowprops=dict(arrowstyle="->", color="#3498db"))

        self.ax.invert_xaxis()
        self.ax.set_title(f"Simulação: {self.dados_elemento_atual['nome_simbolo']} {orbital_nome.upper()}", 
                          fontsize=14, fontweight='bold', pad=35)
        self.ax.set_xlabel("Binding Energy (eV)")
        self.ax.set_ylabel("Intensity (counts)")
        self.canvas.draw_idle()

    def atualizar_fwhm(self, valor):
        self.label_fwhm_val.configure(text=f"{valor:.2f}"); self.replotar()

    def atualizar_ruido(self, valor):
        self.label_ruido_val.configure(text=f"{valor:.1f}"); self.replotar()

    def sincronizar_banco(self):
        try:
            r = requests.get(URL_GITHUB, timeout=8)
            if r.status_code == 200:
                self.banco_dados = r.json()
                with open(ARQUIVO_LOCAL, 'w', encoding='utf-8') as f:
                    json.dump(self.banco_dados, f, indent=4)
        except: pass

if __name__ == "__main__":
    app = XPSApp()
    app.mainloop()