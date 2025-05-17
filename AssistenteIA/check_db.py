import sqlite3

def check_db():
    conn = sqlite3.connect('validacao_triagem.db')
    cursor = conn.cursor()
    
    # Verifica as tabelas existentes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tabelas existentes:", [table[0] for table in tables])
    
    # Verifica dados na tabela casos_iniciais
    cursor.execute("SELECT COUNT(*) FROM casos_iniciais;")
    count = cursor.fetchone()[0]
    print("\nNúmero de casos iniciais:", count)
    
    if count > 0:
        print("\nPrimeiro caso inicial:")
        cursor.execute("SELECT * FROM casos_iniciais LIMIT 1;")
        print(cursor.fetchone())
    
    conn.close()

if __name__ == "__main__":
    check_db()
