import sqlite3

def init_db():
    with open('database_schema.sql', 'r', encoding='utf-8') as sql_file:
        sql_script = sql_file.read()
    
    conn = sqlite3.connect('validacao_triagem.db')
    cursor = conn.cursor()
    cursor.executescript(sql_script)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Banco de dados inicializado com sucesso!")
