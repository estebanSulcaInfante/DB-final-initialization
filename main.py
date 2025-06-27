import psycopg2
from faker import Faker
from faker_food import FoodProvider
from random import randint, choice, sample
import sys

# Inicializar Faker con proveedor de comida
fake = Faker()
fake.add_provider(FoodProvider)

def connect_db():
    return psycopg2.connect(
        host="localhost",
        database="final_project",
        user="postgres",
        password="1234"
    )

# --- Generadores de datos para cada tabla ---

def create_usuario(cursor, n):
    usuarios = []
    for _ in range(n):
        nombre = fake.first_name()[:20]
        apellido = fake.last_name()[:25]
        telefono = fake.phone_number()[:30]
        usuarios.append((nombre, apellido, telefono))
    cursor.executemany(
        "INSERT INTO Usuario (nombre, apellido, numero_telef) VALUES (%s, %s, %s)", usuarios)
    cursor.execute("SELECT id_usuario FROM Usuario ORDER BY id_usuario DESC LIMIT %s", (n,))
    return [row[0] for row in cursor.fetchall()][::-1]


def create_cliente(cursor, usuario_ids):
    clientes = [(uid, fake.company()[:50]) for uid in usuario_ids]
    cursor.executemany("INSERT INTO Cliente (id_usuario, empresa) VALUES (%s, %s)", clientes)
    return usuario_ids.copy()


def create_trabajador(cursor, usuario_ids):
    trabajadores = [(uid, fake.phone_number()[:30]) for uid in usuario_ids]
    cursor.executemany("INSERT INTO Trabajador (id_usuario, nro_telef_emergencia) VALUES (%s, %s)", trabajadores)
    return usuario_ids.copy()


def create_repartidor(cursor, trabajador_ids, k):
    repart = sample(trabajador_ids, k)
    cursor.executemany("INSERT INTO Repartidor (id_usuario) VALUES (%s)", [(rid,) for rid in repart])
    return repart


def create_administrador(cursor, trabajador_ids, k):
    admins = sample(trabajador_ids, k)
    registros = [(uid, fake.email()[:50]) for uid in admins]
    cursor.executemany("INSERT INTO Administrador (id_usuario, correo) VALUES (%s, %s)", registros)
    return admins


def create_menu(cursor, admin_ids, m):
    menus = []
    for _ in range(m):
        id_admin = choice(admin_ids)
        variacion = fake.word()[:50]
        fecha = fake.date_between(start_date='-1y', end_date='today')
        menus.append((id_admin, variacion, fecha))
    cursor.executemany(
        "INSERT INTO Menu (id_administrador, variacion, fecha) VALUES (%s, %s, %s)", menus)
    cursor.execute("SELECT id_menu FROM Menu ORDER BY id_menu DESC LIMIT %s", (m,))
    return [row[0] for row in cursor.fetchall()][::-1]


def create_plato(cursor, p):
    platos = []
    for _ in range(p):
        # Generar nombre coherente de plato usando faker-food
        nombre = fake.dish()
        foto = fake.image_url()
        tipo = choice(['Entrante', 'Principal', 'Postre', 'Bebida'])[:30]
        categoria = choice(['Vegano', 'Vegetariano', 'Carne', 'Pescado', 'Sin Gluten'])[:30]
        cod_nutri = fake.uuid4()[:36]
        platos.append((nombre, foto, tipo, categoria, cod_nutri))
    cursor.executemany(
        "INSERT INTO Plato (nombre, foto, tipo, categoria, codigo_info_nutricional) VALUES (%s, %s, %s, %s, %s)", platos)
    cursor.execute("SELECT id_plato FROM Plato ORDER BY id_plato DESC LIMIT %s", (p,))
    return [row[0] for row in cursor.fetchall()][::-1]


def create_pertenece(cursor, menu_ids, plato_ids):
    relaciones = []
    for mid in menu_ids:
        seleccion = sample(plato_ids, k=randint(1, min(4, len(plato_ids))))
        for pid in seleccion:
            relaciones.append((mid, pid))
    cursor.executemany("INSERT INTO Pertenece (id_menu, id_plato) VALUES (%s, %s)", relaciones)


def create_zona_entrega(cursor):
    zonas = [('Zona Norte', 5.00), ('Zona Sur', 7.50), ('Centro', 6.25)]
    cursor.executemany("INSERT INTO ZonaEntrega (nombre, costo) VALUES (%s, %s)", zonas)
    return [z[0] for z in zonas]


def create_pedido(cursor, usuario_ids, zonas, t):
    pedidos = []
    for _ in range(t):
        fecha = fake.date_time_between(start_date='-30d', end_date='now')
        estado = choice(['Pendiente', 'Enviado', 'Entregado', 'Cancelado'])
        hs, he, he_est = fake.time(), fake.time(), fake.time()
        direccion = fake.address()[:200]
        zona = choice(zonas)
        pedidos.append((fecha, estado, hs, he, he_est, direccion, zona))
    cursor.executemany(
        "INSERT INTO Pedido (fecha, estado, hora_salida, hora_entrega, hora_entrega_estimada, direccion_exacta, zona_entrega) VALUES (%s,%s,%s,%s,%s,%s,%s)", pedidos)
    cursor.execute("SELECT id_pedido FROM Pedido ORDER BY id_pedido DESC LIMIT %s", (t,))
    return [row[0] for row in cursor.fetchall()][::-1]


def create_tiene(cursor, pedido_ids, menu_ids):
    rel = [(pid, mid) for pid in pedido_ids for mid in sample(menu_ids, k=randint(1,3))]
    cursor.executemany("INSERT INTO Tiene (id_pedido, id_menu) VALUES (%s, %s)", rel)


def create_hace(cursor, pedido_ids, user_ids):
    rel = [(pid, choice(user_ids), randint(1,5), fake.text(max_nb_chars=100)) for pid in pedido_ids]
    cursor.executemany("INSERT INTO Hace (id_pedido, id_usuario, calificacion, comentario) VALUES (%s,%s,%s,%s)", rel)


def create_vive(cursor, usuario_ids, zonas):
    rel = [(choice(zonas), uid) for uid in usuario_ids]
    cursor.executemany("INSERT INTO Vive (zona_entrega, id_usuario) VALUES (%s, %s)", rel)


def create_cubre(cursor, repartidor_ids, zonas):
    rel = [(choice(zonas), rid) for rid in repartidor_ids]
    cursor.executemany("INSERT INTO Cubre (zona_entrega, id_usuario) VALUES (%s,%s)", rel)


def clear_tables(cursor, tables):
    for t in tables:
        cursor.execute(f"DELETE FROM {t} CASCADE")


def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py <num_registros_base>")
        sys.exit(1)
    n = int(sys.argv[1])

    conn = connect_db()
    cur = conn.cursor()

    all_tables = ['Hace','Cubre','Vive','Tiene','Pedido','ZonaEntrega','Pertenece','Plato','Menu','Administrador','Repartidor','Trabajador','Cliente','Usuario']
    clear_tables(cur, all_tables)
    conn.commit()

    user_ids = create_usuario(cur, n)
    cliente_ids = create_cliente(cur, sample(user_ids, k=n//2))
    trab_ids = create_trabajador(cur, sample(user_ids, k=n//2))
    reparto_ids = create_repartidor(cur, trab_ids, k=n//4)
    admin_ids = create_administrador(cur, trab_ids, k=n//8)
    menu_ids = create_menu(cur, admin_ids, m=n)
    plato_ids = create_plato(cur, p=n)
    create_pertenece(cur, menu_ids, plato_ids)
    zonas = create_zona_entrega(cur)
    pedido_ids = create_pedido(cur, user_ids, zonas, t=n)
    create_tiene(cur, pedido_ids, menu_ids)
    create_hace(cur, pedido_ids, user_ids)
    create_vive(cur, user_ids, zonas)
    create_cubre(cur, reparto_ids, zonas)

    conn.commit()
    cur.close()
    conn.close()
    print(f"Esquema sembrado con éxito usando base {n} registros.")

if __name__ == "__main__":
    main()
