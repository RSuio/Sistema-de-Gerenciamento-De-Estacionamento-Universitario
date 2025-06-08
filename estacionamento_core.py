estacionamento_core.py
import mysql.connector
from mysql.connector import Error
import os
import datetime
from dotenv import load_dotenv

class Database:
    def __init__(self):
        load_dotenv()

        host = os.getenv('DB_HOST')
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        database = os.getenv('DB_NAME')

        if not password:
            raise ValueError("Senha do banco não encontrada! Verifique o arquivo .env")

        try:
            temp_connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password
            )
            temp_cursor = temp_connection.cursor()
            
            temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}`")
            temp_connection.commit()
            print(f"Database '{database}' criado ou verificado com sucesso!")
            
            temp_cursor.close()
            temp_connection.close()
            
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            self.cursor = self.connection.cursor()
            print("Conexão estabelecida com sucesso!")
            
            self._create_tables()
            
        except Error as error:
            print(f"Erro ao conectar ao banco de dados: {error}")
            self.connection = None
            self.cursor = None

    def _create_tables(self):
        
        tables = [
            """
            CREATE TABLE IF NOT EXISTS ALUNO (
                id_aluno INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                telefone VARCHAR(20),
                email VARCHAR(255),
                documento VARCHAR(20) NOT NULL,
                matricula VARCHAR(20) NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS PROFESSOR (
                id_professor INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                telefone VARCHAR(20),
                email VARCHAR(255),
                documento VARCHAR(20) NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS FUNCIONARIO (
                id_funcionario INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                telefone VARCHAR(20),
                email VARCHAR(255),
                documento VARCHAR(20) NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS VISITANTE (
                id_visitante INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                telefone VARCHAR(20),
                email VARCHAR(255),
                documento VARCHAR(20) NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS VEICULO (
                id_veiculo INT AUTO_INCREMENT PRIMARY KEY,
                placa VARCHAR(10) NOT NULL,
                modelo VARCHAR(50),
                id_aluno INT,
                id_professor INT,
                id_funcionario INT,
                id_visitante INT,
                FOREIGN KEY (id_aluno) REFERENCES ALUNO(id_aluno) ON DELETE CASCADE,
                FOREIGN KEY (id_professor) REFERENCES PROFESSOR(id_professor) ON DELETE CASCADE,
                FOREIGN KEY (id_funcionario) REFERENCES FUNCIONARIO(id_funcionario) ON DELETE CASCADE,
                FOREIGN KEY (id_visitante) REFERENCES VISITANTE(id_visitante) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS VAGA (
                id_vaga INT AUTO_INCREMENT PRIMARY KEY,
                localizacao VARCHAR(10) NOT NULL,
                estado ENUM('disponivel', 'reservada', 'ocupada') DEFAULT 'disponivel',
                tipo ENUM('comum', 'idoso', 'deficiente') DEFAULT 'comum'
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS RESERVA (
                id_reserva INT AUTO_INCREMENT PRIMARY KEY,
                id_aluno INT,
                id_professor INT,
                id_funcionario INT,
                id_visitante INT,
                id_vaga INT NOT NULL,
                data_inicio DATETIME NOT NULL,
                data_fim DATETIME NOT NULL,
                status ENUM('ativa', 'concluida', 'cancelada') DEFAULT 'ativa',
                FOREIGN KEY (id_aluno) REFERENCES ALUNO(id_aluno) ON DELETE CASCADE,
                FOREIGN KEY (id_professor) REFERENCES PROFESSOR(id_professor) ON DELETE CASCADE,
                FOREIGN KEY (id_funcionario) REFERENCES FUNCIONARIO(id_funcionario) ON DELETE CASCADE,
                FOREIGN KEY (id_visitante) REFERENCES VISITANTE(id_visitante) ON DELETE CASCADE,
                FOREIGN KEY (id_vaga) REFERENCES VAGA(id_vaga) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS OCUPACAO (
                id_ocupacao INT AUTO_INCREMENT PRIMARY KEY,
                id_veiculo INT NOT NULL,
                id_vaga INT NOT NULL,
                data_entrada DATETIME NOT NULL,
                data_saida DATETIME,
                FOREIGN KEY (id_veiculo) REFERENCES VEICULO(id_veiculo) ON DELETE CASCADE,
                FOREIGN KEY (id_vaga) REFERENCES VAGA(id_vaga) ON DELETE CASCADE
            )
            """
        ]

        try:
            for table in tables:
                self.cursor.execute(table)
            self.connection.commit()
            print("Tabelas criadas ou verificadas com sucesso.")
        except Error as error:
            print(f"Erro ao criar tabelas: {error}")
            self.connection.rollback()

    def get_connection(self):
        return self.connection

    def close_connection(self):
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("Conexão fechada.")

class Usuario:
    def __init__(self, estacionamento):
        self.connection = estacionamento.connection
        self.cursor = self.connection.cursor()

    def cadastrar_usuario(self, tipo, nome, telefone, email, documento, matricula=None):
        try:
            if tipo not in ['aluno', 'professor', 'funcionario', 'visitante']:
                raise ValueError("Tipo inválido!")

            table = tipo.upper()
            query = f"""
                INSERT INTO {table} (nome, telefone, email, documento{f', matricula' if tipo == 'aluno' else ''})
                VALUES (%s, %s, %s, %s{f', %s' if tipo == 'aluno' else ''})
            """
            values = (nome, telefone, email, documento, matricula) if tipo == 'aluno' else (nome, telefone, email, documento)
            self.cursor.execute(query, values)
            self.connection.commit()
            print(f"Usuário ({tipo.capitalize()}) cadastrado com sucesso. ID: {self.cursor.lastrowid}")
            return self.cursor.lastrowid
        except Error as error:
            print(f"Erro ao cadastrar usuário ({tipo}): {error}")
            return None

class Veiculo:
    def __init__(self, estacionamento):
        self.connection = estacionamento.connection
        self.cursor = self.connection.cursor()

    def cadastrar_veiculo(self, placa, modelo, tipo_usuario, id_usuario):
        try:
            if tipo_usuario not in ['aluno', 'professor', 'funcionario', 'visitante']:
                raise ValueError("Tipo inválido!")

            self.cursor.execute(f"SELECT id_{tipo_usuario} FROM {tipo_usuario.upper()} WHERE id_{tipo_usuario} = %s", (id_usuario,))
            if not self.cursor.fetchone():
                print(f"Usuário ({tipo_usuario.capitalize()}):({id_usuario}) não encontrado.!")
                return None

            query = f"""
                INSERT INTO VEICULO (placa, modelo, id_{tipo_usuario})
                VALUES (%s, %s, %s)
            """
            self.cursor.execute(query, (placa, modelo, id_usuario))
            self.connection.commit()
            print(f"Veículo cadastrado com sucesso. ID: {self.cursor.lastrowid}")
            return self.cursor.lastrowid
        except Error as error:
            print(f"Erro ao cadastrar veículo: {error}")
            return None

class Vaga:
    def __init__(self, estacionamento):
        self.connection = estacionamento.connection
        self.cursor = self.connection.cursor()

    def cadastrar_vaga(self, localizacao, estado='disponivel', tipo='comum'):
        try:
            query = """
                INSERT INTO VAGA (localizacao, estado, tipo)
                VALUES (%s, %s, %s)
            """
            self.cursor.execute(query, (localizacao, estado, tipo))
            self.connection.commit()
            print(f"Vaga cadastrada com sucesso. ID: {self.cursor.lastrowid}")
            return self.cursor.lastrowid
        except Error as error:
            print(f"Erro ao cadastrar vaga: {error}")
            return None

    def listar_disponiveis(self):
        query = """ SELECT * FROM VAGA WHERE estado = 'disponivel'"""
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(query)
            return cursor.fetchall()
        except Error as error:
            print(f'Erro ao listar vagas: {error}')
            return None

class Reserva:
    def __init__(self, estacionamento):
        self.estacionamento = estacionamento
        self.connection = estacionamento.connection
        self.cursor = self.connection.cursor() if self.connection else None

    def reservar_vaga(self, id_usuario, id_vaga, data_inicio, data_fim, tipo_usuario):
        if not self.connection or not self.cursor:
            print("Erro: Conexão com o banco de dados não está disponível.")
            return None

        tipo_usuario = tipo_usuario.lower()
        if tipo_usuario not in ['aluno', 'professor', 'funcionario', 'visitante']:
            print("Tipo de usuário inválido!")
            return None

        try:
            datetime_obj_inicio = datetime.datetime.strptime(data_inicio, '%Y-%m-%d %H:%M')
            datetime_obj_fim = datetime.datetime.strptime(data_fim, '%Y-%m-%d %H:%M')
            if datetime_obj_fim <= datetime_obj_inicio:
                print("Erro: A data de fim deve ser posterior à data de início.")
                return None
            data_inicio_mysql = datetime_obj_inicio.strftime('%Y-%m-%d %H:%M:00')
            data_fim_mysql = datetime_obj_fim.strftime('%Y-%m-%d %H:%M:00')
        except ValueError:
            print("Formato de data inválido! Use AAAA-MM-DD HH:MM")
            return None

        cursor = self.connection.cursor(dictionary=True)
        query_vaga = "SELECT estado FROM VAGA WHERE id_vaga = %s"
        cursor.execute(query_vaga, (id_vaga,))
        vaga = cursor.fetchone()

        if vaga and vaga['estado'] == 'disponivel':
            cursor.execute(f"SELECT id_{tipo_usuario} FROM {tipo_usuario.upper()} WHERE id_{tipo_usuario} = %s", (id_usuario,))
            if not cursor.fetchone():
                print(f"Usuário do tipo {tipo_usuario} com ID {id_usuario} não encontrado.")
                cursor.close()
                return None

            query = f"""INSERT INTO RESERVA
                        (id_{tipo_usuario}, id_vaga, data_inicio, data_fim)
                        VALUES (%s, %s, %s, %s)"""
            update_vaga = "UPDATE VAGA SET estado = 'reservada' WHERE id_vaga = %s"

            try:
                if self.connection.in_transaction:
                    self.connection.rollback()
                    print("Aviso: Transação anterior foi encerrada.")
                self.connection.start_transaction()
                cursor.execute(query, (id_usuario, id_vaga, data_inicio_mysql, data_fim_mysql))
                cursor.execute(update_vaga, (id_vaga,))
                self.connection.commit()
                print("Reserva criada com sucesso!")
                return cursor.lastrowid
            except Error as error:
                self.connection.rollback()
                print(f'Erro ao criar reserva: {error}')
                return None
            finally:
                cursor.close()
        else:
            print("Vaga não está disponível para reserva")
            cursor.close()
            return None

class Ocupacao:
    def __init__(self, estacionamento):
        self.estacionamento = estacionamento

    def registrar_entrada(self, id_veiculo, id_vaga):
        if not self.estacionamento.connection or not self.estacionamento.connection.cursor:
            print("Erro: Conexão com o banco de dados não está disponível.")
            return None

        cursor = self.estacionamento.connection.cursor(dictionary=True)
        query_vaga = """SELECT estado FROM VAGA WHERE id_vaga = %s"""
        cursor.execute(query_vaga, (id_vaga,))
        vaga = cursor.fetchone()

        if vaga:
            if vaga['estado'] == 'disponivel' or vaga['estado'] == 'reservada':
                tipo_usuario = None
                for tipo in ['aluno', 'professor', 'funcionario', 'visitante']:
                    query_check = f"SELECT id_{tipo} FROM VEICULO WHERE id_veiculo = %s"
                    cursor.execute(query_check, (id_veiculo,))
                    if cursor.fetchone():
                        tipo_usuario = tipo
                        break

                if not tipo_usuario:
                    print("Veículo não está associado a nenhum usuário.")
                    cursor.close()
                    return None

                query_reserva = f"""SELECT id_reserva FROM RESERVA
                                   WHERE id_vaga = %s AND id_{tipo_usuario} =
                                   (SELECT id_{tipo_usuario} FROM VEICULO WHERE id_veiculo = %s)
                                   AND status = 'ativa'"""
                cursor.execute(query_reserva, (id_vaga, id_veiculo))
                reserva = cursor.fetchone()

                if vaga['estado'] == 'reservada' and not reserva:
                    print("Vaga está reservada para outro usuário")
                    cursor.close()
                    return None

                query = """INSERT INTO OCUPACAO
                           (id_veiculo, id_vaga, data_entrada)
                           VALUES (%s, %s, NOW())"""
                update_vaga = "UPDATE VAGA SET estado = 'ocupada' WHERE id_vaga = %s"
                update_reserva = """UPDATE RESERVA SET status = 'concluida'
                                   WHERE id_reserva = %s""" if reserva else None

                try:
                    if self.estacionamento.connection.in_transaction:
                        self.estacionamento.connection.rollback()
                        print("Aviso: Transação anterior foi encerrada.")
                    self.estacionamento.connection.start_transaction()
                    cursor.execute(query, (id_veiculo, id_vaga))
                    cursor.execute(update_vaga, (id_vaga,))
                    if update_reserva:
                        cursor.execute(update_reserva, (reserva['id_reserva'],))
                    self.estacionamento.connection.commit()
                    print("Entrada registrada com sucesso!")
                    return cursor.lastrowid
                except Error as error:
                    self.estacionamento.connection.rollback()
                    print(f'Erro ao registrar entrada: {error}')
                    return None
                finally:
                    cursor.close()
            else:
                print("Vaga não está disponível")
                cursor.close()
                return None
        else:
            print("Vaga não encontrada")
            cursor.close()
            return None

    def registrar_saida(self, id_ocupacao):
        query = """UPDATE OCUPACAO
                  SET data_saida = NOW()
                  WHERE id_ocupacao = %s AND data_saida IS NULL"""
        query_vaga = """UPDATE VAGA SET estado = 'disponivel'
                  WHERE id_vaga = (SELECT id_vaga FROM OCUPACAO WHERE id_ocupacao = %s)"""

        cursor = self.estacionamento.connection.cursor()
        try:
            self.estacionamento.connection.start_transaction()
            cursor.execute(query, (id_ocupacao,))
            cursor.execute(query_vaga, (id_ocupacao,))
            self.estacionamento.connection.commit()
            return cursor.rowcount > 0
        except Error as error:
            self.estacionamento.connection.rollback()
            print(f'Erro ao registrar saída: {error}')
            return False
