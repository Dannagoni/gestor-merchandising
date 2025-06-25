import os
from TPO_FINAL import (
    usuarios,
    sesion_activa,
    cargar_datos,
    guardar_datos,
    es_contraseña_valida,
    es_email_valido,
    registrar_usuario_en_memoria,
    cerrar_sesion,
    obtener_categorias_con_productos,
    formatear_linea_producto,
    formatear_encabezado_categoria,
    obtener_lineas_categoria,
    interpretar_opcion_categoria,
    calcular_subtotal,
    armar_item_para_historial,
    calcular_costo_total,
    actualizar_stock,
    procesar_venta,
    confirmar_y_procesar_venta,
    validar_cantidad,
    manejar_agregado_producto_al_carrito,
    mostrar_carrito_actual,
    buscar_clientes_por_nombre,
    buscar_administradores,
    calcular_indices_paginacion
)

# --- BASE ---

def test_cargar_datos_inexistente_devuelve_default():
    ruta_prueba = "archivo_inventado_para_test.json"
    default = {"lista": []}
    resultado = cargar_datos(ruta_prueba, default)
    assert resultado == default
    os.remove(ruta_prueba)

def test_guardar_y_cargar_datos():
    ruta = "archivo_test.json"
    datos = {"email": "test@test.com", "nombre": "Juan"}
    guardar_datos(ruta, datos)
    leido = cargar_datos(ruta, {})
    assert leido == datos
    os.remove(ruta)


# CREAR USUARIO
def test_contraseña_valida():
    assert es_contraseña_valida("123456@U") == True

def test_contraseña_sin_mayuscula():
    assert es_contraseña_valida("clave123") == False

def test_contraseña_corta():
    assert es_contraseña_valida("C1a") == False

def test_contraseña_sin_mayuscula_y_corta():
    assert es_contraseña_valida("abc") == False

def test_email_valido_correcto():
    usuarios.clear()  # Limpiar antes de probar
    assert es_email_valido("nuevo@ejemplo.com") == True

def test_email_ya_existente():
    usuarios["repetido@ejemplo.com"] = {"nombre": "Ya está", "contraseña": "Test123", "rol": "cliente"}
    assert es_email_valido("repetido@ejemplo.com") == False

def test_email_sin_arroba():
    assert es_email_valido("invalido.com") == False

def test_email_sin_punto():
    assert es_email_valido("invalido@com") == False

def test_registrar_usuario_en_memoria():
    usuarios.clear()
    sesion = {}
    ruta_test = "usuarios_test.json"

    registrar_usuario_en_memoria(
        "test@correo.com",
        "Test",
        "Clave123",
        usuarios,
        sesion,
        ruta_guardado=ruta_test
    )

    assert "test@correo.com" in usuarios
    assert usuarios["test@correo.com"]["nombre"] == "Test"
    assert usuarios["test@correo.com"]["rol"] == "cliente"
    assert sesion["email"] == "test@correo.com"
    assert sesion["rol"] == "cliente"

    # Aseguramos que el archivo de prueba se elimine después
    os.remove(ruta_test)

def test_cerrar_sesion():
    sesion_activa["email"] = "test@correo.com"
    sesion_activa["rol"] = "cliente"
    usuarios["test@correo.com"] = {"nombre": "Test", "rol": "cliente", "contraseña": "Clave123"}

    cerrar_sesion()

    assert sesion_activa["email"] is None
    assert sesion_activa["rol"] is None


# --- TESTS UNITARIOS PARA INVENTARIO ---

def test_obtener_categorias_con_productos():
    stock = {
        "lacteos": {"leche": 3},
        "panaderia": {},
    }
    resultado = obtener_categorias_con_productos(stock)
    assert "lacteos" in resultado
    assert "panaderia" not in resultado

def test_formatear_linea_producto_stock_y_precio():
    linea = formatear_linea_producto("leche", 10, 25.5)
    assert "leche" in linea.lower()
    assert "10" in linea
    assert "$25.50" in linea

def test_formatear_linea_producto_sin_stock():
    linea = formatear_linea_producto("yogur", 0, 10.0)
    assert "Sin stock" in linea

def test_formatear_linea_producto_sin_precio():
    linea = formatear_linea_producto("pan", 2, None)
    assert "No definido" in linea

def test_formatear_encabezado_categoria():
    encabezado = formatear_encabezado_categoria("lacteos")
    assert encabezado[0] == "📁 Categoría: Lacteos"
    assert "Producto" in encabezado[1]
    assert "-" * 50 in encabezado[2]

def test_obtener_lineas_categoria_completo():
    productos = {"leche": 5, "yogur": 0}
    precios = {"leche": 30.0, "yogur": 15.0}
    lineas = obtener_lineas_categoria("lacteos", productos, precios)
    assert any("Leche" in l and "$30.00" in l for l in lineas)
    assert any("Yogur" in l and "Sin stock" in l for l in lineas)

def test_opcion_valida_devuelve_categoria():
    categorias = ["frutas", "bebidas", "panaderia"]
    resultado = interpretar_opcion_categoria(2, categorias)
    assert resultado == "bebidas"

def test_opcion_finalizar_compra():
    categorias = ["frutas", "bebidas"]
    resultado = interpretar_opcion_categoria(3, categorias)  # len = 2, entonces +1 = 3
    assert resultado == "FINALIZAR_COMPRA"

def test_opcion_cancelar_compra():
    categorias = ["frutas", "bebidas"]
    resultado = interpretar_opcion_categoria(4, categorias)  # len = 2, entonces +2 = 4
    assert resultado == "CANCELAR_COMPRA_TOTAL"

def test_opcion_invalida():
    categorias = ["frutas"]
    resultado = interpretar_opcion_categoria(10, categorias)  # opción inválida
    assert resultado is None

def test_calcular_subtotal():
    assert calcular_subtotal(3, 10.0) == 30.0
    assert calcular_subtotal(0, 99.0) == 0.0
    assert calcular_subtotal(1, 0.0) == 0.0
    assert calcular_subtotal(2, 5.5) == 11.0

def test_armar_item_para_historial():
    item = armar_item_para_historial("bebida", "agua", 2, 5.0, 10.0)
    assert item == {
        "categoria": "bebida",
        "producto": "agua",
        "cantidad": 2,
        "precio_unitario": 5.0,
        "subtotal": 10.0
    }

def test_calcular_costo_total():
    items = [
        {"subtotal": 10.0},
        {"subtotal": 15.5},
        {"subtotal": 4.5}
    ]
    assert calcular_costo_total(items) == 30.0
    assert calcular_costo_total([]) == 0.0

def test_actualizar_stock():
    # CASO 1: producto con stock suficiente
    carrito1 = {"remeras:camiseta_negra": {"cantidad": 2}}
    stock1 = {"remeras": {"camiseta_negra": 5}}
    resultado1 = actualizar_stock(carrito1, stock1)
    assert resultado1["remeras"]["camiseta_negra"] == 3

    # CASO 2: producto con stock insuficiente, debe corregirse a 0
    carrito2 = {"pantalones:jean_azul": {"cantidad": 10}}
    stock2 = {"pantalones": {"jean_azul": 4}}
    resultado2 = actualizar_stock(carrito2, stock2)
    assert resultado2["pantalones"]["jean_azul"] == 0

    # CASO 3: producto inexistente en la categoría, el stock no debe cambiar
    carrito3 = {"calzado:zapatillas_blancas": {"cantidad": 1}}
    stock3 = {"calzado": {"botas_negras": 3}}
    resultado3 = actualizar_stock(carrito3, stock3)
    assert resultado3["calzado"]["botas_negras"] == 3

def test_procesar_venta():
    guardados = []

    def guardar(ruta, datos):
        guardados.append((ruta, datos))

    historial = []
    ventas = []
    rutas = {
        "historial_ventas": "h.json",
        "ventas_realizadas": "v.json"
    }

    procesar_venta("m@g.com", [{"producto": "Remera", "cantidad": 1, "precio_unitario": 50, "subtotal": 50}], 50, historial, ventas, guardar, rutas)

    assert len(historial) == 1
    assert len(ventas) == 1
    assert len(guardados) == 2

def test_confirmar_y_procesar_venta():
    guardados = []

    def guardar(ruta, datos):
        guardados.append((ruta, datos))

    def confirmar():
        return True

    def resumen(carrito):
        return 100, [{"categoria": "Electrónica", "producto": "Mouse", "cantidad": 1, "precio_unitario": 100, "subtotal": 100}]

    carrito = {"Electrónica:Mouse": {"cantidad": 1, "precio_unitario_registrado": 100}}
    stock = {"Electrónica": {"Mouse": 3}}
    historial = []
    ventas = []
    rutas = {"stock": "s.json", "ventas_realizadas": "v.json", "historial_ventas": "h.json"}

    ok = confirmar_y_procesar_venta(carrito, "a@a.com", stock, {}, historial, ventas, guardar, rutas, resumen, confirmar)

    assert ok
    assert stock["Electrónica"]["Mouse"] == 2
    assert len(historial) == 1
    assert len(ventas) == 1
    assert len(guardados) == 3

def test_validar_cantidad_none():
    assert validar_cantidad(None, 5) == -1

def test_validar_cantidad_vacia():
    assert validar_cantidad("", 5) == "continuar"

def test_validar_cantidad_no_numerica():
    assert validar_cantidad("abc", 5) == "continuar"

def test_validar_cantidad_negativa():
    assert validar_cantidad("-2", 5) == "continuar"

def test_validar_cantidad_mayor_stock():
    assert validar_cantidad("10", 5) == "continuar"

def test_validar_cantidad_cero():
    assert validar_cantidad("0", 5) == 0

def test_validar_cantidad_valida():
    assert validar_cantidad("3", 5) == 3



#Simula que se agrega 1 unidad de "camisa".
#Verifica que el carrito se actualiza correctamente.
#Verifica que el stock se descuenta.

def test_manejar_agregado_producto_simple():
    carrito = {}
    stock = {"ropa": {"camisa": 3}}
    precios = {"ropa": {"camisa": 15.0}}

    def cantidad_fija(*_):
        return 1  # Simula que el usuario quiere agregar 1

    manejar_agregado_producto_al_carrito(
        carrito_cliente=carrito,
        categoria="ropa",
        producto_key="camisa",
        stock=stock,
        precios=precios,
        solicitar_cantidad_fn=cantidad_fija
    )

    assert carrito == {
        "ropa:camisa": {
            "cantidad": 1,
            "precio_unitario_registrado": 15.0,
            "producto_display": "Camisa",
            "categoria_display": "Ropa"
        }
    }
    assert stock["ropa"]["camisa"] == 2

def test_mostrar_carrito_actual():
    # Solo verifica que no lance excepciones
    try:
        mostrar_carrito_actual({})
        mostrar_carrito_actual({"test:item": {"cantidad": 1}})
        assert True  # Si llegó aquí sin errores, pasa la prueba
    except Exception:
        assert False, "La función lanzó una excepción inesperada"

def test_buscar_clientes_por_nombre():
    # 1. Buscar cliente existente
    usuarios = {
        "ceo@gmail.com": {
            "nombre": "Danna Goni CEO",
            "contraseña": "123",
            "rol": "administrador"
        },
        "jefa@gmail.com": {
            "nombre": "Gaby Espinosa",
            "contraseña": "1234",
            "rol": "administrador"
        },
        "supervisor@gmail.com": {
            "nombre": "Nico Bayon",
            "contraseña": "456",
            "rol": "administrador"
        },
        "agus@gmail.com": {
            "nombre": "Agustin Fernandez",
            "contraseña": "789",
            "rol": "cliente"
        },
        "roma@gmail.com": {
            "nombre": "Roma Moyano",
            "contraseña": "101",
            "rol": "cliente"
        },
        "kiara@gmail.com": {
            "nombre": "Kiara Moyano",
            "contraseña": "111",
            "rol": "cliente"
        },
        "figa@gmail.com": {
            "nombre": "Bauti Crespo",
            "contraseña": "777",
            "rol": "cliente"
        },
        "djsergio@gmail.com": {
            "nombre": "Sebastian Villavicenio",
            "contraseña": "121",
            "rol": "cliente"
        },
        "gabriela@gmail.com": {
            "nombre": "Gabriela Espinosa",
            "contraseña": "123456U",
            "rol": "cliente"
        },
        "ruby@gmail.com": {
            "nombre": "Ruby Fernandez Moyano",
            "contraseña": "wauwaU123",
            "rol": "administrador"
        },
        "da@gmail.com": {
            "nombre": "Danna",
            "contraseña": "D12345",
            "rol": "cliente"
        },
        "cliente1@example.com": {
            "nombre": "Juan Pérez", 
            "rol": "cliente"
        },
        "cliente2@example.com": {
            "nombre": "Ana Gómez", 
            "rol": "cliente"
        },
        "admin@example.com": {
            "nombre": "Carlos Admin", 
            "rol": "admin"
        },
        "cliente3@example.com": {
            "nombre": "Juanita Pérez", 
            "rol": "cliente"}
    }
    resultado = buscar_clientes_por_nombre("Juanita Pérez", usuarios)
    print(resultado)

    esperado = [
        ("cliente3@example.com", "Juanita Pérez")
    ]

    assert resultado == esperado, f"Error: {resultado} != {esperado}"

    # 2. Buscar cliente no existente
    resultado = buscar_clientes_por_nombre("Pedro", usuarios)
    esperado = []
    assert resultado == esperado, f"Error: {resultado} != {esperado}"

    # 3. Buscar cliente con espacios
    resultado = buscar_clientes_por_nombre("  Ana  ", usuarios)
    esperado = [("cliente2@example.com", "Ana Gómez")]
    assert resultado == esperado, f"Error: {resultado} != {esperado}"

    # 4. Buscar cliente case insensitive
    resultado = buscar_clientes_por_nombre("JUAN", usuarios)
    esperado = [
        ("cliente1@example.com", "Juan Pérez"),
        ("cliente3@example.com", "Juanita Pérez")
    ]
    assert resultado == esperado, f"Error: {resultado} != {esperado}"

    print("Todas las pruebas pasaron.")

def test_buscar_administradores():
    # Datos de prueba
    usuarios = {
        "ceo@gmail.com": {
            "nombre": "Danna Goni CEO",
            "contraseña": "123",
            "rol": "administrador"
        },
        "jefa@gmail.com": {
            "nombre": "Gaby Espinosa",
            "contraseña": "1234",
            "rol": "administrador"
        },
        "supervisor@gmail.com": {
            "nombre": "Nico Bayon",
            "contraseña": "456",
            "rol": "administrador"
        },
        "agus@gmail.com": {
            "nombre": "Agustin Fernandez",
            "contraseña": "789",
            "rol": "cliente"
        },
        "roma@gmail.com": {
            "nombre": "Roma Moyano",
            "contraseña": "101",
            "rol": "cliente"
        },
        "kiara@gmail.com": {
            "nombre": "Kiara Moyano",
            "contraseña": "111",
            "rol": "cliente"
        },
        "figa@gmail.com": {
            "nombre": "Bauti Crespo",
            "contraseña": "777",
            "rol": "cliente"
        },
        "djsergio@gmail.com": {
            "nombre": "Sebastian Villavicenio",
            "contraseña": "121",
            "rol": "cliente"
        },
        "gabriela@gmail.com": {
            "nombre": "Gabriela Espinosa",
            "contraseña": "123456U",
            "rol": "cliente"
        },
        "ruby@gmail.com": {
            "nombre": "Ruby Fernandez Moyano",
            "contraseña": "wauwaU123",
            "rol": "administrador"
        },
        "da@gmail.com": {
            "nombre": "Danna",
            "contraseña": "D12345",
            "rol": "cliente"
        },
        "cliente1@example.com": {
            "nombre": "Juan Pérez", 
            "rol": "cliente"
        },
        "cliente2@example.com": {
            "nombre": "Ana Gómez", 
            "rol": "cliente"
        },
        "admin@example.com": {
            "nombre": "Carlos Admin", 
            "rol": "admin"
        },
        "cliente3@example.com": {
            "nombre": "Juanita Pérez", 
            "rol": "cliente"
        }
    }

    # Casos de prueba
    casos_prueba = [
        ("danna", [("ceo@gmail.com", "Danna Goni CEO")]),
        ("gaby", [("jefa@gmail.com", "Gaby Espinosa")]),
        ("nico", [("supervisor@gmail.com", "Nico Bayon")]),
        ("ruby", [("ruby@gmail.com", "Ruby Fernandez Moyano")]),
        ("pedro", []),  # No existe
        ("", []),  # Búsqueda vacía
        ("  gaby  ", [("jefa@gmail.com", "Gaby Espinosa")]),  # Espacios en blanco
        ("GABY", [("jefa@gmail.com", "Gaby Espinosa")]),  # Case insensitive
    ]

    # Ejecutar pruebas
    for i, (nombre_buscar, esperado) in enumerate(casos_prueba, 1):
        resultado = buscar_administradores(nombre_buscar, usuarios)
        assert resultado == esperado, f"""
        Caso {i} falló:
        - Búsqueda: '{nombre_buscar}'
        - Esperado: {esperado}
        - Obtenido: {resultado}
        """

def test_calcular_indices_paginacion():
    # Casos de prueba
    casos_prueba = [
        (1, 10, (0, 10)),  # Primera página, 10 ventas por página
        (2, 10, (10, 20)),  # Segunda página, 10 ventas por página
        (3, 10, (20, 30)),  # Tercera página, 10 ventas por página
        (1, 5, (0, 5)),  # Primera página, 5 ventas por página
        (2, 5, (5, 10)),  # Segunda página, 5 ventas por página
        (0, 10, (-10, 0)),  # Página 0, 10 ventas por página (caso no válido)
    ]

    # Ejecutar pruebas
    for i, (pagina_actual, ventas_por_pagina, esperado) in enumerate(casos_prueba, 1):
        resultado = calcular_indices_paginacion(pagina_actual, ventas_por_pagina)
        assert resultado == esperado, f"""
        Caso {i} falló:
        - Página actual: {pagina_actual}
        - Ventas por página: {ventas_por_pagina}
        - Esperado: {esperado}
        - Obtenido: {resultado}
        """

    print("✅ Todos los casos de prueba pasaron correctamente")
