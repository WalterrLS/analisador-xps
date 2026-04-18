import customtkinter as ctk
import json
import os
import requests
import matplotlib.pyplot as plt
import numpy as np

# --- CONFIGURAÇÕES GLOBAIS ---
URL_GITHUB = "https://raw.githubusercontent.com/WalterrLS/analisador-xps/refs/heads/main/meu_banco_xps.json"
ARQUIVO_LOCAL = "meu_banco_xps.json"
  # --- INTERFACE GRÁFICA ---
class XPSApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração da Janela Principal
        self.title("Analisador de Dados XPS - Mês 1")
        self.geometry("500x550")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # --- Elementos da Interface ---
        self.label_titulo = ctk.CTkLabel(self, text="Consultoria de Referência XPS", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_titulo.pack(pady=20)

        #  Sincronização
        self.btn_sync = ctk.CTkButton(self, text="Sincronizar com GitHub", command=self.sincronizar_banco, fg_color="green", hover_color="darkgreen")
        self.btn_sync.pack(pady=10)

        self.status_label = ctk.CTkLabel(self, text="Banco Local detectado", text_color="gray")
        self.status_label.pack(pady=5)
        
        # Busca de Elemento
        self.label_busca = ctk.CTkLabel(self, text="1. Digite o Elemento (ex: Ti, Cu):")
        self.label_busca.pack(pady=(20, 0))
        
        self.entry_elemento = ctk.CTkEntry(self, placeholder_text="Símbolo...")
        self.entry_elemento.pack(pady=10)
        
        # Listagem de Orbitais
        self.btn_carregar = ctk.CTkButton(self, text="2. Listar Orbitais", command=self.carregar_orbitais_elemento, fg_color="#D48806", hover_color="#AA6D05")
        self.btn_carregar.pack(pady=5)

        self.label_orbital = ctk.CTkLabel(self, text="3. Selecione o Orbital:")
        self.label_orbital.pack(pady=(10, 0))

        self.combo_orbitais = ctk.CTkComboBox(self, values=["Busque um elemento..."], width=200)
        self.combo_orbitais.pack(pady=10)
        # --- FIM DOS ELEMENTOS DE INTERFACE ---
        #  Geração de Gráfico
        self.btn_plot = ctk.CTkButton(self, text="4. Gerar Gráfico de Referência", command=self.preparar_plot)
        self.btn_plot.pack(pady=20)

        # Rodapé
        self.label_footer = ctk.CTkLabel(self, text="Projeto Análise XPS - v1.0", font=ctk.CTkFont(size=10))
        self.label_footer.pack(side="bottom", pady=10)
        # --- FIM DA GERAÇÃO DE GRÁFICO ---
    # --- LÓGICA DE SINCRONIZAÇÃO ---
    def sincronizar_banco(self):
        try:
            response = requests.get(URL_GITHUB, timeout=10)
            if response.status_code == 200:
                with open(ARQUIVO_LOCAL, 'w', encoding='utf-8') as f:
                    json.dump(response.json(), f, indent=4)
                self.status_label.configure(text="[✔] Sincronizado com Sucesso!", text_color="lightgreen")
            else:
                self.status_label.configure(text=f"[!] Erro no GitHub (Status {response.status_code})", text_color="orange")
        except Exception as e:
            self.status_label.configure(text="[!] Falha na conexão", text_color="red")
    # --- FIM DA LÓGICA DE SINCRONIZAÇÃO --- 
    # --- LÓGICA PARA CARREGAR ORBITAIS NO MENU ---
    def carregar_orbitais_elemento(self):
        elemento = self.entry_elemento.get().strip().upper()
        
        if not os.path.exists(ARQUIVO_LOCAL):
            self.status_label.configure(text="[!] Sincronize o banco primeiro", text_color="red")
            return
        try:
            with open(ARQUIVO_LOCAL, 'r', encoding='utf-8') as f:
                banco = json.load(f)
            if elemento in banco:
                lista_orbitais = list(banco[elemento]["orbitais"].keys())
                self.combo_orbitais.configure(values=lista_orbitais)
                self.combo_orbitais.set(lista_orbitais[0]) 
                self.status_label.configure(text=f"[✔] Orbitais de {elemento} carregados", text_color="lightgreen")
            else:
                self.status_label.configure(text=f"[!] {elemento} não encontrado", text_color="orange")
        except Exception as e:
            self.status_label.configure(text="[!] Erro ao ler banco local", text_color="red")
      # --- FIM DA LÓGICA PARA CARREGAR ORBITAIS NO MENU ---
    # --- LÓGICA DE PREPARAÇÃO DO PLOT ---
    def preparar_plot(self):
        elemento = self.entry_elemento.get().strip().upper()
        orbital_selecionado = self.combo_orbitais.get()
        
        if not os.path.exists(ARQUIVO_LOCAL):
            self.status_label.configure(text="[!] Erro: Baixe o banco primeiro!", text_color="red")
            return

        with open(ARQUIVO_LOCAL, 'r', encoding='utf-8') as f:
            banco = json.load(f)

        if elemento in banco:
            if orbital_selecionado in banco[elemento]["orbitais"]:
                be = banco[elemento]["orbitais"][orbital_selecionado]
                self.mostrar_grafico_focado(elemento, orbital_selecionado, be)
            else:
                self.status_label.configure(text="[!] Selecione um orbital válido", text_color="orange")
        else:
            self.status_label.configure(text=f"[!] {elemento} não encontrado", text_color="orange")

    # --- FUNÇÃO DE GRÁFICO ---
    def mostrar_grafico_focado(self, elemento, orbital, be):
        plt.figure(f"XPS - {elemento} {orbital}", figsize=(8, 5))
        
        # Matemática da Simulação
        x = np.linspace(be - 5, be + 5, 1000)
        y = 100 * np.exp(-(x - be)**2 / (2 * 0.6**2))
        
        plt.plot(x, y, color='blue', lw=2, label=f"{elemento} {orbital}: {be} eV")
        plt.axvline(x=be, color='red', linestyle='--', alpha=0.7)
        
        # --- AJUSTE DO TEXTO ---
        plt.text(be + 1.5, 100, f'{be} eV',
                 color='red', 
                 ha='left',          
                 va='center',        
                 fontweight='bold',
                 fontsize=10,
                 bbox=dict(facecolor='white', alpha=0.5, edgecolor='none')) # Um fundinho branco para ler melhor
        
        plt.gca().invert_xaxis()
        plt.title(f"Padrão de Referência: {elemento} {orbital}")
        plt.xlabel("Binding Energy (eV)")
        plt.ylabel("Intensidade (u.a.)")
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.legend(loc='upper right', shadow=True)
        plt.tight_layout() # Ajusta as margens automaticamente
        plt.show()

if __name__ == "__main__":
    app = XPSApp()
    app.mainloop()