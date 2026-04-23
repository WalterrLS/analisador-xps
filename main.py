import customtkinter as ctk
import json
import os
import requests
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- CONFIGURAÇÕES ---  # AQUI É DE ONDE O SOFTWARE VAI BUSCAR OS DADOS DE ENERGIA DE VÍNCULO E ASF PARA CADA ORBITAL
URL_GITHUB = "https://raw.githubusercontent.com/WalterrLS/analisador-xps/refs/heads/main/meu_banco_xps.json" # AQUI É O LINK DO ARQUIVO JSON NO GITHUB, QUE CONTÉM OS DADOS DE ENERGIA DE VÍNCULO E ASF PARA CADA ORBITAL
ARQUIVO_LOCAL = "meu_banco_xps.json" # AQUI É O NOME DO ARQUIVO LOCAL ONDE OS DADOS VÃO SER SALVOS APÓS A SINCRONIZAÇÃO COM A NUVEM. SE O ARQUIVO NÃO EXISTIR, ELE VAI SER CRIADO VAZIO NA PRIMEIRA EXECUÇÃO PARA EVITAR ERROS

class XPSApp(ctk.CTk):  # AQUI É A CLASSE PRINCIPAL DO SOFTWARE, QUE HERDA DE CTK.CTK PARA CRIAR A JANELA PRINCIPAL
    def __init__(self): # O MÉTODO __INIT__ É O CONSTRUTOR DA CLASSE, ONDE SÃO INICIALIZADAS AS CONFIGURAÇÕES INICIAIS DA JANELA E OS ELEMENTOS GRÁFICOS
        super().__init__() # AQUI É CHAMADO O CONSTRUTOR DA CLASSE PAI (CTK.CTK) PARA INICIALIZAR A JANELA ANTES DE CONFIGURAR OS ELEMENTOS GRÁFICOS
        # AQUI SÃO AS CONFIGURAÇÕES INICIAIS DA JANELA
        self.title("Simulador de Espectros XPS - v1.2") # AQUI É O TÍTULO DA JANELA
        self.geometry("1100x750") # AQUI É O TAMANHO INICIAL DA JANELA (LARGURA x ALTURA)
        ctk.set_appearance_mode("dark") # MODO ESCURO
        
        try: # AQUI É TENTADO DEFINIR O ÍCONE DA JANELA, MAS SE O ARQUIVO "logo.ico" NÃO FOR ENCONTRADO, O PROGRAMA VAI RODAR NORMALMENTE SEM O ÍCONE
            self.iconbitmap("logo.ico") 
        except: 
            pass    

        self.dados_elemento_atual = None   # VARIÁVEL PARA ARMAZENAR OS DADOS DO ORBITAL SELECIONADO

        if not os.path.exists(ARQUIVO_LOCAL):  # SE O ARQUIVO LOCAL NÃO EXISTIR, CRIA UM VAZIO PARA EVITAR ERROS
            with open(ARQUIVO_LOCAL, 'w', encoding='utf-8') as f: 
                json.dump({}, f)  

        # LAYOUT DE GRID PARA ARRUMAR AS FRAMES
        self.grid_columnconfigure(1, weight=1) # AQUI É CONFIGURADO O GRID PARA QUE A COLUNA 1 (ONDE FICA O GRÁFICO) SE EXPANDA PARA PREENCHER O ESPAÇO DISPONÍVEL
        self.grid_rowconfigure(0, weight=1) # AQUI É CONFIGURADO O GRID PARA QUE A LINHA 0 SE EXPANDA PARA PREENCHER O ESPAÇO DISPONÍVEL

        # SIDEBAR
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0) # AQUI É A CONFIGURAÇÃO DA SIDEBAR (LARGURA E CANTO ARREDONDADO)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10) # AQUI É ONDE A SIDEBAR VAI FICAR (LINHA 0, COLUNA 0) E O "STICKY" FAZ COM QUE ELA SE EXPANDA PARA PREENCHER O ESPAÇO DISPONÍVEL

        ctk.CTkLabel(self.sidebar, text="Ajustes de Simulação", font=("Arial", 18, "bold")).pack(pady=20) # AQUI É O TÍTULO DA SIDEBAR, COM UM ESPAÇO ACIMA E ABAIXO DE 20 PIXELS
        
        self.btn_sync = ctk.CTkButton(self.sidebar, text="Sincronizar Nuvem ↻",  # AQUI É O BOTÃO DE SINCRONIZAÇÃO COM A NUVEM, COM UM TEXTO E UM SÍMBOLO DE RECICLAGEM
                                      fg_color="#28a745", hover_color="#218838", # AQUI SÃO AS CORES DO BOTÃO (COR DE FUNDO E COR DE HOVER)
                                      command=self.sincronizar_banco) # AQUI É A FUNÇÃO QUE VAI SER CHAMADA QUANDO O BOTÃO FOR CLICADO (SINCRONIZAR O BANCO DE DADOS COM A NUVEM)
        self.btn_sync.pack(pady=(10, 5), padx=20) # AQUI É ONDE O BOTÃO VAI FICAR, COM UM ESPAÇO ACIMA DE 10 PIXELS E ABAIXO DE 5 PIXELS, E UM ESPAÇO LATERAL DE 20 PIXELS
        
        self.label_status_sync = ctk.CTkLabel(self.sidebar, text="Aguardando...", font=("Arial", 11, "italic")) # AQUI É O RÓTULO QUE VAI MOSTRAR O STATUS DA SINCRONIZAÇÃO, COM UM TEXTO INICIAL DE "AGUARDANDO..." E UMA FONTE ITÁLICA
        self.label_status_sync.pack(pady=(0, 10))

        self.frame_busca = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.frame_busca.pack(pady=10, fill="x", padx=10)
        self.entry_elemento = ctk.CTkEntry(self.frame_busca, placeholder_text="Ex: Si", width=80)
        self.entry_elemento.pack(side="left", padx=5)
        self.btn_buscar = ctk.CTkButton(self.frame_busca, text="Listar", width=100, command=self.carregar_dados)
        self.btn_buscar.pack(side="left", padx=5)

        self.combo_orbitais = ctk.CTkComboBox(self.sidebar, values=["..."], command=self.ao_selecionar_orbital)
        self.combo_orbitais.pack(pady=10, fill="x", padx=20)

        ctk.CTkLabel(self.sidebar, text="Resolução de Energia (eV)").pack(pady=(20, 0))
        self.label_fwhm_val = ctk.CTkLabel(self.sidebar, text="1.20", text_color="#3498db", font=("Arial", 12, "bold"))
        self.label_fwhm_val.pack()
        self.slider_fwhm = ctk.CTkSlider(self.sidebar, from_=0.1, to=4.0, command=self.atualizar_fwhm)
        self.slider_fwhm.set(1.2)
        self.slider_fwhm.pack(pady=5, padx=20)

        ctk.CTkLabel(self.sidebar, text="Qualidade do Sinal(SNR)").pack(pady=(15, 0))
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

# --- FUNÇÕES MATEMÁTICAS ---
    def pseudo_voigt(self, x, be, fwhm, eta=0.3): # AQUI É A FUNÇÃO QUE CALCULA O PERFIL PSEUDO-VOIGT, QUE É UMA COMBINAÇÃO LINEAR ENTRE UMA GAUSSIANA E UMA LORENTZIANA, CONTROLADA PELO PARÂMETRO ETA. ESSA FUNÇÃO É USADA PARA GERAR O SINAL TEÓRICO PURO DO ESPECTRO XPS, ANTES DE APLICAR O RUÍDO DE POISSON E O TRATAMENTO DE FUNDO DE SHIRLEY.
        """
        Calcula o perfil Pseudo-Voigt diretamente.
        eta=0 é 100% Gaussiana, eta=1 é 100% Lorentziana.
        """
        # Parâmetros de largura
        sigma = fwhm / 2.3548
        gamma = fwhm / 2.0
        
        # Cálculo da Gaussiana
        g = np.exp(-(x - be)**2 / (2 * sigma**2))
        
        # Cálculo da Lorentziana
        l = (gamma**2) / ((x - be)**2 + gamma**2)
        
        # Retorno da combinação linear
        return (1 - eta) * g + eta * l

    def atualizar_fwhm(self, valor): #Slider de resolução de energia (FWHM)
        self.label_fwhm_val.configure(text=f"{valor:.2f}")
        self.replotar()

    def atualizar_ruido(self, valor): #Slider de qualidade do sinal (SNR)
        self.label_ruido_val.configure(text=f"{valor:.1f}")
        self.replotar()

    def sincronizar_banco(self): #Botão para sincronizar o banco de dados com a nuvem, baixando o arquivo JSON do GitHub e salvando localmente
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

    def carregar_dados(self): #Função para carregar os dados do orbital selecionado e atualizar o combo box de orbitais disponíveis para o elemento digitado
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

    def ao_selecionar_orbital(self, orbital_escolhido): #Função para carregar os dados do orbital selecionado e atualizar o gráfico
        elem = self.entry_elemento.get().strip().upper()
        try:
            with open(ARQUIVO_LOCAL, 'r', encoding='utf-8') as f:
                banco = json.load(f)
                self.dados_elemento_atual = banco[elem]["orbitais"][orbital_escolhido]
                nome_completo = banco[elem]["nome"]
                self.dados_elemento_atual["nome"] = f"{nome_completo} {orbital_escolhido}"
            self.replotar()
        except:
            pass

    def calcular_shirley(self, y): #Função para calcular o fundo de Shirley a partir do espectro simulado, usando um método iterativo para ajustar o fundo com base na área total entre o espectro e o fundo
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

    def replotar(self): #Função para replotar o gráfico com base nos dados do orbital atual, aplicando o perfil Pseudo-Voigt, a estatística de Poisson e o tratamento de fundo de Shirley, além de atualizar a estética do gráfico
        if not self.dados_elemento_atual:
            return
        
        self.ax.clear()
        self.ax.set_facecolor('#ffffff')
        self.ax.grid(True, linestyle='--', alpha=0.3)

        be = self.dados_elemento_atual["be"]
        asf = self.dados_elemento_atual["asf"]
        fwhm = self.slider_fwhm.get()
        
        # Eixo X com margem de 10 eV para cada lado
        x = np.linspace(be + 10, be - 10, 400)
        
        # 1. Geração do Sinal Puro usando Pseudo-Voigt (Mix de 30% Lorentziana)
        y_teorico_max = (asf * 1000)
        y_puro = y_teorico_max * self.pseudo_voigt(x, be, fwhm, eta=0.3)
        
        # 2. Estatística de Poisson (Shot Noise)
        fator_intensidade = max(self.slider_ruido.get(), 0.1)
        y_final = np.random.poisson(np.maximum(y_puro, 0) * fator_intensidade) / fator_intensidade
        
        # 3. Tratamento Shirley
        bg = self.calcular_shirley(y_final)
        
        # Desenho do gráfico
        self.ax.fill_between(x, bg, y_final, color='#3498db', alpha=0.3, label="Área de Pico")
        self.ax.scatter(x, y_final, s=2, color='black', alpha=0.6, label="Sinal Simulado")
        self.ax.plot(x, bg, color='#e74c3c', lw=2, label="Fundo de Shirley")
        
        # --- ESTÉTICA DO BALÃO (ANNOTATE) ---
        y_pico_real = np.max(y_final)
        self.ax.annotate(f"{self.dados_elemento_atual['nome']}\n{be:.2f} eV", 
                         xy=(be, y_pico_real), 
                         xytext=(0, 20), 
                         textcoords="offset points",
                         ha='center', va='bottom',
                         fontsize=10, fontweight='bold', color='#2c3e50',
                         bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#3498db", alpha=0.9),
                         arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color="#3498db"))

        self.ax.invert_xaxis()
        self.ax.set_title(f"Simulação: {self.dados_elemento_atual['nome']}", pad=25, fontsize=14, fontweight='bold')
        self.ax.set_xlabel("Binding Energy (eV)")
        self.ax.set_ylabel("Intensity (counts)")
        self.ax.legend(fontsize='x-small', loc='upper right')
        
        self.canvas.draw_idle()

if __name__ == "__main__":
    app = XPSApp()
    app.mainloop()