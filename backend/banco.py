"""Persistência em SQLite. Uma conta de jogador local para o MVP acadêmico."""
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from backend.catalogo import nome_bonito
from backend.economia import Orcamento, RegraDeNegocio

ROOT = Path(__file__).resolve().parents[1]
OURO_INICIAL_CENTAVOS = 100_000  # 1.000 moedas


def caminho_banco() -> Path:
    return Path(os.getenv('DATABASE_PATH', str(ROOT / 'dados' / 'mercador.db'))).resolve()


@contextmanager
def conexao():
    caminho = caminho_banco()
    caminho.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(caminho), timeout=10, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    conn.execute('PRAGMA busy_timeout = 10000')
    try:
        yield conn
    finally:
        conn.close()


def inicializar():
    with conexao() as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS jogador (
            id INTEGER PRIMARY KEY CHECK(id = 1),
            nome TEXT NOT NULL,
            ouro_centavos INTEGER NOT NULL CHECK(ouro_centavos >= 0)
        );
        CREATE TABLE IF NOT EXISTS inventario (
            jogador_id INTEGER NOT NULL REFERENCES jogador(id),
            item TEXT NOT NULL,
            quantidade INTEGER NOT NULL CHECK(quantidade > 0),
            PRIMARY KEY (jogador_id, item)
        );
        CREATE TABLE IF NOT EXISTS compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jogador_id INTEGER NOT NULL REFERENCES jogador(id),
            item TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            local TEXT NOT NULL,
            subtotal_centavos INTEGER NOT NULL,
            taxa_centavos INTEGER NOT NULL,
            total_centavos INTEGER NOT NULL,
            criado_em TEXT NOT NULL DEFAULT (datetime('now'))
        );
        INSERT OR IGNORE INTO jogador(id, nome, ouro_centavos)
        VALUES (1, 'Aventureiro', 100000);
        ''')


def estado() -> dict:
    with conexao() as db:
        row = db.execute('SELECT ouro_centavos, nome FROM jogador WHERE id = 1').fetchone()
        itens = db.execute('SELECT item, quantidade FROM inventario WHERE jogador_id = 1 ORDER BY item').fetchall()
        compras = db.execute('SELECT COUNT(*) FROM compras WHERE jogador_id = 1').fetchone()[0]
        return {
            'nome': row['nome'], 'ouro_centavos': row['ouro_centavos'],
            'inventario': [dict(item=r['item'], nome=nome_bonito(r['item']), quantidade=r['quantidade']) for r in itens],
            'compras_realizadas': compras,
        }


def comprar(orcamento: Orcamento) -> dict:
    # Transação atômica: checar saldo, debitar, inserir inventário e histórico juntos.
    with conexao() as db:
        db.execute('BEGIN IMMEDIATE')
        try:
            saldo = db.execute('SELECT ouro_centavos FROM jogador WHERE id = 1').fetchone()[0]
            if saldo < orcamento.total_centavos:
                raise RegraDeNegocio('Ouro insuficiente para concluir esta compra.')
            db.execute('UPDATE jogador SET ouro_centavos = ouro_centavos - ? WHERE id = 1',
                       (orcamento.total_centavos,))
            db.execute('''INSERT INTO inventario(jogador_id,item,quantidade) VALUES (1,?,?)
                       ON CONFLICT(jogador_id,item) DO UPDATE SET quantidade = quantidade + excluded.quantidade''',
                       (orcamento.item, orcamento.quantidade))
            cursor = db.execute('''INSERT INTO compras(jogador_id,item,quantidade,local,subtotal_centavos,taxa_centavos,total_centavos)
                               VALUES(1,?,?,?,?,?,?)''',
                               (orcamento.item, orcamento.quantidade, orcamento.local,
                                orcamento.subtotal_centavos, orcamento.taxa_centavos, orcamento.total_centavos))
            db.commit()
            return {'compra_id': cursor.lastrowid, 'orcamento': orcamento.como_dict(), 'estado': estado()}
        except Exception:
            db.rollback()
            raise


def reiniciar():
    with conexao() as db:
        db.execute('BEGIN IMMEDIATE')
        try:
            db.execute('DELETE FROM compras')
            db.execute('DELETE FROM inventario')
            db.execute('UPDATE jogador SET ouro_centavos = ? WHERE id = 1', (OURO_INICIAL_CENTAVOS,))
            db.commit()
        except Exception:
            db.rollback()
            raise
    return estado()
