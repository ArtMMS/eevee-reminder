# Project Roadmap

This project will be developed incrementally, starting with a minimal proof of concept and gradually evolving into a complete Windows application. Each milestone introduces new features while keeping the project functional and easy to test.



Etapa 1 — Paleta de Cores e Estilização Base (ttk.Style)

    Definir as variáveis globais de cores com base na arte (Creme #FAF6F0, Marrom/Terracota #8B5A2B, Destaque Verde #EAF4EC e Texto #2C2C2C).

    Sobrescrever o tema padrão do Tkinter (ttk.Style.theme_use("clam")) para remover as bordas cinzas tridimensionais da Treeview e ajustar a altura das linhas para 35px.

Etapa 2 — Estrutura de Layout e Sidebar (Barra Lateral)

    Dividir a janela principal (820x520) em dois painéis fixos: Sidebar (à esquerda) e Main Panel (à direita).

    Montar a barra lateral com o título Eevee Reminder, os botões de navegação estilizados (Home, Settings e About) e o rodapé com a frase motivacional.

    Inserir o carregamento da imagem da Eevee na parte inferior da barra lateral usando Pillow (ImageTk.PhotoImage).

Etapa 3 — Cabeçalho Dinâmico e Formulário Inline

    Adicionar a saudação no topo do painel principal que muda dinamicamente de acordo com o relógio do sistema (Good morning, Good afternoon, Good evening).

    Mover o formulário de cadastro (campos de remédio, horário e botão de salvar) para a parte superior da lista em formato compacto/inline.

Etapa 4 — Tabela Integrada e Card "Next Medication"

    Ajustar a Treeview para ocupar o centro da tela sem barras de rolagem desnecessárias, exibindo apenas as colunas Medicamento e Horário.

    Criar o card inferior com fundo verde claro (#EAF4EC) para o Next Medication.

    Conectar a lógica que calcula automaticamente qual é o próximo remédio do dia e exibe a contagem regressiva ("em X horas e Y min"), atualizando a cada alteração da lista.

Etapa 5 — Redesign da Janela Pop-up de Alarme

    Reformular a janela do alarme para utilizar o mesmo fundo creme/branco e bordas limpas.

    Incluir a ilustração da Eevee ao lado da mensagem do remédio e aplicar os botões estilizados Tomei ✓ (Marrom) e Adiar 5m ⏱ (Bege).