## Proyecto: Seeder de Base de Datos PostgreSQL

Este repositorio contiene un script (`main.py`) para sembrar datos de prueba en un esquema PostgreSQL basado en un conjunto de tablas de usuarios, clientes, trabajadores, repartidores, administradores, menús, platos, zonas de entrega, pedidos y relaciones entre estas.

---

### 📋 Contenido

- `main.py`: Script principal en Python que:
  1. Se conecta a la base de datos PostgreSQL.
  2. Limpia (DELETE CASCADE) las tablas en el orden correcto.
  3. Inserta datos de prueba en todas las tablas usando Faker y faker-food.

---

### 🚀 Requisitos

- Python 3.7 o superior
- PostgreSQL corriendo (host, base de datos, usuario y contraseña configurados)
- Dependencias de Python:
  ```bash
  pip install -r requirements.txt
  ```

---

### ⚙️ Configuración

Edita la función `connect_db()` en `main.py` para apuntar a tu instancia pon tus credenciales del LOCAL:

```python
def connect_db():
    return psycopg2.connect(
        host="localhost",
        database="bddproyecto",
        user="postgres",
        password="1234"
    )
```

---

### 📥 Uso

1. Asegúrate de tener el esquema (tablas) creado en PostgreSQL. Usa tu script DDL para generar las tablas.
2. Ejecuta el seeder pasando como argumento el número base de registros:
   ```bash
   python main.py <num_registros_base>
   ```
   - `<num_registros_base>`: número de usuarios, menús, platos y pedidos a generar.

Ejemplo:

```bash
python main.py 1000
```

Esto:

- Generará 1 000 usuarios.
- Creará clientes y trabajadores a partir de la mitad de esos usuarios.
- Tendrás 250 repartidores y 125 administradores.
- Sembrará 1 000 menús y 1 000 platos.
- Insertará 1 000 pedidos y sus relaciones.

---

### 🔧 Personalización

- **Proveedores de datos**: Faker y faker-food ofrecen muchos métodos. Puedes cambiar:
  - `fake.dish()` por otros sabores o ingredientes.
  - `fake.company()`, `fake.address()`, etc.
- **Proporciones**: Ajusta en `main.py` el número de repartidores (`n//4`), administradores (`n//8`) o relaciones.
- **Tablas adicionales**: Añade funciones nuevas siguiendo el patrón.

---

### 📖 Estructura del proyecto

```
├── main.py
└── README.md
```

---

### ❓ Preguntas

Si encuentras errores o tienes sugerencias, abre un *issue* o contáctame por correo.

