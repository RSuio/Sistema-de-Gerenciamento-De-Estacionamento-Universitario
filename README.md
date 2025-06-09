# Sistema-de-Gerenciamento-De-Estacionamento-Universitario
Um sistema básico de um gerenciamento de estacionamento.

Sistema de Gerenciamento de Estacionamento:
1. Introdução
Este documento descreve o Sistema de Gerenciamento de Estacionamento, uma aplicação desktop desenvolvida em Python para gerenciar operações de estacionamento em uma instituição. A aplicação utiliza a biblioteca Tkinter para uma interface gráfica moderna e intuitiva, com um banco de dados MySQL para armazenamento seguro e eficiente dos dados. O sistema suporta o cadastro de usuários (alunos, professores, funcionários e visitantes), veículos, vagas, reservas e ocupações, além de oferecer funcionalidades avançadas de edição, exclusão e geração de relatórios detalhados.
O objetivo é automatizar e otimizar o controle de estacionamento, garantindo facilidade de uso, validações robustas e uma interface visualmente atraente, com um fundo temático de estacionamento e um design responsivo em tela cheia.


2. Objetivo do Sistema
O sistema foi projetado para:
Gerenciar cadastros de usuários (alunos, professores, funcionários e visitantes) e seus veículos.
Controlar a alocação de vagas, incluindo tipos especiais (idoso e deficiente).
Permitir reservas de vagas para períodos específicos, com validação de disponibilidade.
Registrar entradas e saídas de veículos, atualizando o estado das vagas em tempo real.
Fornecer relatórios detalhados sobre vagas, ocupações, usuários, veículos e reservas.
Oferecer funcionalidades de edição e exclusão de registros, com validações para garantir a integridade dos dados.


3. Requisitos do Sistema
3.1. Requisitos de Software
Sistema Operacional: Windows, Linux ou macOS.
Python: Versão 3.8 ou superior.
Bibliotecas Python:
mysql-connector-python: Conexão e manipulação do banco de dados MySQL.
python-dotenv: Gerenciamento de variáveis de ambiente via arquivo .env.
Pillow: Processamento de imagens para o fundo temático.
requests: Requisições HTTP para carregar imagens de fundo.
tkinter: Biblioteca nativa do Python para criação da interface gráfica.
io: Manipulação de dados binários em memória.
math:Biblioteca nativa do Python para operações matemáticas, como cálculos e manipulação de números.
datetime:Biblioteca nativa do Python para manipulação de datas e horários.
Banco de Dados: MySQL Server 8.0 ou superior.
IDE: Visual Studio Code (recomendado) ou outra de preferência.


4. Estrutura do Projeto
O projeto está organizado nos seguintes arquivos:
estacionamento_core.py: Contém a lógica principal, incluindo as classes Database, Usuario, Veiculo, Vaga, Reserva e Ocupacao, responsáveis pela conexão com o banco de dados e pelas operações de negócio.
estacionamento_gui.py: Implementa a interface gráfica com Tkinter, incluindo menus, formulários, relatórios e funcionalidades de edição/exclusão.
.env: Arquivo de configuração para credenciais do banco de dados (não versionado).
requirements.txt: Lista as dependências Python necessárias.
SQL Scripts: Incluídos em estacionamento_core.py, criam o banco de dados estacionamento e suas tabelas.
README.md: Este documento, com instruções detalhadas do projeto.

4.1. Modelo Conceitual
Entidades: Aluno, Professor, Funcionário, Visitante, Veículo, Vaga, Reserva, Ocupação.
Relacionamentos:
Um usuário (Aluno, Professor, Funcionário ou Visitante) pode ter vários veículos (1:N).
Um veículo pertence a apenas um usuário (1:1).
Uma vaga pode ter várias reservas e ocupações ao longo do tempo (1:N).
Uma reserva ou ocupação está associada a uma única vaga (1:1).

4.2. Modelo Lógico
O banco de dados inclui as seguintes tabelas:
ALUNO, PROFESSOR, FUNCIONARIO, VISITANTE: Armazenam informações pessoais (nome, telefone, e-mail, documento, matrícula para alunos).
VEICULO: Registra veículos (placa, modelo, vínculo com usuário).
VAGA: Contém informações de localização, tipo (comum, idoso, deficiente) e estado (disponível, ocupada, reservada).
RESERVA: Armazena reservas (data de início, fim, status, vínculo com usuário e vaga).
OCUPACAO: Registra o histórico de ocupações (data de entrada, saída, vínculo com veículo e vaga).

5. Instalação
5.1. Configuração do Banco de Dados
Instale o MySQL Server (versão 8.0 ou superior).
Execute os scripts SQL em estacionamento_core.py para criar o banco de dados estacionamento e suas tabelas.
Crie um arquivo .env na raiz do projeto com as credenciais do banco:
DB_HOST='localhost'
DB_USER='root'
DB_PASSWORD='sua_senha'
DB_NAME='estacionamento'

5.2. Configuração do Ambiente Python
Instale o Python 3.8 ou superior.
Na raiz do projeto, instale as dependências:
pip install -r requirements.txt
Verifique se o tkinter está disponível (geralmente incluído na instalação padrão do Python).

5.3. Execução da Aplicação
Abra o projeto no Visual Studio Code ou outra IDE.
Certifique-se de que os arquivos estacionamento_core.py, estacionamento_gui.py, .env e requirements.txt estão na raiz do projeto.
Execute o script principal:
python estacionamento_gui.py


6. Uso do Sistema
A aplicação opera em tela cheia, com uma interface gráfica moderna e um fundo temático de estacionamento com 50% de opacidade, garantindo estética e legibilidade. Os botões possuem um design consistente com cores vibrantes, fontes claras (Arial) e espaçamento otimizado.

6.1. Menu Principal
O menu principal (Dashboard) é dividido em três seções:
Ações Rápidas: Botões para cadastro, operações e edição/exclusão de dados.
Distribuição do Sistema: Gráfico de rosca atualizado em tempo real, exibindo o número de usuários, veículos, vagas disponíveis, ocupadas e reservadas.
Dados Recentes: Exibe tabelas interativas com vagas disponíveis, ocupações ativas e reservas ativas, organizadas em abas.

6.2. Funcionalidades
Cadastrar Usuário: Registra alunos, professores, funcionários ou visitantes, com validação de campos obrigatórios (nome, documento, matrícula para alunos). Formulário dinâmico exibe o campo de matrícula apenas para alunos.
Cadastrar Veículo: Associa veículos (placa, modelo) a um usuário, com validação de ID e tipo de proprietário.
Cadastrar Vaga: Registra vagas com localização e tipo (comum, idoso, deficiente), inicializando o estado como "disponível".
Reservar Vaga: Permite reservar uma vaga para um período, com validação de formato de data (AAAA-MM-DD HH:MM), disponibilidade e conflitos de reservas.
Registrar Entrada: Marca a entrada de um veículo em uma vaga, atualizando o estado para "ocupada" e validando reservas existentes.
Registrar Saída: Registra a saída de um veículo, liberando a vaga e atualizando o histórico.
Editar Dados: Permite editar registros de usuários, veículos, vagas, reservas e ocupações, com formulários pré-preenchidos e validações robustas.
Deletar Dados: Exclui registros de qualquer entidade (usuário, veículo, vaga, reserva, ocupação), com verificação de existência.
Relatórios: Exibe dados em tabelas interativas com barras de rolagem:
Vagas Disponíveis: ID, localização, tipo.
Ocupações Ativas: ID, placa, vaga, entrada, saída.
Histórico de Ocupações: ID, placa, vaga, entrada, saída (ordenado por data).
Todos os Usuários: ID, tipo, nome, telefone, e-mail, documento, matrícula (se aplicável).
Todos os Veículos: ID, placa, modelo, proprietário, tipo.
Todas as Reservas: ID, vaga, usuário, tipo, início, fim, status.
Todas as Vagas: ID, localização, estado, tipo.
Relatório Completo: Combina todas as informações acima em um único relatório com rolagem.

7. Segurança de Dados
Credenciais: Armazenadas no arquivo .env, que deve ser protegido e não versionado.
Validações: Validações rigorosas de entrada (ex.: formato de data, IDs numéricos, existência de registros).
Transações: Operações críticas (cadastros, reservas, ocupações) utilizam transações SQL para garantir consistência.
Exceções: Tratamento de erros exibe mensagens claras ao usuário via caixas de diálogo.

8. Estrutura do Código
O código é modular, dividido em dois arquivos principais:
estacionamento_core.py:
Database: Gerencia a conexão com o MySQL e cria as tabelas.
Usuario: Cadastro de usuários com validação de tipo e matrícula.
Veiculo: Cadastro de veículos com validação de proprietário.
Vaga: Gerenciamento de vagas com estado e tipo.
Reserva: Criação e validação de reservas, incluindo verificação de conflitos.
Ocupacao: Registro de entradas e saídas, com atualização de estados.
estacionamento_gui.py:
Implementa a interface gráfica com Tkinter, incluindo:
Dashboard com gráfico dinâmico e abas de dados recentes.
Formulários para cadastros, operações, edição e exclusão.
Relatórios em tabelas com barras de rolagem.
Design moderno com fundo temático e botões estilizados.

9. Considerações Finais
O Sistema de Gerenciamento de Estacionamento é uma solução robusta, modular e amigável para o controle de estacionamentos institucionais. A interface em tela cheia, com design moderno e funcionalidades de edição/exclusão, garante uma experiência eficiente e visualmente agradável. Para dúvidas ou suporte, contate a equipe de desenvolvimento.
Autoria: Alberto Vitorino Silva Barros, Bruno de Melo Baumgartner, Isabelle Melo Moraes, Thiago Henrique Ciriano Neves.
Data: 30 de maio de 2025
Versão: 1.0


