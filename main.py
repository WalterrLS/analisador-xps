import customtkinter as ctk
import json
import os
import requests
import matplotlib.pyplot as plt
import numpy as np

# --- CONFIGURAÇÕES GLOBAIS ---
# Substitua pelo link 'RAW' do seu JSON no GitHub após fazer o upload
URL_GITHUB = "https://github.com/WalterrLS/analisador-xps/blob/main/meu_banco_xps.json"
ARQUIVO_LOCAL = "meu_banco_xps.json"

class XPSApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração da Janela Principal
        self.title("XPS Analyzer Pro - Mês 1")
        self.geometry("500x450")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # --- Elementos da Interface ---
        self.label_titulo = ctk.CTkLabel(self, text="Consultoria de Referência XPS", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_titulo.pack(pady=20)

        # Botão de Sincronização
        self.btn_sync = ctk.CTkButton(self, text="Sincronizar com GitHub", command=self.sincronizar_banco, fg_color="green", hover_color="darkgreen")
        self.btn_sync.pack(pady=10)

        self.status_label = ctk.CTkLabel(self, text="Banco Local detectado", text_color="gray")
        self.status_label.pack(pady=5)

        # Campo de Busca
        self.label_busca = ctk.CTkLabel(self, text="Digite o Elemento (ex: Ti, Au):")
        self.label_busca.pack(pady=(20, 0))
        
        self.entry_elemento = ctk.CTkEntry(self, placeholder_text="Símbolo...")
        self.entry_elemento.pack(pady=10)

        # Botão de Gráfico
        self.btn_plot = ctk.CTkButton(self, text="Gerar Gráfico de Referência", command=self.preparar_plot)
        self.btn_plot.pack(pady=20)

        # Rodapé
        self.label_footer = ctk.CTkLabel(self, text="Projeto Análise XPS", font=ctk.CTkFont(size=10))
        self.label_footer.pack(side="bottom", pady=10)

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

    # --- LÓGICA DE GRÁFICO (Reaproveitada do nosso código anterior) ---
    def preparar_plot(self):
        elemento = self.entry_elemento.get().strip().upper()
        
        if not os.path.exists(ARQUIVO_DB := ARQUIVO_LOCAL):
            self.status_label.configure(text="[!] Erro: Baixe o banco primeiro!", text_color="red")
            return

        with open(ARQUIVO_DB, 'r', encoding='utf-8') as f:
            banco = json.load(f)

        if elemento in banco:
            # Por enquanto, pegamos o primeiro estado disponível para simplificar a GUI
            estado = list(banco[elemento].keys())[0]
            dados = banco[elemento][estado]
            self.mostrar_grafico(elemento, estado, dados)
        else:
            self.status_label.configure(text=f"[!] {elemento} não encontrado no banco", text_color="orange")

    def mostrar_grafico(self, elemento, estado, dados):
        be = dados['be']
        orbital = dados['orbital']
        
        # Matemática da Simulação
        x = np.linspace(be - 5, be + 5, 1000)
        y = 100 * np.exp(-(x - be)**2 / (2 * 0.6**2))
        
        plt.figure("Visualizador XPS", figsize=(8, 5))
        plt.plot(x, y, color='black', lw=2, label=f"Ref: {elemento} {orbital}")
        plt.axvline(x=be, color='red', linestyle='--', alpha=0.7)
        plt.text(be, max(y)*1.02, f'{be} eV', color='red', ha='center', fontweight='bold')
        
        plt.gca().invert_xaxis()
        plt.title(f"Padrão de Referência: {elemento} ({estado})")
        plt.xlabel("Binding Energy (eV)")
        plt.ylabel("Intensidade (u.a.)")
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.legend()
        plt.show()

if __name__ == "__main__":
    app = XPSApp()
    app.mainloop()