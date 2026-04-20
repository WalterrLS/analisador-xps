Software em Python para simulação de espectros
# ⚛️ Analisador XPS: Simulação de Espectros

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

📌 **Sobre o Projeto**
Este software está sendo desenvolvido como um projeto durante a graduação em Física, com foco em **Espectroscopia de Fotoelétrons excitados por Raios-X (XPS)**. O objetivo é facilitar a identificação de elementos químicos e estados de oxidação através da comparação de dados experimentais com referências bibliográficas (NIST/PHI).

A ferramenta permite simular picos espectroscópicos teóricos, tratar sinais experimentais e sincronizar um banco de dados dinâmico hospedado em nuvem.

🚀 **Funcionalidades Atuais**
* **Interface Gráfica (GUI):** Experiência de usuário moderna desenvolvida com `CustomTkinter`.
* **Tratamento Físico de Dados:** Implementação do algoritmo iterativo de **Background Shirley** para subtração de fundo inelástico.
* **Simulação Dinâmica:** Geração de curvas Gaussianas com ajuste em tempo real de FWHM e níveis de ruído estatístico.
* **Sincronização em Nuvem:** Download e atualização automática do banco de dados (`.json`) diretamente do repositório remoto via GitHub.
* **Padrão Científico:** Gráficos gerados com o eixo X invertido e anotações dinâmicas de picos, seguindo o rigor da espectroscopia.

🛠️ **Tecnologias Utilizadas**
* **Python 3**
* **CustomTkinter:** Interface visual e interatividade.
* **Matplotlib:** Plotagem de gráficos científicos de alta resolução.
* **NumPy:** Cálculos vetoriais e simulação de sinais físicos.
* **Requests:** Comunicação com a API do GitHub para sincronização de dados.

🏗️ **Futuras Atualizações**
* **Quantificação Relativa:** Módulo para cálculo automático de **Porcentagem Atômica (%)**.
* **Física Avançada:** Simulação de **Dubletos Spin-Órbita** e picos satélites.
* **Exportação Científica:** Função para exportar dados tratados em formato `.csv`.
