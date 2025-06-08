import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from PIL import Image, ImageTk
import requests
import math
from io import BytesIO
from estacionamento_core import Database, Usuario, Veiculo, Vaga, Reserva, Ocupacao

class EstacionamentoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Estacionamento - Dashboard")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#f0f2f5')
        self.estacionamento = Database()
        self.usuario = Usuario(self.estacionamento)
        self.veiculo = Veiculo(self.estacionamento)
        self.vaga = Vaga(self.estacionamento)
        self.reserva = Reserva(self.estacionamento)
        self.ocupacao = Ocupacao(self.estacionamento)
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TButton', font=('Arial', 12), padding=10, background='#d32f2f', foreground='white')
        self.style.map('TButton', background=[('active', '#4945a0')])
        self.style.configure('TCombobox', font=('Arial', 12))
        self.style.configure('TLabel', background='#f0f2f5', font=('Arial', 12))
        self.style.configure('Treeview', font=('Arial', 11))
        self.style.configure('Treeview.Heading', font=('Arial', 12, 'bold'))
        response = requests.get('https://static.vecteezy.com/system/resources/previews/001/437/687/original/empty-car-parking-isometric-design-free-vector.jpg')
        img_data = BytesIO(response.content)
        img = Image.open(img_data)
        img = img.convert('RGBA')
        alpha = Image.new('RGBA', img.size, (255, 255, 255, 128))
        img = Image.blend(img, alpha, 0.5)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        img = img.resize((screen_width, screen_height), Image.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(img)
        self.bg_label = tk.Label(self.root, image=self.bg_image)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.current_frame = None
        self.create_dashboard()

    def create_dashboard(self):
        self.clear_window()
        self.current_frame = tk.Frame(self.root, bg='#f0f2f5')
        self.current_frame.pack(expand=True, fill='both', padx=20, pady=20)
        header_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        header_frame.pack(fill='x', pady=10)
        tk.Label(header_frame, text="Sistema de Estacionamento - Dashboard", font=('Arial', 24, 'bold'), bg='#f0f2f5', fg='#333').pack(pady=10)
        content_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        content_frame.pack(expand=True, fill='both')
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=2)
        actions_frame = tk.Frame(content_frame, bg='#ffffff', bd=2, relief='groove')
        actions_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        tk.Label(actions_frame, text="Ações Rápidas", font=('Arial', 16, 'bold'), bg='#ffffff', fg='#333').pack(pady=10)
        action_buttons_frame = tk.Frame(actions_frame, bg='#ffffff')
        action_buttons_frame.pack(pady=5)
        action_buttons_frame.grid_columnconfigure(0, weight=1)
        action_buttons_frame.grid_columnconfigure(1, weight=1)
        buttons = [
            ("Cadastrar Usuário", self.show_cadastrar_usuario),
            ("Cadastrar Veículo", self.show_cadastrar_veiculo),
            ("Cadastrar Vaga", self.show_cadastrar_vaga),
            ("Reservar Vaga", self.show_reservar_vaga),
            ("Registrar Entrada", self.show_registrar_entrada),
            ("Registrar Saída", self.show_registrar_saida),
            ("Editar Dados", self.show_editar_dados),
            ("Deletar Dados", self.show_deletar_dados),
        ]
        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(action_buttons_frame, text=text, command=lambda cmd=command: self.open_popup(cmd), style='TButton')
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky='ew')
        tk.Button(actions_frame, text="Sair", command=self.exit_system, bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(pady=10)
        metrics_frame = tk.Frame(content_frame, bg='#ffffff', bd=2, relief='groove')
        metrics_frame.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)
        tk.Label(metrics_frame, text="Distribuição do Sistema", font=('Arial', 16, 'bold'), bg='#ffffff', fg='#333').pack(pady=10)

        canvas = tk.Canvas(metrics_frame, width=350, height=350, bg='white')
        canvas.pack(pady=10)

        def update_chart():
            try:
                if not canvas.winfo_exists():
                    return

                canvas.delete("all")

                try:
                    num_usuarios = 0
                    user_types = ['ALUNO', 'PROFESSOR', 'FUNCIONARIO', 'VISITANTE']
                    cursor = self.estacionamento.connection.cursor()
                    for user_type in user_types:
                        query = f"SELECT COUNT(*) FROM {user_type}"
                        cursor.execute(query)
                        num_usuarios += cursor.fetchone()[0]
                    cursor.close()
                except Exception:
                    num_usuarios = 0

                try:
                    query = "SELECT COUNT(*) FROM VEICULO"
                    cursor = self.estacionamento.connection.cursor()
                    cursor.execute(query)
                    num_veiculos = cursor.fetchone()[0]
                    cursor.close()
                except Exception:
                    num_veiculos = 0

                try:
                    vagas = self.vaga.listar_disponiveis()
                    vagas_disponiveis = len(vagas) if vagas else 0
                except Exception:
                    vagas_disponiveis = 0

                try:
                    query = "SELECT COUNT(*) FROM OCUPACAO WHERE data_saida IS NULL"
                    cursor = self.estacionamento.connection.cursor()
                    cursor.execute(query)
                    vagas_ocupadas = cursor.fetchone()[0]
                    cursor.close()
                except Exception:
                    vagas_ocupadas = 0

                try:
                    query = "SELECT COUNT(*) FROM RESERVA WHERE status = 'ativa'"
                    cursor = self.estacionamento.connection.cursor()
                    cursor.execute(query)
                    vagas_reservadas = cursor.fetchone()[0]
                    cursor.close()
                except Exception:
                    vagas_reservadas = 0

                dados = [
                    ("Usuários", max(num_usuarios, 1), '#FF6B6B'),
                    ("Veículos", max(num_veiculos, 1), '#4ECDC4'),
                    ("Disponíveis", max(vagas_disponiveis, 1), '#45B7D1'),
                    ("Ocupadas", max(vagas_ocupadas, 1), '#96CEB4'),
                    ("Reservadas", max(vagas_reservadas, 1), '#FFEAA7')
                ]

                center_x, center_y = 175, 175
                radius = 80
                total = sum([item[1] for item in dados])

                start_angle = 0
                for label, valor, cor in dados:
                    angle = (valor / total) * 360
                    
                    canvas.create_arc(center_x - radius, center_y - radius,
                                    center_x + radius, center_y + radius,
                                    start=start_angle, extent=angle, fill=cor, outline='white', width=2)
                    
                    mid_angle = math.radians(start_angle + angle/2)
                    label_x = center_x + (radius + 50) * math.cos(mid_angle)
                    label_y = center_y + (radius + 50) * math.sin(mid_angle)
                    
                    valor_real = [num_usuarios, num_veiculos, vagas_disponiveis, vagas_ocupadas, vagas_reservadas][dados.index((label, valor, cor))]
                    canvas.create_text(label_x, label_y, text=f"{label}\n{valor_real}", 
                                    font=('Arial', 10, 'bold'), anchor='center')
                    
                    start_angle += angle

                self.root.after(1000, update_chart)

            except Exception:
                return

        update_chart()

        data_frame = tk.Frame(content_frame, bg='#ffffff', bd=2, relief='groove')
        data_frame.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=10, pady=10)
        tk.Label(data_frame, text="Dados Recentes", font=('Arial', 16, 'bold'), bg='#ffffff', fg='#333').pack(pady=10)
        notebook = ttk.Notebook(data_frame)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)
        vagas_frame = tk.Frame(notebook, bg='#ffffff')
        notebook.add(vagas_frame, text="Vagas Disponíveis")
        self._insert_treeview_section(
            vagas_frame,
            columns=("ID", "Localização", "Tipo"),
            headings=("ID", "Localização", "Tipo"),
            fetch_method=self.vaga.listar_disponiveis,
            value_extractor=lambda vaga: (vaga['id_vaga'], vaga['localizacao'], vaga['tipo']),
            no_data_text="Nenhuma vaga disponível no momento."
        )
        ocupacoes_frame = tk.Frame(notebook, bg='#ffffff')
        notebook.add(ocupacoes_frame, text="Ocupações Ativas")
        def fetch_ocupacoes():
            query = """SELECT o.id_ocupacao, v.placa, vg.localizacao, o.data_entrada, o.data_saida
                      FROM OCUPACAO o
                      JOIN VEICULO v ON o.id_veiculo = v.id_veiculo
                      JOIN VAGA vg ON o.id_vaga = vg.id_vaga
                      WHERE o.data_saida IS NULL"""
            cursor = self.estacionamento.connection.cursor(dictionary=True)
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            return data
        self._insert_treeview_section(
            ocupacoes_frame,
            columns=("ID", "Placa", "Vaga", "Entrada", "Saída"),
            headings=("ID", "Placa", "Vaga", "Entrada", "Saída"),
            fetch_method=fetch_ocupacoes,
            value_extractor=lambda oc: (oc['id_ocupacao'], oc['placa'], oc['localizacao'], str(oc['data_entrada']), str(oc['data_saida']) if oc['data_saida'] else "Ainda não saiu"),
            no_data_text="Nenhuma ocupação ativa no momento."
        )
        reservas_frame = tk.Frame(notebook, bg='#ffffff')
        notebook.add(reservas_frame, text="Reservas Ativas")
        def fetch_reservas():
            query = """
                SELECT r.id_reserva, r.id_vaga, r.data_inicio, r.data_fim, r.status,
                    COALESCE(a.nome, p.nome, f.nome, vi.nome) AS nome_usuario,
                    CASE
                        WHEN r.id_aluno IS NOT NULL THEN 'Aluno'
                        WHEN r.id_professor IS NOT NULL THEN 'Professor'
                        WHEN r.id_funcionario IS NOT NULL THEN 'Funcionário'
                        WHEN r.id_visitante IS NOT NULL THEN 'Visitante'
                    END AS tipo_usuario
                FROM RESERVA r
                LEFT JOIN ALUNO a ON r.id_aluno = a.id_aluno
                LEFT JOIN PROFESSOR p ON r.id_professor = p.id_professor
                LEFT JOIN FUNCIONARIO f ON r.id_funcionario = f.id_funcionario
                LEFT JOIN VISITANTE vi ON r.id_visitante = vi.id_visitante
                WHERE r.status = 'ativa'
            """
            cursor = self.estacionamento.connection.cursor(dictionary=True)
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            return data
        self._insert_treeview_section(
            reservas_frame,
            columns=("ID", "Vaga", "Usuário", "Tipo", "Início", "Fim", "Status"),
            headings=("ID", "Vaga", "Usuário", "Tipo", "Início", "Fim", "Status"),
            fetch_method=fetch_reservas,
            value_extractor=lambda r: (
                r['id_reserva'],
                r['id_vaga'],
                r['nome_usuario'],
                r['tipo_usuario'],
                str(r['data_inicio']),
                str(r['data_fim']),
                r['status']
            ),
            no_data_text="Nenhuma reserva ativa no momento."
        )
        relatorios_frame = tk.Frame(notebook, bg='#ffffff')
        notebook.add(relatorios_frame, text="Relatórios")
        relatorio_buttons = tk.Frame(relatorios_frame, bg='#ffffff')
        relatorio_buttons.pack(pady=10)
        relatorio_buttons.grid_columnconfigure(0, weight=1)
        relatorio_buttons.grid_columnconfigure(1, weight=1)
        relatorio_buttons.grid_columnconfigure(2, weight=1)
        relatorio_buttons.grid_columnconfigure(3, weight=1)
        relatorios = [
            ("Vagas Disponíveis", self.show_vagas_disponiveis),
            ("Ocupações Ativas", self.show_ocupacoes_ativas),
            ("Histórico Ocupações", self.show_historico_ocupacoes),
            ("Todos os Usuários", self.show_usuarios),
            ("Todos os Veículos", self.show_veiculos),
            ("Todas as Reservas", self.show_reservas),
            ("Todas as Vagas", self.show_vagas),
            ("Relatório Completo", self.show_relatorio_completo),
        ]
        for i, (text, command) in enumerate(relatorios):
            btn = ttk.Button(relatorio_buttons, text=text, command=lambda cmd=command: self.open_popup(cmd), style='TButton')
            btn.grid(row=i//4, column=i%4, padx=5, pady=5, sticky='ew')

    def open_popup(self, command):
        popup = tk.Toplevel(self.root)
        popup.title("Ação")
        popup.geometry("600x400")
        popup.configure(bg='#f0f2f5')
        self.current_frame = tk.Frame(popup, bg='#f0f2f5')
        self.current_frame.pack(expand=True, fill='both', padx=20, pady=20)
        command()
        self.current_frame = None

    def show_cadastrar_usuario(self):
        self.clear_window()
        self.current_frame = tk.Frame(self.root, bg='#f0f2f5')
        self.current_frame.pack(expand=True, fill='both', padx=50, pady=50)
        tk.Label(self.current_frame, text="Cadastrar Usuário", font=('Arial', 18, 'bold'), bg='#f0f2f5', fg='#333').pack(pady=20)
        form_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        form_frame.pack(expand=True)
        tk.Label(form_frame, text="Tipo:", bg='#f0f2f5', font=('Arial', 12)).grid(row=0, column=0, sticky='w', pady=5)
        self.tipo_usuario = ttk.Combobox(form_frame, values=[" ALUNO", " PROFESSOR", " FUNCIONÁRIO", " VISITANTE"], style='TCombobox')
        self.tipo_usuario.grid(row=0, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="Nome completo:", bg='#f0f2f5', font=('Arial', 12)).grid(row=1, column=0, sticky='w', pady=5)
        self.nome_usuario = tk.Entry(form_frame, font=('Arial', 12))
        self.nome_usuario.grid(row=1, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="Telefone:", bg='#f0f2f5', font=('Arial', 12)).grid(row=2, column=0, sticky='w', pady=5)
        self.telefone_usuario = tk.Entry(form_frame, font=('Arial', 12))
        self.telefone_usuario.grid(row=2, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="Email:", bg='#f0f2f5', font=('Arial', 12)).grid(row=3, column=0, sticky='w', pady=5)
        self.email_usuario = tk.Entry(form_frame, font=('Arial', 12))
        self.email_usuario.grid(row=3, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="Documento (CPF/RG):", bg='#f0f2f5', font=('Arial', 12)).grid(row=4, column=0, sticky='w', pady=5)
        self.documento_usuario = tk.Entry(form_frame, font=('Arial', 12))
        self.documento_usuario.grid(row=4, column=1, pady=5, sticky='ew')
        self.matricula_label = tk.Label(form_frame, text="Matrícula:", bg='#f0f2f5', font=('Arial', 12))
        self.matricula_entry = tk.Entry(form_frame, font=('Arial', 12))
        def toggle_matricula(event):
            if self.tipo_usuario.get() == " ALUNO":
                self.matricula_label.grid(row=5, column=0, sticky='w', pady=5)
                self.matricula_entry.grid(row=5, column=1, pady=5, sticky='ew')
            else:
                self.matricula_label.grid_forget()
                self.matricula_entry.grid_forget()
        self.tipo_usuario.bind("<<ComboboxSelected>>", toggle_matricula)
        button_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Cadastrar", command=self.cadastrar_usuario, bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Voltar", command=self.create_dashboard, bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(side=tk.LEFT, padx=10)

    def cadastrar_usuario(self):
        tipo = self.tipo_usuario.get().strip().lower()
        nome = self.nome_usuario.get().strip()
        telefone = self.telefone_usuario.get().strip()
        email = self.email_usuario.get().strip()
        documento = self.documento_usuario.get().strip()
        matricula = self.matricula_entry.get().strip() if tipo == "aluno" else None
        if not all([tipo, nome, telefone, email, documento]):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return
        if tipo == "aluno" and not matricula:
            messagebox.showerror("Erro", "Matrícula é obrigatória para alunos!")
            return
        if tipo not in ['aluno', 'professor', 'funcionario', 'visitante']:
            messagebox.showerror("Erro", "Tipo de usuário inválido!")
            return
        try:
            user_id = self.usuario.cadastrar_usuario(tipo, nome, telefone, email, documento, matricula)
            if user_id:
                messagebox.showinfo("Sucesso", f"{tipo.capitalize()} cadastrado com sucesso! ID: {user_id}")
                self.create_dashboard()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao cadastrar usuário: {str(e)}")

    def show_cadastrar_veiculo(self):
        self.clear_window()
        self.current_frame = tk.Frame(self.root, bg='#f0f2f5')
        self.current_frame.pack(expand=True, fill='both', padx=50, pady=50)
        tk.Label(self.current_frame, text="Cadastrar Veículo", font=('Arial', 18, 'bold'), bg='#f0f2f5', fg='#333').pack(pady=20)
        form_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        form_frame.pack(expand=True)
        tk.Label(form_frame, text="Placa:", bg='#f0f2f5', font=('Arial', 12)).grid(row=0, column=0, sticky='w', pady=5)
        self.placa_veiculo = tk.Entry(form_frame, font=('Arial', 12))
        self.placa_veiculo.grid(row=0, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="Modelo:", bg='#f0f2f5', font=('Arial', 12)).grid(row=1, column=0, sticky='w', pady=5)
        self.modelo_veiculo = tk.Entry(form_frame, font=('Arial', 12))
        self.modelo_veiculo.grid(row=1, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="Tipo do proprietário:", bg='#f0f2f5', font=('Arial', 12)).grid(row=2, column=0, sticky='w', pady=5)
        self.tipo_proprietario = ttk.Combobox(form_frame, values=[" ALUNO", " PROFESSOR", " FUNCIONÁRIO", " VISITANTE"], style='TCombobox')
        self.tipo_proprietario.grid(row=2, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="ID do proprietário:", bg='#f0f2f5', font=('Arial', 12)).grid(row=3, column=0, sticky='w', pady=5)
        self.id_proprietario = tk.Entry(form_frame, font=('Arial', 12))
        self.id_proprietario.grid(row=3, column=1, pady=5, sticky='ew')
        button_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Cadastrar", command=self.cadastrar_veiculo, bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Voltar", command=self.create_dashboard, bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(side=tk.LEFT, padx=10)

    def cadastrar_veiculo(self):
        placa = self.placa_veiculo.get().strip()
        modelo = self.modelo_veiculo.get().strip()
        tipo_usuario = self.tipo_proprietario.get().strip().lower()
        id_usuario = self.id_proprietario.get().strip()
        if not all([placa, modelo, tipo_usuario, id_usuario]):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return
        if tipo_usuario not in ['aluno', 'professor', 'funcionario', 'visitante']:
            messagebox.showerror("Erro", "Tipo de usuário inválido!")
            return
        try:
            id_usuario = int(id_usuario)
            veiculo_id = self.veiculo.cadastrar_veiculo(placa, modelo, tipo_usuario, id_usuario)
            if veiculo_id:
                messagebox.showinfo("Sucesso", f"Veículo cadastrado com sucesso! ID: {veiculo_id}")
                self.create_dashboard()
            else:
                messagebox.showerror("Erro", "Falha ao cadastrar veículo: ID do usuário inválido ou não encontrado.")
        except ValueError:
            messagebox.showerror("Erro", "ID do usuário deve ser um número!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao cadastrar veículo: {str(e)}")

    def show_cadastrar_vaga(self):
        self.clear_window()
        self.current_frame = tk.Frame(self.root, bg='#f0f2f5')
        self.current_frame.pack(expand=True, fill='both', padx=50, pady=50)
        tk.Label(self.current_frame, text="Cadastrar Vaga", font=('Arial', 18, 'bold'), bg='#f0f2f5', fg='#333').pack(pady=20)
        form_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        form_frame.pack(expand=True)
        tk.Label(form_frame, text="Localização (ex: A12):", bg='#f0f2f5', font=('Arial', 12)).grid(row=0, column=0, sticky='w', pady=5)
        self.localizacao_vaga = tk.Entry(form_frame, font=('Arial', 12))
        self.localizacao_vaga.grid(row=0, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="Tipo:", bg='#f0f2f5', font=('Arial', 12)).grid(row=1, column=0, sticky='w', pady=5)
        self.tipo_vaga = ttk.Combobox(form_frame, values=[" COMUM", " IDOSO", " DEFICIENTE"], style='TCombobox')
        self.tipo_vaga.grid(row=1, column=1, pady=5, sticky='ew')
        button_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Cadastrar", command=self.cadastrar_vaga, bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Voltar", command=self.create_dashboard, bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(side=tk.LEFT, padx=10)

    def cadastrar_vaga(self):
        localizacao = self.localizacao_vaga.get().strip()
        tipo = self.tipo_vaga.get().strip().lower()
        if not all([localizacao, tipo]):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return
        valid_types = ['comum', 'idoso', 'deficiente']
        if tipo not in valid_types:
            messagebox.showerror("Erro", f"Tipo de vaga inválido! Escolha entre {', '.join(valid_types)}.")
            return
        try:
            vaga_id = self.vaga.cadastrar_vaga(localizacao, tipo=tipo, estado='disponivel')
            if vaga_id:
                messagebox.showinfo("Sucesso", f"Vaga cadastrada com sucesso! ID: {vaga_id}")
                self.create_dashboard()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao cadastrar vaga: {str(e)}")

    def show_reservar_vaga(self):
        self.clear_window()
        self.current_frame = tk.Frame(self.root, bg='#f0f2f5')
        self.current_frame.pack(expand=True, fill='both', padx=50, pady=50)
        tk.Label(self.current_frame, text="Reservar Vaga", font=('Arial', 18, 'bold'), bg='#f0f2f5', fg='#333').pack(pady=20)
        form_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        form_frame.pack(expand=True)
        tk.Label(form_frame, text="Tipo do usuário:", bg='#f0f2f5', font=('Arial', 12)).grid(row=0, column=0, sticky='w', pady=5)
        self.reserva_tipo_usuario = ttk.Combobox(form_frame, values=[" ALUNO", " PROFESSOR", " FUNCIONÁRIO", " VISITANTE"], style='TCombobox')
        self.reserva_tipo_usuario.grid(row=0, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="ID do usuário:", bg='#f0f2f5', font=('Arial', 12)).grid(row=1, column=0, sticky='w', pady=5)
        self.reserva_id_usuario = tk.Entry(form_frame, font=('Arial', 12))
        self.reserva_id_usuario.grid(row=1, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="ID da vaga:", bg='#f0f2f5', font=('Arial', 12)).grid(row=2, column=0, sticky='w', pady=5)
        self.reserva_id_vaga = tk.Entry(form_frame, font=('Arial', 12))
        self.reserva_id_vaga.grid(row=2, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="Data/hora início (AAAA-MM-DD HH:MM):", bg='#f0f2f5', font=('Arial', 12)).grid(row=3, column=0, sticky='w', pady=5)
        self.reserva_data_inicio = tk.Entry(form_frame, font=('Arial', 12))
        self.reserva_data_inicio.grid(row=3, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="Data/hora fim (AAAA-MM-DD HH:MM):", bg='#f0f2f5', font=('Arial', 12)).grid(row=4, column=0, sticky='w', pady=5)
        self.reserva_data_fim = tk.Entry(form_frame, font=('Arial', 12))
        self.reserva_data_fim.grid(row=4, column=1, pady=5, sticky='ew')
        button_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Reservar", command=self.reservar_vaga, bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Voltar", command=self.create_dashboard, bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(side=tk.LEFT, padx=10)

    def reservar_vaga(self):
        tipo_usuario = self.reserva_tipo_usuario.get().strip().lower()
        id_usuario = self.reserva_id_usuario.get().strip()
        id_vaga = self.reserva_id_vaga.get().strip()
        data_inicio = self.reserva_data_inicio.get().strip()
        data_fim = self.reserva_data_fim.get().strip()
        if not all([tipo_usuario, id_usuario, id_vaga, data_inicio, data_fim]):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return
        if tipo_usuario not in ['aluno', 'professor', 'funcionario', 'visitante']:
            messagebox.showerror("Erro", "Tipo de usuário inválido!")
            return
        try:
            id_usuario = int(id_usuario)
            id_vaga = int(id_vaga)
            datetime.strptime(data_inicio, "%Y-%m-%d %H:%M")
            datetime.strptime(data_fim, "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Erro", "IDs devem ser números e datas devem estar no formato AAAA-MM-DD HH:MM!")
            return
        cursor = self.estacionamento.connection.cursor()
        try:
            query = "SELECT estado FROM VAGA WHERE id_vaga = %s"
            cursor.execute(query, (id_vaga,))
            result = cursor.fetchone()
            if not result:
                raise Exception("Vaga não encontrada!")
            if result[0] != 'disponivel':
                raise Exception("Vaga não está disponível!")
            query = """
                SELECT COUNT(*) FROM RESERVA
                WHERE id_vaga = %s
                AND status = 'ativa'
                AND (
                    (%s <= data_fim AND %s >= data_inicio)
                    OR (%s <= data_fim AND %s >= data_inicio)
                    OR (data_inicio <= %s AND data_fim >= %s)
                )
            """
            cursor.execute(query, (id_vaga, data_inicio, data_inicio, data_fim, data_fim, data_inicio, data_fim))
            if cursor.fetchone()[0] > 0:
                raise Exception("Vaga já reservada no período solicitado!")
            query = "SELECT COUNT(*) FROM OCUPACAO WHERE id_vaga = %s AND data_saida IS NULL"
            cursor.execute(query, (id_vaga,))
            if cursor.fetchone()[0] > 0:
                raise Exception("Vaga está ocupada!")
            query = f"SELECT id_{tipo_usuario.lower()} FROM {tipo_usuario.upper()} WHERE id_{tipo_usuario.lower()} = %s"
            cursor.execute(query, (id_usuario,))
            if not cursor.fetchone():
                raise Exception(f"Usuário do tipo {tipo_usuario} com ID {id_usuario} não encontrado!")
            query = f"""
                INSERT INTO RESERVA (id_{tipo_usuario.lower()}, id_vaga, data_inicio, data_fim, status)
                VALUES (%s, %s, %s, %s, 'ativa')
            """
            cursor.execute(query, (id_usuario, id_vaga, data_inicio, data_fim))
            self.estacionamento.connection.commit()
            reserva_id = cursor.lastrowid
            query = "UPDATE VAGA SET estado = 'reservada' WHERE id_vaga = %s"
            cursor.execute(query, (id_vaga,))
            self.estacionamento.connection.commit()
            messagebox.showinfo("Sucesso", f"Reserva criada com sucesso! ID: {reserva_id}")
            self.create_dashboard()
        except Exception as e:
            self.estacionamento.connection.rollback()
            messagebox.showerror("Erro", f"Falha ao criar reserva: {str(e)}")
        finally:
            cursor.close()

    def show_registrar_entrada(self):
        self.clear_window()
        self.current_frame = tk.Frame(self.root, bg='#f0f2f5')
        self.current_frame.pack(expand=True, fill='both', padx=50, pady=50)
        tk.Label(self.current_frame, text="Registrar Entrada", font=('Arial', 18, 'bold'), bg='#f0f2f5', fg='#333').pack(pady=20)
        form_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        form_frame.pack(expand=True)
        tk.Label(form_frame, text="ID do veículo:", bg='#f0f2f5', font=('Arial', 12)).grid(row=0, column=0, sticky='w', pady=5)
        self.entrada_id_veiculo = tk.Entry(form_frame, font=('Arial', 12))
        self.entrada_id_veiculo.grid(row=0, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="ID da vaga:", bg='#f0f2f5', font=('Arial', 12)).grid(row=1, column=0, sticky='w', pady=5)
        self.entrada_id_vaga = tk.Entry(form_frame, font=('Arial', 12))
        self.entrada_id_vaga.grid(row=1, column=1, pady=5, sticky='ew')
        button_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Registrar", command=self.registrar_entrada, bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Voltar", command=self.create_dashboard, bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(side=tk.LEFT, padx=10)

    def registrar_entrada(self):
        id_veiculo = self.entrada_id_veiculo.get().strip()
        id_vaga = self.entrada_id_vaga.get().strip()
        if not all([id_veiculo, id_vaga]):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return
        try:
            id_veiculo = int(id_veiculo)
            id_vaga = int(id_vaga)
            ocupacao_id = self.ocupacao.registrar_entrada(id_veiculo, id_vaga)
            if ocupacao_id is not None:
                messagebox.showinfo("Sucesso", f"Entrada registrada com sucesso! ID da ocupação: {ocupacao_id}")
            else:
                messagebox.showinfo("Sucesso", "Entrada registrada com sucesso!")
            self.create_dashboard()
        except ValueError:
            messagebox.showerror("Erro", "IDs devem ser números!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao registrar entrada: {str(e)}")

    def show_registrar_saida(self):
        self.clear_window()
        self.current_frame = tk.Frame(self.root, bg='#f0f2f5')
        self.current_frame.pack(expand=True, fill='both', padx=50, pady=50)
        tk.Label(self.current_frame, text="Registrar Saída", font=('Arial', 18, 'bold'), bg='#f0f2f5', fg='#333').pack(pady=20)
        form_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        form_frame.pack(expand=True)
        tk.Label(form_frame, text="ID da ocupação:", bg='#f0f2f5', font=('Arial', 12)).grid(row=0, column=0, sticky='w', pady=5)
        self.saida_id_ocupacao = tk.Entry(form_frame, font=('Arial', 12))
        self.saida_id_ocupacao.grid(row=0, column=1, pady=5, sticky='ew')
        button_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Registrar", command=self.registrar_saida, bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Voltar", command=self.create_dashboard, bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(side=tk.LEFT, padx=10)

    def registrar_saida(self):
        id_ocupacao = self.saida_id_ocupacao.get().strip()
        if not id_ocupacao:
            messagebox.showerror("Erro", "ID da ocupação é obrigatório!")
            return
        try:
            id_ocupacao = int(id_ocupacao)
            if self.ocupacao.registrar_saida(id_ocupacao):
                messagebox.showinfo("Sucesso", "Saída registrada com sucesso!")
                self.create_dashboard()
            else:
                messagebox.showerror("Erro", "Não foi possível registrar a saída.")
        except ValueError:
            messagebox.showerror("Erro", "ID deve ser um número!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao registrar saída: {str(e)}")

    def show_vagas_disponiveis(self):
        self._show_treeview_report(
            title="Vagas Disponíveis",
            columns=("ID", "Localização", "Tipo"),
            fetch_method=self.vaga.listar_disponiveis,
            value_extractor=lambda vaga: (vaga['id_vaga'], vaga['localizacao'], vaga['tipo']),
            no_data_text="Nenhuma vaga disponível no momento."
        )

    def show_ocupacoes_ativas(self):
        def fetch_ocupacoes():
            query = """SELECT o.id_ocupacao, v.placa, vg.localizacao, o.data_entrada, o.data_saida
                      FROM OCUPACAO o
                      JOIN VEICULO v ON o.id_veiculo = v.id_veiculo
                      JOIN VAGA vg ON o.id_vaga = vg.id_vaga
                      WHERE o.data_saida IS NULL"""
            cursor = self.estacionamento.connection.cursor(dictionary=True)
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            return data
        self._show_treeview_report(
            title="Ocupações Ativas",
            columns=("ID", "Placa", "Vaga", "Entrada", "Saída"),
            fetch_method=fetch_ocupacoes,
            value_extractor=lambda oc: (oc['id_ocupacao'], oc['placa'], oc['localizacao'], str(oc['data_entrada']), str(oc['data_saida']) if oc['data_saida'] else "Ainda não saiu"),
            no_data_text="Nenhuma ocupação ativa no momento."
        )

    def show_usuarios(self):
        def fetch_usuarios():
            tipos = ['ALUNO', 'PROFESSOR', 'FUNCIONARIO', 'VISITANTE']
            usuarios = []
            cursor = self.estacionamento.connection.cursor(dictionary=True)
            for tipo in tipos:
                query = f"""
                    SELECT id_{tipo.lower()} AS id, nome, telefone, email, documento
                    {', matricula' if tipo == 'ALUNO' else ''}, '{tipo.capitalize()}' AS tipo
                    FROM {tipo}
                """
                cursor.execute(query)
                usuarios.extend(cursor.fetchall())
            cursor.close()
            return usuarios
        self._show_treeview_report(
            title="Todos os Usuários",
            columns=("ID", "Tipo", "Nome", "Telefone", "Email", "Documento", "Matrícula"),
            fetch_method=fetch_usuarios,
            value_extractor=lambda u: (
                u['id'],
                u['tipo'],
                u['nome'],
                u['telefone'],
                u['email'],
                u['documento'],
                u.get('matricula', '')
            ),
            no_data_text="Nenhum usuário cadastrado."
        )

    def show_veiculos(self):
        def fetch_veiculos():
            query = """
                SELECT v.id_veiculo, v.placa, v.modelo,
                    COALESCE(a.nome, p.nome, f.nome, vi.nome) AS nome_proprietario,
                    CASE
                        WHEN v.id_aluno IS NOT NULL THEN 'Aluno'
                        WHEN v.id_professor IS NOT NULL THEN 'Professor'
                        WHEN v.id_funcionario IS NOT NULL THEN 'Funcionário'
                        WHEN v.id_visitante IS NOT NULL THEN 'Visitante'
                    END AS tipo_usuario
                FROM VEICULO v
                LEFT JOIN ALUNO a ON v.id_aluno = a.id_aluno
                LEFT JOIN PROFESSOR p ON v.id_professor = p.id_professor
                LEFT JOIN FUNCIONARIO f ON v.id_funcionario = f.id_funcionario
                LEFT JOIN VISITANTE vi ON v.id_visitante = vi.id_visitante
            """
            cursor = self.estacionamento.connection.cursor(dictionary=True)
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            return data
        self._show_treeview_report(
            title="Todos os Veículos",
            columns=("ID", "Placa", "Modelo", "Proprietário", "Tipo"),
            fetch_method=fetch_veiculos,
            value_extractor=lambda v: (
                v['id_veiculo'],
                v['placa'],
                v['modelo'],
                v['nome_proprietario'],
                v['tipo_usuario']
            ),
            no_data_text="Nenhum veículo cadastrado."
        )

    def show_reservas(self):
        def fetch_reservas():
            query = """
                SELECT r.id_reserva, r.id_vaga, r.data_inicio, r.data_fim, r.status,
                    COALESCE(a.nome, p.nome, f.nome, vi.nome) AS nome_usuario,
                    CASE
                        WHEN r.id_aluno IS NOT NULL THEN 'Aluno'
                        WHEN r.id_professor IS NOT NULL THEN 'Professor'
                        WHEN r.id_funcionario IS NOT NULL THEN 'Funcionário'
                        WHEN r.id_visitante IS NOT NULL THEN 'Visitante'
                    END AS tipo_usuario
                FROM RESERVA r
                LEFT JOIN ALUNO a ON r.id_aluno = a.id_aluno
                LEFT JOIN PROFESSOR p ON r.id_professor = p.id_professor
                LEFT JOIN FUNCIONARIO f ON r.id_funcionario = f.id_funcionario
                LEFT JOIN VISITANTE vi ON r.id_visitante = vi.id_visitante
            """
            cursor = self.estacionamento.connection.cursor(dictionary=True)
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            return data
        self._show_treeview_report(
            title="Todas as Reservas",
            columns=("ID", "Vaga", "Usuário", "Tipo", "Início", "Fim", "Status"),
            fetch_method=fetch_reservas,
            value_extractor=lambda r: (
                r['id_reserva'],
                r['id_vaga'],
                r['nome_usuario'],
                r['tipo_usuario'],
                str(r['data_inicio']),
                str(r['data_fim']),
                r['status']
            ),
            no_data_text="Nenhuma reserva cadastrada."
        )

    def show_vagas(self):
        def fetch_vagas():
            query = "SELECT id_vaga, localizacao, estado, tipo FROM VAGA"
            cursor = self.estacionamento.connection.cursor(dictionary=True)
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            return data
        self._show_treeview_report(
            title="Todas as Vagas",
            columns=("ID", "Localização", "Estado", "Tipo"),
            fetch_method=fetch_vagas,
            value_extractor=lambda v: (
                v['id_vaga'],
                v['localizacao'],
                v['estado'],
                v['tipo']
            ),
            no_data_text="Nenhuma vaga cadastrada."
        )

    def show_relatorio_completo(self):
        self.clear_window()
        self.current_frame = tk.Frame(self.root, bg='#f0f2f5')
        self.current_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
        canvas = tk.Canvas(self.current_frame, bg='#f0f2f5')
        scrollbar = ttk.Scrollbar(self.current_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f2f5')
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        def separator():
            tk.Label(scrollable_frame, text=" ", font=('Arial', 6), bg='#f0f2f5').pack()
        tk.Label(scrollable_frame, text="Vagas Disponíveis", font=('Arial', 14, 'bold'), bg='#f0f2f5', fg='#333').pack(pady=8)
        self._insert_treeview_section(
            scrollable_frame,
            columns=("ID", "Localização", "Tipo"),
            headings=("ID", "Localização", "Tipo"),
            fetch_method=self.vaga.listar_disponiveis,
            value_extractor=lambda vaga: (vaga['id_vaga'], vaga['localizacao'], vaga['tipo']),
            no_data_text="Nenhuma vaga disponível no momento."
        )
        separator()
        tk.Label(scrollable_frame, text="Ocupações Ativas", font=('Arial', 14, 'bold'), bg='#f0f2f5', fg='#333').pack(pady=8)
        def fetch_ocupacoes():
            query = """SELECT o.id_ocupacao, v.placa, vg.localizacao, o.data_entrada, o.data_saida
                    FROM OCUPACAO o
                    JOIN VEICULO v ON o.id_veiculo = v.id_veiculo
                    JOIN VAGA vg ON o.id_vaga = vg.id_vaga
                    WHERE o.data_saida IS NULL"""
            cursor = self.estacionamento.connection.cursor(dictionary=True)
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            return data
        self._insert_treeview_section(
            scrollable_frame,
            columns=("ID", "Placa", "Vaga", "Entrada", "Saída"),
            headings=("ID", "Placa", "Vaga", "Entrada", "Saída"),
            fetch_method=fetch_ocupacoes,
            value_extractor=lambda oc: (oc['id_ocupacao'], oc['placa'], oc['localizacao'], str(oc['data_entrada']), str(oc['data_saida']) if oc['data_saida'] else "Ainda não saiu"),
            no_data_text="Nenhuma ocupação ativa no momento."
        )
        separator()
        tk.Label(scrollable_frame, text="Histórico de Entradas e Saídas", font=('Arial', 14, 'bold'), bg='#f0f2f5', fg='#333').pack(pady=8)
        def fetch_historico_ocupacoes():
            query = """SELECT o.id_ocupacao, v.placa, vg.localizacao, o.data_entrada, o.data_saida
                       FROM OCUPACAO o
                       JOIN VEICULO v ON o.id_veiculo = v.id_veiculo
                       JOIN VAGA vg ON o.id_vaga = vg.id_vaga
                       ORDER BY o.data_entrada DESC"""
            cursor = self.estacionamento.connection.cursor(dictionary=True)
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            return data
        self._insert_treeview_section(
            scrollable_frame,
            columns=("ID", "Placa", "Vaga", "Entrada", "Saída"),
            headings=("ID", "Placa", "Vaga", "Entrada", "Saída"),
            fetch_method=fetch_historico_ocupacoes,
            value_extractor=lambda oc: (
                oc['id_ocupacao'],
                oc['placa'],
                oc['localizacao'],
                oc['data_entrada'].strftime("%Y-%m-%d %H:%M") if oc['data_entrada'] else "-",
                oc['data_saida'].strftime("%Y-%m-%d %H:%M") if oc['data_saida'] else "-"
            ),
            no_data_text="Nenhum histórico encontrado."
        )
        separator()
        tk.Label(scrollable_frame, text="Todos os Usuários", font=('Arial', 14, 'bold'), bg='#f0f2f5', fg='#333').pack(pady=8)
        def fetch_usuarios():
            tipos = ['ALUNO', 'PROFESSOR', 'FUNCIONARIO', 'VISITANTE']
            usuarios = []
            cursor = self.estacionamento.connection.cursor(dictionary=True)
            for tipo in tipos:
                query = f"""
                    SELECT id_{tipo.lower()} AS id, nome, telefone, email, documento
                    {', matricula' if tipo == 'ALUNO' else ''}, '{tipo.capitalize()}' AS tipo
                    FROM {tipo}
                """
                cursor.execute(query)
                usuarios.extend(cursor.fetchall())
            cursor.close()
            return usuarios
        self._insert_treeview_section(
            scrollable_frame,
            columns=("ID", "Tipo", "Nome", "Telefone", "Email", "Documento", "Matrícula"),
            headings=("ID", "Tipo", "Nome", "Telefone", "Email", "Documento", "Matrícula"),
            fetch_method=fetch_usuarios,
            value_extractor=lambda u: (
                u['id'],
                u['tipo'],
                u['nome'],
                u['telefone'],
                u['email'],
                u['documento'],
                u.get('matricula', '')
            ),
            no_data_text="Nenhum usuário cadastrado."
        )
        separator()
        tk.Label(scrollable_frame, text="Todos os Veículos", font=('Arial', 14, 'bold'), bg='#f0f2f5', fg='#333').pack(pady=8)
        def fetch_veiculos():
            query = """
                SELECT v.id_veiculo, v.placa, v.modelo,
                    COALESCE(a.nome, p.nome, f.nome, vi.nome) AS nome_proprietario,
                    CASE
                        WHEN v.id_aluno IS NOT NULL THEN 'Aluno'
                        WHEN v.id_professor IS NOT NULL THEN 'Professor'
                        WHEN v.id_funcionario IS NOT NULL THEN 'Funcionário'
                        WHEN v.id_visitante IS NOT NULL THEN 'Visitante'
                    END AS tipo_usuario
                FROM VEICULO v
                LEFT JOIN ALUNO a ON v.id_aluno = a.id_aluno
                LEFT JOIN PROFESSOR p ON v.id_professor = p.id_professor
                LEFT JOIN FUNCIONARIO f ON v.id_funcionario = f.id_funcionario
                LEFT JOIN VISITANTE vi ON v.id_visitante = vi.id_visitante
            """
            cursor = self.estacionamento.connection.cursor(dictionary=True)
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            return data
        self._insert_treeview_section(
            scrollable_frame,
            columns=("ID", "Placa", "Modelo", "Proprietário", "Tipo"),
            headings=("ID", "Placa", "Modelo", "Proprietário", "Tipo"),
            fetch_method=fetch_veiculos,
            value_extractor=lambda v: (
                v['id_veiculo'],
                v['placa'],
                v['modelo'],
                v['nome_proprietario'],
                v['tipo_usuario']
            ),
            no_data_text="Nenhum veículo cadastrado."
        )
        separator()
        tk.Label(scrollable_frame, text="Todas as Reservas", font=('Arial', 14, 'bold'), bg='#f0f2f5', fg='#333').pack(pady=8)
        def fetch_reservas():
            query = """
                SELECT r.id_reserva, r.id_vaga, r.data_inicio, r.data_fim, r.status,
                    COALESCE(a.nome, p.nome, f.nome, vi.nome) AS nome_usuario,
                    CASE
                        WHEN r.id_aluno IS NOT NULL THEN 'Aluno'
                        WHEN r.id_professor IS NOT NULL THEN 'Professor'
                        WHEN r.id_funcionario IS NOT NULL THEN 'Funcionário'
                        WHEN r.id_visitante IS NOT NULL THEN 'Visitante'
                    END AS tipo_usuario
                FROM RESERVA r
                LEFT JOIN ALUNO a ON r.id_aluno = a.id_aluno
                LEFT JOIN PROFESSOR p ON r.id_professor = p.id_professor
                LEFT JOIN FUNCIONARIO f ON r.id_funcionario = f.id_funcionario
                LEFT JOIN VISITANTE vi ON r.id_visitante = vi.id_visitante
            """
            cursor = self.estacionamento.connection.cursor(dictionary=True)
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            return data
        self._insert_treeview_section(
            scrollable_frame,
            columns=("ID", "Vaga", "Usuário", "Tipo", "Início", "Fim", "Status"),
            headings=("ID", "Vaga", "Usuário", "Tipo", "Início", "Fim", "Status"),
            fetch_method=fetch_reservas,
            value_extractor=lambda r: (
                r['id_reserva'],
                r['id_vaga'],
                r['nome_usuario'],
                r['tipo_usuario'],
                str(r['data_inicio']),
                str(r['data_fim']),
                r['status']
            ),
            no_data_text="Nenhuma reserva cadastrada."
        )
        separator()
        tk.Label(scrollable_frame, text="Todas as Vagas", font=('Arial', 14, 'bold'), bg='#f0f2f5', fg='#333').pack(pady=8)
        def fetch_vagas():
            query = "SELECT id_vaga, localizacao, estado, tipo FROM VAGA"
            cursor = self.estacionamento.connection.cursor(dictionary=True)
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            return data
        self._insert_treeview_section(
            scrollable_frame,
            columns=("ID", "Localização", "Estado", "Tipo"),
            headings=("ID", "Localização", "Estado", "Tipo"),
            fetch_method=fetch_vagas,
            value_extractor=lambda v: (
                v['id_vaga'],
                v['localizacao'],
                v['estado'],
                v['tipo']
            ),
            no_data_text="Nenhuma vaga cadastrada."
        )
        tk.Button(scrollable_frame, text="Voltar", command=self.create_dashboard, bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(pady=20)

    def _insert_treeview_section(self, parent, columns, headings, fetch_method, value_extractor, no_data_text):
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=7)
        for col, head in zip(columns, headings):
            tree.heading(col, text=head)
            tree.column(col, width=175, anchor=tk.CENTER)
        tree.pack(fill=tk.X, padx=15, pady=6)
        try:
            data = fetch_method()
            if data:
                for item in data:
                    tree.insert("", tk.END, values=value_extractor(item))
            else:
                tk.Label(parent, text=no_data_text, font=('Arial', 11, 'italic'), bg='#f0f2f5').pack()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar dados: {str(e)}")

    def _show_treeview_report(self, title, columns, fetch_method, value_extractor, no_data_text):
        self.clear_window()
        self.current_frame = tk.Frame(self.root, bg='#f0f2f5')
        self.current_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
        tk.Label(self.current_frame, text=title, font=('Arial', 16, 'bold'), bg='#f0f2f5', fg='#333').pack(pady=12)
        tree = ttk.Treeview(self.current_frame, columns=columns, show="headings", height=15)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor=tk.CENTER, width=120)
        tree.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(self.current_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        try:
            data = fetch_method()
            if data:
                for item in data:
                    tree.insert("", tk.END, values=value_extractor(item))
            else:
                tk.Label(self.current_frame, text=no_data_text, font=('Arial', 12, 'italic'), bg='#f0f2f5').pack(pady=10)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao listar dados: {str(e)}")
        tk.Button(self.current_frame, text="Voltar", command=self.create_dashboard, bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(pady=15)

    def show_historico_ocupacoes(self):
        self.clear_window()
        self.current_frame = tk.Frame(self.root, bg='#f0f2f5')
        self.current_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
        tk.Label(self.current_frame, text="Histórico de Entradas e Saídas", font=('Arial', 16, 'bold'), bg='#f0f2f5', fg='#333').pack(pady=12)
        columns = ("ID", "Placa", "Vaga", "Entrada", "Saída")
        tree = ttk.Treeview(self.current_frame, columns=columns, show="headings", height=20)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor=tk.CENTER, width=130)
        tree.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(self.current_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        try:
            query = """SELECT o.id_ocupacao, v.placa, vg.localizacao, o.data_entrada, o.data_saida
                    FROM OCUPACAO o
                    JOIN VEICULO v ON o.id_veiculo = v.id_veiculo
                    JOIN VAGA vg ON o.id_vaga = vg.id_vaga
                    ORDER BY o.data_entrada DESC"""
            cursor = self.estacionamento.connection.cursor(dictionary=True)
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            if data:
                for oc in data:
                    entrada = oc['data_entrada'].strftime("%Y-%m-%d %H:%M") if oc['data_entrada'] else "-"
                    saida = oc['data_saida'].strftime("%Y-%m-%d %H:%M") if oc['data_saida'] else "-"
                    tree.insert("", tk.END, values=(
                        oc['id_ocupacao'],
                        oc['placa'],
                        oc['localizacao'],
                        entrada,
                        saida
                    ))
            else:
                tk.Label(self.current_frame, text="Nenhum histórico encontrado.", font=('Arial', 12, 'italic'), bg='#f0f2f5').pack(pady=10)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar histórico: {str(e)}")
        tk.Button(self.current_frame, text="Voltar", command=self.create_dashboard, bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(pady=15)

    def show_editar_dados(self):
        self.clear_window()
        self.current_frame = tk.Frame(self.root, bg='#f0f2f5')
        self.current_frame.pack(expand=True, fill='both', padx=50, pady=50)
        tk.Label(self.current_frame, text="Editar Dados", font=('Arial', 18, 'bold'), bg='#f0f2f5', fg='#333').pack(pady=20)
        form_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        form_frame.pack(expand=True)
        tk.Label(form_frame, text="Tipo de dado:", bg='#f0f2f5', font=('Arial', 12)).grid(row=0, column=0, sticky='w', pady=5)
        self.editar_tipo_dado = ttk.Combobox(form_frame, values=["ALUNO", "PROFESSOR", "FUNCIONARIO", "VISITANTE", "VEICULO", "VAGA", "RESERVA", "OCUPACAO"], style='TCombobox')
        self.editar_tipo_dado.grid(row=0, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="ID do registro:", bg='#f0f2f5', font=('Arial', 12)).grid(row=1, column=0, sticky='w', pady=5)
        self.editar_id_registro = tk.Entry(form_frame, font=('Arial', 12))
        self.editar_id_registro.grid(row=1, column=1, pady=5, sticky='ew')
        button_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Carregar Dados", command=self.carregar_dados_para_edicao, bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Voltar", command=self.create_dashboard, bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(side=tk.LEFT, padx=10)

    def carregar_dados_para_edicao(self):
        tipo_dado = self.editar_tipo_dado.get().strip().upper()
        id_registro = self.editar_id_registro.get().strip()
        if not tipo_dado or not id_registro:
            messagebox.showerror("Erro", "Tipo de dado e ID são obrigatórios!")
            return
        try:
            id_registro = int(id_registro)
        except ValueError:
            messagebox.showerror("Erro", "ID deve ser um número!")
            return
        cursor = self.estacionamento.connection.cursor(dictionary=True)
        try:
            if tipo_dado in ['ALUNO', 'PROFESSOR', 'FUNCIONARIO', 'VISITANTE']:
                query = f"SELECT * FROM {tipo_dado} WHERE id_{tipo_dado.lower()} = %s"
                cursor.execute(query, (id_registro,))
                registro = cursor.fetchone()
                if not registro:
                    messagebox.showerror("Erro", f"Registro {tipo_dado} com ID {id_registro} não encontrado!")
                    return
                self.show_formulario_edicao_usuario(tipo_dado, registro)
            elif tipo_dado == 'VEICULO':
                query = """
                    SELECT v.*, COALESCE(a.id_aluno, p.id_professor, f.id_funcionario, vi.id_visitante) AS id_usuario,
                        CASE
                            WHEN v.id_aluno IS NOT NULL THEN 'ALUNO'
                            WHEN v.id_professor IS NOT NULL THEN 'PROFESSOR'
                            WHEN v.id_funcionario IS NOT NULL THEN 'FUNCIONARIO'
                            WHEN v.id_visitante IS NOT NULL THEN 'VISITANTE'
                        END AS tipo_usuario
                    FROM VEICULO v
                    LEFT JOIN ALUNO a ON v.id_aluno = a.id_aluno
                    LEFT JOIN PROFESSOR p ON v.id_professor = p.id_professor
                    LEFT JOIN FUNCIONARIO f ON v.id_funcionario = f.id_funcionario
                    LEFT JOIN VISITANTE vi ON v.id_visitante = vi.id_visitante
                    WHERE v.id_veiculo = %s
                """
                cursor.execute(query, (id_registro,))
                registro = cursor.fetchone()
                if not registro:
                    messagebox.showerror("Erro", f"Veículo com ID {id_registro} não encontrado!")
                    return
                self.show_formulario_edicao_veiculo(registro)
            elif tipo_dado == 'VAGA':
                query = "SELECT * FROM VAGA WHERE id_vaga = %s"
                cursor.execute(query, (id_registro,))
                registro = cursor.fetchone()
                if not registro:
                    messagebox.showerror("Erro", f"Vaga com ID {id_registro} não encontrada!")
                    return
                self.show_formulario_edicao_vaga(registro)
            elif tipo_dado == 'RESERVA':
                query = """
                    SELECT r.*, COALESCE(a.id_aluno, p.id_professor, f.id_funcionario, vi.id_visitante) AS id_usuario,
                        CASE
                            WHEN r.id_aluno IS NOT NULL THEN 'ALUNO'
                            WHEN r.id_professor IS NOT NULL THEN 'PROFESSOR'
                            WHEN r.id_funcionario IS NOT NULL THEN 'FUNCIONARIO'
                            WHEN r.id_visitante IS NOT NULL THEN 'VISITANTE'
                        END AS tipo_usuario
                    FROM RESERVA r
                    LEFT JOIN ALUNO a ON r.id_aluno = a.id_aluno
                    LEFT JOIN PROFESSOR p ON r.id_professor = p.id_professor
                    LEFT JOIN FUNCIONARIO f ON r.id_funcionario = f.id_funcionario
                    LEFT JOIN VISITANTE vi ON r.id_visitante = vi.id_visitante
                    WHERE r.id_reserva = %s
                """
                cursor.execute(query, (id_registro,))
                registro = cursor.fetchone()
                if not registro:
                    messagebox.showerror("Erro", f"Reserva com ID {id_registro} não encontrada!")
                    return
                self.show_formulario_edicao_reserva(registro)
            elif tipo_dado == 'OCUPACAO':
                query = "SELECT * FROM OCUPACAO WHERE id_ocupacao = %s"
                cursor.execute(query, (id_registro,))
                registro = cursor.fetchone()
                if not registro:
                    messagebox.showerror("Erro", f"Ocupação com ID {id_registro} não encontrada!")
                    return
                self.show_formulario_edicao_ocupacao(registro)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar dados: {str(e)}")
        finally:
            cursor.close()

    def show_formulario_edicao_usuario(self, tipo_dado, registro):
        self.clear_window()
        self.current_frame = tk.Frame(self.root, bg='#f0f2f5')
        self.current_frame.pack(expand=True, fill='both', padx=50, pady=50)
        tk.Label(self.current_frame, text=f"Editar {tipo_dado.capitalize()}", font=('Arial', 18, 'bold'), bg='#f0f2f5', fg='#333').pack(pady=20)
        form_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        form_frame.pack(expand=True)
        tk.Label(form_frame, text="Nome completo:", bg='#f0f2f5', font=('Arial', 12)).grid(row=0, column=0, sticky='w', pady=5)
        self.editar_nome = tk.Entry(form_frame, font=('Arial', 12))
        self.editar_nome.insert(0, registro['nome'])
        self.editar_nome.grid(row=0, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="Telefone:", bg='#f0f2f5', font=('Arial', 12)).grid(row=1, column=0, sticky='w', pady=5)
        self.editar_telefone = tk.Entry(form_frame, font=('Arial', 12))
        self.editar_telefone.insert(0, registro.get('telefone', ''))
        self.editar_telefone.grid(row=1, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="Email:", bg='#f0f2f5', font=('Arial', 12)).grid(row=2, column=0, sticky='w', pady=5)
        self.editar_email = tk.Entry(form_frame, font=('Arial', 12))
        self.editar_email.insert(0, registro.get('email', ''))
        self.editar_email.grid(row=2, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="Documento (CPF/RG):", bg='#f0f2f5', font=('Arial', 12)).grid(row=3, column=0, sticky='w', pady=5)
        self.editar_documento = tk.Entry(form_frame, font=('Arial', 12))
        self.editar_documento.insert(0, registro['documento'])
        self.editar_documento.grid(row=3, column=1, pady=5, sticky='ew')
        if tipo_dado == 'ALUNO':
            tk.Label(form_frame, text="Matrícula:", bg='#f0f2f5', font=('Arial', 12)).grid(row=4, column=0, sticky='w', pady=5)
            self.editar_matricula = tk.Entry(form_frame, font=('Arial', 12))
            self.editar_matricula.insert(0, registro.get('matricula', ''))
            self.editar_matricula.grid(row=4, column=1, pady=5, sticky='ew')
        button_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Salvar", command=lambda: self.salvar_edicao_usuario(tipo_dado, registro[f'id_{tipo_dado.lower()}']), bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Voltar", command=self.show_editar_dados, bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(side=tk.LEFT, padx=10)

    def salvar_edicao_usuario(self, tipo_dado, id_registro):
        nome = self.editar_nome.get().strip()
        telefone = self.editar_telefone.get().strip()
        email = self.editar_email.get().strip()
        documento = self.editar_documento.get().strip()
        matricula = self.editar_matricula.get().strip() if tipo_dado == 'ALUNO' else None
        if not all([nome, documento]):
            messagebox.showerror("Erro", "Nome e documento são obrigatórios!")
            return
        if tipo_dado == 'ALUNO' and not matricula:
            messagebox.showerror("Erro", "Matrícula é obrigatória para alunos!")
            return
        try:
            cursor = self.estacionamento.connection.cursor()
            if tipo_dado == 'ALUNO':
                query = "UPDATE ALUNO SET nome = %s, telefone = %s, email = %s, documento = %s, matricula = %s WHERE id_aluno = %s"
                cursor.execute(query, (nome, telefone, email, documento, matricula, id_registro))
            else:
                query = f"UPDATE {tipo_dado} SET nome = %s, telefone = %s, email = %s, documento = %s WHERE id_{tipo_dado.lower()} = %s"
                cursor.execute(query, (nome, telefone, email, documento, id_registro))
            self.estacionamento.connection.commit()
            messagebox.showinfo("Sucesso", f"{tipo_dado.capitalize()} atualizado com sucesso!")
            self.create_dashboard()
        except Exception as e:
            self.estacionamento.connection.rollback()
            messagebox.showerror("Erro", f"Falha ao atualizar usuário: {str(e)}")
        finally:
            cursor.close()

    def show_formulario_edicao_veiculo(self, registro):
        self.clear_window()
        self.current_frame = tk.Frame(self.root, bg='#f0f2f5')
        self.current_frame.pack(expand=True, fill='both', padx=50, pady=50)
        tk.Label(self.current_frame, text="Editar Veículo", font=('Arial', 18, 'bold'), bg='#f0f2f5', fg='#333').pack(pady=20)
        form_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        form_frame.pack(expand=True)
        tk.Label(form_frame, text="Placa:", bg='#f0f2f5', font=('Arial', 12)).grid(row=0, column=0, sticky='w', pady=5)
        self.editar_placa = tk.Entry(form_frame, font=('Arial', 12))
        self.editar_placa.insert(0, registro['placa'])
        self.editar_placa.grid(row=0, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="Modelo:", bg='#f0f2f5', font=('Arial', 12)).grid(row=1, column=0, sticky='w', pady=5)
        self.editar_modelo = tk.Entry(form_frame, font=('Arial', 12))
        self.editar_modelo.insert(0, registro['modelo'])
        self.editar_modelo.grid(row=1, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="Tipo do proprietário:", bg='#f0f2f5', font=('Arial', 12)).grid(row=2, column=0, sticky='w', pady=5)
        self.editar_tipo_usuario = ttk.Combobox(form_frame, values=["ALUNO", "PROFESSOR", "FUNCIONARIO", "VISITANTE"], style='TCombobox')
        self.editar_tipo_usuario.set(registro['tipo_usuario'])
        self.editar_tipo_usuario.grid(row=2, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="ID do proprietário:", bg='#f0f2f5', font=('Arial', 12)).grid(row=3, column=0, sticky='w', pady=5)
        self.editar_id_usuario = tk.Entry(form_frame, font=('Arial', 12))
        self.editar_id_usuario.insert(0, registro['id_usuario'])
        self.editar_id_usuario.grid(row=3, column=1, pady=5, sticky='ew')
        button_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Salvar", command=lambda: self.salvar_veiculo(registro['id_veiculo']), bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Voltar", command=self.show_editar_dados, bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(side=tk.LEFT, padx=10)

    def salvar_veiculo(self, id_veiculo):
        placa = self.editar_placa.get().strip()
        modelo = self.editar_modelo.get().strip()
        tipo_usuario = self.editar_tipo_usuario.get().strip().lower()
        id_usuario = self.editar_id_usuario.get().strip()
        if not all([placa, modelo, tipo_usuario, id_usuario]):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return
        if tipo_usuario not in ['aluno', 'professor', 'funcionario', 'visitante']:
            messagebox.showerror("Erro", "Tipo de usuário inválido!")
            return
        try:
            id_usuario = int(id_usuario)
            cursor = self.estacionamento.connection.cursor()
            query = f"""
                UPDATE VEICULO
                SET placa = %s, modelo = %s,
                    id_aluno = NULL, id_professor = NULL, id_funcionario = NULL, id_visitante = NULL,
                    id_{tipo_usuario.lower()} = %s
                WHERE id_veiculo = %s
            """
            cursor.execute(query, (placa, modelo, id_usuario, id_veiculo))
            self.estacionamento.connection.commit()
            messagebox.showinfo("Sucesso", "Veículo atualizado com sucesso!")
            self.create_dashboard()
        except Exception as e:
            self.estacionamento.connection.rollback()
            messagebox.showerror("Erro", f"Falha ao atualizar veículo: {str(e)}")
        finally:
            cursor.close()

    def show_formulario_edicao_vaga(self, registro):
        self.clear_window()
        self.current_frame = tk.Frame(self.root, bg='#f0f2f5')
        self.current_frame.pack(expand=True, fill='both', padx=50, pady=50)
        tk.Label(self.current_frame, text="Editar Vaga", font=('Arial', 18, 'bold'), bg='#f0f2f5', fg='#333').pack(pady=20)
        form_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        form_frame.pack(expand=True)
        tk.Label(form_frame, text="Localização:", bg='#f0f2f5', font=('Arial', 12)).grid(row=0, column=0, sticky='w', pady=5)
        self.editar_localizacao_vaga = tk.Entry(form_frame, font=('Arial', 12))
        self.editar_localizacao_vaga.insert(0, registro['localizacao'])
        self.editar_localizacao_vaga.grid(row=0, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="Tipo:", bg='#f0f2f5', font=('Arial', 12)).grid(row=1, column=0, sticky='w', pady=5)
        self.editar_tipo_vaga = ttk.Combobox(form_frame, values=['COMUM', 'IDOSO', 'DEFICIENTE'], style='TCombobox')
        self.editar_tipo_vaga.set(registro['tipo'].upper().capitalize())
        self.editar_tipo_vaga.grid(row=1, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="Estado:", bg='#f0f2f5', font=('Arial', 12)).grid(row=2, column=0, sticky='w', pady=5)
        self.editar_estado_vaga = ttk.Combobox(form_frame, values=['disponivel', 'ocupada', 'reservada'], style='TCombobox')
        self.editar_estado_vaga.set(registro['estado'])
        self.editar_estado_vaga.grid(row=2, column=1, pady=5, sticky='ew')
        button_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Salvar", command=lambda: self.salvar_vaga(registro['id_vaga']), bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Voltar", command=self.show_editar_dados, bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(side=tk.LEFT, padx=10)

    def salvar_vaga(self, id_vaga):
        localizacao = self.editar_localizacao_vaga.get().strip()
        tipo = self.editar_tipo_vaga.get().strip().lower()
        estado = self.editar_estado_vaga.get().strip().lower()
        if not all([localizacao, tipo, estado]):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return
        if tipo not in ['comum', 'idoso', 'deficiente']:
            messagebox.showerror("Erro", "Tipo de vaga inválido!")
            return
        if estado not in ['disponivel', 'ocupada', 'reservada']:
            messagebox.showerror("Erro", "Estado inválido!")
            return
        try:
            cursor = self.estacionamento.connection.cursor()
            query = "UPDATE VAGA SET localizacao = %s, tipo = %s, estado = %s WHERE id_vaga = %s"
            cursor.execute(query, (localizacao, tipo, estado, id_vaga))
            self.estacionamento.connection.commit()
            messagebox.showinfo("Sucesso", "Vaga atualizada com sucesso!")
            self.create_dashboard()
        except Exception as e:
            self.estacionamento.connection.rollback()
            messagebox.showerror("Erro", f"Falha ao atualizar vaga: {str(e)}")
        finally:
            cursor.close()

    def show_formulario_edicao_reserva(self, registro):
        self.clear_window()
        self.current_frame = tk.Frame(self.root, bg='#f0f2f5')
        self.current_frame.pack(expand=True, fill='both', padx=50, pady=50)
        tk.Label(self.current_frame, text="Editar Reserva", font=('Arial', 18, 'bold'), bg='#f0f2f5', fg='#333').pack(pady=20)
        form_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        form_frame.pack(expand=True)
        tk.Label(form_frame, text="Tipo do usuário:", bg='#f0f2f5', font=('Arial', 12)).grid(row=0, column=0, sticky='w', pady=5)
        self.editar_reserva_tipo_usuario = ttk.Combobox(form_frame, values=['ALUNO', 'PROFESSOR', 'FUNCIONARIO', 'VISITANTE'], style='TCombobox')
        self.editar_reserva_tipo_usuario.set(registro['tipo_usuario'])
        self.editar_reserva_tipo_usuario.grid(row=0, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="ID do usuário:", bg='#f0f2f5', font=('Arial', 12)).grid(row=1, column=0, sticky='w', pady=5)
        self.editar_reserva_id_usuario = tk.Entry(form_frame, font=('Arial', 12))
        self.editar_reserva_id_usuario.insert(0, registro['id_usuario'])
        self.editar_reserva_id_usuario.grid(row=1, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="ID da vaga:", bg='#f0f2f5', font=('Arial', 12)).grid(row=2, column=0, sticky='w', pady=5)
        self.editar_reserva_id_vaga = tk.Entry(form_frame, font=('Arial', 12))
        self.editar_reserva_id_vaga.insert(0, registro['id_vaga'])
        self.editar_reserva_id_vaga.grid(row=2, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="Data/hora início (AAAA-MM-DD HH:MM):", bg='#f0f2f5', font=('Arial', 12)).grid(row=3, column=0, sticky='w', pady=5)
        self.editar_reserva_data_inicio = tk.Entry(form_frame, font=('Arial', 12))
        self.editar_reserva_data_inicio.insert(0, registro['data_inicio'].strftime("%Y-%m-%d %H:%M"))
        self.editar_reserva_data_inicio.grid(row=3, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="Data/hora fim (AAAA-MM-DD HH:MM):", bg='#f0f2f5', font=('Arial', 12)).grid(row=4, column=0, sticky='w', pady=5)
        self.editar_reserva_data_fim = tk.Entry(form_frame, font=('Arial', 12))
        self.editar_reserva_data_fim.insert(0, registro['data_fim'].strftime("%Y-%m-%d %H:%M"))
        self.editar_reserva_data_fim.grid(row=4, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="Status:", bg='#f0f2f5', font=('Arial', 12)).grid(row=5, column=0, sticky='w', pady=5)
        self.editar_reserva_status = ttk.Combobox(form_frame, values=['ativa', 'cancelada', 'concluida'], style='TCombobox')
        self.editar_reserva_status.set(registro['status'])
        self.editar_reserva_status.grid(row=5, column=1, pady=5, sticky='ew')
        button_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Salvar", command=lambda: self.salvar_reserva(registro['id_reserva']), bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Voltar", command=self.show_editar_dados, bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(side=tk.LEFT, padx=10)

    def salvar_reserva(self, id_reserva):
        tipo_usuario = self.editar_reserva_tipo_usuario.get().strip().lower()
        id_usuario = self.editar_reserva_id_usuario.get().strip()
        id_vaga = self.editar_reserva_id_vaga.get().strip()
        data_inicio = self.editar_reserva_data_inicio.get().strip()
        data_fim = self.editar_reserva_data_fim.get().strip()
        status = self.editar_reserva_status.get().strip().lower()
        if not all([tipo_usuario, id_usuario, id_vaga, data_inicio, data_fim, status]):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return
        if tipo_usuario not in ['aluno', 'professor', 'funcionario', 'visitante']:
            messagebox.showerror("Erro", "Tipo de usuário inválido!")
            return
        if status not in ['ativa', 'cancelada', 'concluida']:
            messagebox.showerror("Erro", "Status inválido!")
            return
        try:
            id_usuario = int(id_usuario)
            id_vaga = int(id_vaga)
            datetime.strptime(data_inicio, "%Y-%m-%d %H:%M")
            datetime.strptime(data_fim, "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Erro", "IDs devem ser números e datas no formato AAAA-MM-DD HH:MM!")
            return
        cursor = self.estacionamento.connection.cursor()
        try:
            query = f"SELECT id_{tipo_usuario} FROM {tipo_usuario.upper()} WHERE id_{tipo_usuario} = %s"
            cursor.execute(query, (id_usuario,))
            if not cursor.fetchone():
                raise Exception(f"Usuário {tipo_usuario} com ID {id_usuario} não encontrado!")
            query = "SELECT id_vaga FROM VAGA WHERE id_vaga = %s"
            cursor.execute(query, (id_vaga,))
            if not cursor.fetchone():
                raise Exception(f"Vaga com ID {id_vaga} não encontrada!")
            query = f"""
                UPDATE RESERVA
                SET id_aluno = NULL, id_professor = NULL, id_funcionario = NULL, id_visitante = NULL,
                    id_{tipo_usuario} = %s, id_vaga = %s, data_inicio = %s, data_fim = %s, status = %s
                WHERE id_reserva = %s
            """
            cursor.execute(query, (id_usuario, id_vaga, data_inicio, data_fim, status, id_reserva))
            self.estacionamento.connection.commit()
            messagebox.showinfo("Sucesso", "Reserva atualizada com sucesso!")
            self.create_dashboard()
        except Exception as e:
            self.estacionamento.connection.rollback()
            messagebox.showerror("Erro", f"Falha ao atualizar reserva: {str(e)}")
        finally:
            cursor.close()

    def show_formulario_edicao_ocupacao(self, registro):
        self.clear_window()
        self.current_frame = tk.Frame(self.root, bg='#f0f2f5')
        self.current_frame.pack(expand=True, fill='both', padx=50, pady=50)
        tk.Label(self.current_frame, text="Editar Ocupação", font=('Arial', 18, 'bold'), bg='#f0f2f5', fg='#333').pack(pady=20)
        form_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        form_frame.pack(expand=True)
        tk.Label(form_frame, text="ID do veículo:", bg='#f0f2f5', font=('Arial', 12)).grid(row=0, column=0, sticky='w', pady=5)
        self.editar_ocupacao_id_veiculo = tk.Entry(form_frame, font=('Arial', 12))
        self.editar_ocupacao_id_veiculo.insert(0, registro['id_veiculo'])
        self.editar_ocupacao_id_veiculo.grid(row=0, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="ID da vaga:", bg='#f0f2f5', font=('Arial', 12)).grid(row=1, column=0, sticky='w', pady=5)
        self.editar_ocupacao_id_vaga = tk.Entry(form_frame, font=('Arial', 12))
        self.editar_ocupacao_id_vaga.insert(0, registro['id_vaga'])
        self.editar_ocupacao_id_vaga.grid(row=1, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="Data de entrada (AAAA-MM-DD HH:MM):", bg='#f0f2f5', font=('Arial', 12)).grid(row=2, column=0, sticky='w', pady=5)
        self.editar_ocupacao_data_entrada = tk.Entry(form_frame, font=('Arial', 12))
        self.editar_ocupacao_data_entrada.insert(0, registro['data_entrada'].strftime("%Y-%m-%d %H:%M"))
        self.editar_ocupacao_data_entrada.grid(row=2, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="Data de saída (AAAA-MM-DD HH:MM ou vazio):", bg='#f0f2f5', font=('Arial', 12)).grid(row=3, column=0, sticky='w', pady=5)
        self.editar_ocupacao_data_saida = tk.Entry(form_frame, font=('Arial', 12))
        if registro['data_saida']:
            self.editar_ocupacao_data_saida.insert(0, registro['data_saida'].strftime("%Y-%m-%d %H:%M"))
        self.editar_ocupacao_data_saida.grid(row=3, column=1, pady=5, sticky='ew')
        button_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Salvar", command=lambda: self.salvar_ocupacao(registro['id_ocupacao']), bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Voltar", command=self.show_editar_dados, bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(side=tk.LEFT, padx=10)

    def salvar_ocupacao(self, id_ocupacao):
        id_veiculo = self.editar_ocupacao_id_veiculo.get().strip()
        id_vaga = self.editar_ocupacao_id_vaga.get().strip()
        data_entrada = self.editar_ocupacao_data_entrada.get().strip()
        data_saida = self.editar_ocupacao_data_saida.get().strip()
        if not all([id_veiculo, id_vaga, data_entrada]):
            messagebox.showerror("Erro", "ID do veículo, ID da vaga e data de entrada são obrigatórios!")
            return
        try:
            id_veiculo = int(id_veiculo)
            id_vaga = int(id_vaga)
            datetime.strptime(data_entrada, "%Y-%m-%d %H:%M")
            if data_saida:
                datetime.strptime(data_saida, "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Erro", "IDs devem ser números e datas no formato AAAA-MM-DD HH:MM!")
            return
        cursor = self.estacionamento.connection.cursor()
        try:
            query = "SELECT id_veiculo FROM VEICULO WHERE id_veiculo = %s"
            cursor.execute(query, (id_veiculo,))
            if not cursor.fetchone():
                raise Exception(f"Veículo com ID {id_veiculo} não encontrado!")
            query = "SELECT id_vaga FROM VAGA WHERE id_vaga = %s"
            cursor.execute(query, (id_vaga,))
            if not cursor.fetchone():
                raise Exception(f"Vaga com ID {id_vaga} não encontrada!")
            query = """
                UPDATE OCUPACAO
                SET id_veiculo = %s, id_vaga = %s, data_entrada = %s, data_saida = %s
                WHERE id_ocupacao = %s
            """
            cursor.execute(query, (id_veiculo, id_vaga, data_entrada, data_saida if data_saida else None, id_ocupacao))
            self.estacionamento.connection.commit()
            messagebox.showinfo("Sucesso", "Ocupação atualizada com sucesso!")
            self.create_dashboard()
        except Exception as e:
            self.estacionamento.connection.rollback()
            messagebox.showerror("Erro", f"Falha ao atualizar ocupação: {str(e)}")
        finally:
            cursor.close()

    def show_deletar_dados(self):
        self.clear_window()
        self.current_frame = tk.Frame(self.root, bg='#f0f2f5')
        self.current_frame.pack(expand=True, fill='both', padx=50, pady=50)
        tk.Label(self.current_frame, text="Deletar Dados", font=('Arial', 18, 'bold'), bg='#f0f2f5', fg='#333').pack(pady=20)
        form_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        form_frame.pack(expand=True)
        tk.Label(form_frame, text="Tipo de dado:", bg='#f0f2f5', font=('Arial', 12)).grid(row=0, column=0, sticky='w', pady=5)
        self.deletar_tipo_dado = ttk.Combobox(form_frame, values=["ALUNO", "PROFESSOR", "FUNCIONARIO", "VISITANTE", "VEICULO", "VAGA", "RESERVA", "OCUPACAO"], style='TCombobox')
        self.deletar_tipo_dado.grid(row=0, column=1, pady=5, sticky='ew')
        tk.Label(form_frame, text="ID do registro:", bg='#f0f2f5', font=('Arial', 12)).grid(row=1, column=0, sticky='w', pady=5)
        self.deletar_id_registro = tk.Entry(form_frame, font=('Arial', 12))
        self.deletar_id_registro.grid(row=1, column=1, pady=5, sticky='ew')
        button_frame = tk.Frame(self.current_frame, bg='#f0f2f5')
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Deletar", command=self.deletar_registro, bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Voltar", command=self.create_dashboard, bg='#d32f2f', fg='white', font=('Arial', 12), relief='flat', padx=20, pady=10).pack(side=tk.LEFT, padx=10)

    def deletar_registro(self):
        tipo_dado = self.deletar_tipo_dado.get().strip().upper()
        id_registro = self.deletar_id_registro.get().strip()
        if not tipo_dado or not id_registro:
            messagebox.showerror("Erro", "Tipo de dado e ID são obrigatórios!")
            return
        try:
            id_registro = int(id_registro)
        except ValueError:
            messagebox.showerror("Erro", "ID deve ser um número!")
            return
        cursor = self.estacionamento.connection.cursor()
        try:
            if tipo_dado in ['ALUNO', 'PROFESSOR', 'FUNCIONARIO', 'VISITANTE']:
                query = f"DELETE FROM {tipo_dado} WHERE id_{tipo_dado.lower()} = %s"
            elif tipo_dado == 'VEICULO':
                query = "DELETE FROM VEICULO WHERE id_veiculo = %s"
            elif tipo_dado == 'VAGA':
                query = "DELETE FROM VAGA WHERE id_vaga = %s"
            elif tipo_dado == 'RESERVA':
                query = "DELETE FROM RESERVA WHERE id_reserva = %s"
            elif tipo_dado == 'OCUPACAO':
                query = "DELETE FROM OCUPACAO WHERE id_ocupacao = %s"
            else:
                messagebox.showerror("Erro", "Tipo de dado inválido!")
                return
            cursor.execute(query, (id_registro,))
            if cursor.rowcount == 0:
                messagebox.showerror("Erro", f"Registro {tipo_dado} com ID {id_registro} não encontrado!")
            else:
                self.estacionamento.connection.commit()
                messagebox.showinfo("Sucesso", f"Registro {tipo_dado} deletado com sucesso!")
                self.create_dashboard()
        except Exception as e:
            self.estacionamento.connection.rollback()
            messagebox.showerror("Erro", f"Falha ao deletar registro: {str(e)}")
        finally:
            cursor.close()

    def clear_window(self):
        if self.current_frame:
            self.current_frame.destroy()
        for widget in self.root.winfo_children():
            if widget != self.bg_label:
                widget.destroy()
        self.current_frame = None

    def exit_system(self):
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = EstacionamentoGUI(root)
    root.mainloop()
