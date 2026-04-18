Software em Python para simulação e análise de dados de XPS
# ⚛️ Analisador XPS: Simulação e Consulta de Referências

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

## 📌 Sobre o Projeto
Este software foi desenvolvido como um projeto pessoal durante a graduação, com foco em **Espectroscopia de Fotoelétrons excitados por Raios-X (XPS)**. O objetivo é facilitar a identificação de estados de oxidação e elementos químicos através da comparação de dados experimentais com referências bibliográficas (NIST/PHI).

A ferramenta permite simular picos espectroscópicos teóricos e sincronizar um banco de dados dinâmico hospedado em nuvem.

## 🚀 Funcionalidades (Mês 1)
- **Interface Gráfica (GUI):** Desenvolvida com `CustomTkinter` para uma experiência de usuário moderna.
- **Simulação de Picos:** Geração de curvas Gaussianas baseadas em Energias de Ligação (Binding Energy) nominais.
- **Sincronização em Nuvem:** Download automático do banco de dados (`.json`) diretamente do repositório remoto.
- **Padrão Científico:** Gráficos gerados com o eixo X invertido, seguindo a convenção da área de espectroscopia.

## 🛠️ Tecnologias Utilizadas
- **Python 3**
- **CustomTkinter:** Interface visual.
- **Matplotlib:** Plotagem de gráficos científicos.
- **NumPy:** Cálculos matemáticos e geração de sinais.
- **Requests:** Comunicação com a API do GitHub para sincronização.

## 📂 Estrutura do Banco de Dados
O software utiliza um arquivo JSON estruturado para catalogar os elementos:
```json
"TI": {
    "oxido": {
        "be": 458.5,
        "orbital": "2p 3/2",
        "info": "TiO2 (Dióxido de Titânio)"
    }
}
