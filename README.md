Software em Python para simulação e análise de dados de XPS
# ⚛️ Analisador XPS: Simulação e Consulta de Referências

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

## 📌 Sobre o Projeto
Este software foi desenvolvido como um projeto durante a graduação, com foco em **Espectroscopia de Fotoelétrons excitados por Raios-X (XPS)**. O objetivo é facilitar a identificação de estados de oxidação e elementos químicos através da comparação de dados experimentais com referências bibliográficas (NIST/PHI).

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
{
    "C": {
        "adventicio": {
            "be": 284.8,
            "orbital": "1s",
            "info": "Referência universal de calibração para amostras expostas ao ar"
        },
        "grafite": {
            "be": 284.0,
            "orbital": "1s",
            "info": "Carbono sp2 puro"
        }
    },
    "O": {
        "oxido": {
            "be": 529.8,
            "orbital": "1s",
            "info": "Oxigênio de rede metálica (ex: TiO2, Al2O3)"
        },
        "organico": {
            "be": 532.0,
            "orbital": "1s",
            "info": "Oxigênio em ligações C-O ou contaminação de superfície"
        }
    },
    "AU": {
        "metal": {
            "be": 84.0,
            "orbital": "4f 7/2",
            "info": "Padrão primário de calibração de energia do equipamento"
        }
    },
    "AG": {
        "metal": {
            "be": 368.2,
            "orbital": "3d 5/2",
            "info": "Padrão de calibração e teste de resolução do feixe"
        }
    },
    "CU": {
        "metal": {
            "be": 932.7,
            "orbital": "2p 3/2",
            "info": "Cobre metálico puro"
        },
        "oxido_ii": {
            "be": 933.6,
            "orbital": "2p 3/2",
            "info": "CuO (Cobre II). Nota: Apresenta satélites intensos em 943 eV"
        }
    },
    "TI": {
        "metal": {
            "be": 454.1,
            "orbital": "2p 3/2",
            "info": "Titânio metálico"
        },
        "oxido": {
            "be": 458.5,
            "orbital": "2p 3/2",
            "info": "TiO2 (Dióxido de Titânio)"
        }
    },
    "SI": {
        "metal": {
            "be": 99.3,
            "orbital": "2p",
            "info": "Silício elementar (Si 0)"
        },
        "oxido": {
            "be": 103.3,
            "orbital": "2p",
            "info": "SiO2 (Sílica)"
        }
    },
    "AL": {
        "metal": {
            "be": 72.9,
            "orbital": "2p",
            "info": "Alumínio metálico"
        },
        "oxido": {
            "be": 74.7,
            "orbital": "2p",
            "info": "Al2O3 (Alumina)"
        }
    },
    "FE": {
        "metal": {
            "be": 706.7,
            "orbital": "2p 3/2",
            "info": "Ferro metálico"
        },
        "oxido_iii": {
            "be": 710.7,
            "orbital": "2p 3/2",
            "info": "Fe2O3 (Hematita)"
        }
    },
    "NI": {
        "metal": {
            "be": 852.6,
            "orbital": "2p 3/2",
            "info": "Níquel metálico"
        },
        "oxido": {
            "be": 853.7,
            "orbital": "2p 3/2",
            "info": "NiO (Óxido de Níquel)"
        }
    }
}
