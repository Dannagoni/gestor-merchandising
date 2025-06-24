import json
import os
import re
from functools import reduce
import log.logger as logger

# ==============================================================================
# Definición de Rutas para Archivos JSON 
# ==============================================================================
RUTA_USUARIOS = "usuarios.json"
RUTA_STOCK = "stock.json"
RUTA_PRECIOS = "precios.json"
RUTA_HISTORIAL_VENTAS = "historial_ventas.json"
RUTA_VENTAS_REALIZADAS = "ventas_realizadas.json"

def cargar_datos(ruta_archivo, tipo_dato_default):
    """
    Carga datos desde un archivo JSON.
    Si el archivo no existe, devuelve el tipo de dato por defecto (lista o diccionario vacío).
    """
    if not os.path.exists(ruta_archivo):
        with open(ruta_archivo, 'w', encoding='utf-8') as archivo_nuevo:
            json.dump(tipo_dato_default, archivo_nuevo, indent=4, ensure_ascii=False)
        logger.info(f"El archivo {ruta_archivo} no existía. Se creó con datos por defecto.")
        logger.debug(f"Datos por defecto usados para {ruta_archivo}: {tipo_dato_default}")
        return tipo_dato_default

    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            contenido = archivo.read()
            if not contenido:
                logger.debug(f"El archivo {ruta_archivo} estaba vacío. Se usaron datos por defecto: {tipo_dato_default}")
                return tipo_dato_default
            archivo.seek(0)
            datos = json.load(archivo)
            logger.info(f"Los datos de {ruta_archivo} se cargaron correctamente.")
            logger.debug(f"Contenido cargado desde {ruta_archivo}: {datos}")
            return datos
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"No se pudo cargar el archivo {ruta_archivo} o está corrupto. Se usarán datos por defecto.")
        logger.debug(f"Excepción: {e}")
        print(f"⚠️ No se pudo cargar el archivo {ruta_archivo} o está corrupto. Se usarán datos por defecto.")
        with open(ruta_archivo, 'w', encoding='utf-8') as archivo_nuevo:
            json.dump(tipo_dato_default, archivo_nuevo, indent=4, ensure_ascii=False)
        return tipo_dato_default

def guardar_datos(ruta_archivo, datos):
    """
    Guarda los datos proporcionados en un archivo JSON.
    """
    try:
        with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)

        logger.info(f"Los datos de {ruta_archivo} se guardaron correctamente.")
        logger.debug(f"Contenido guardado en {ruta_archivo}: {datos}")
    except IOError as e:
        logger.error(f"Error: No se pudieron guardar los datos en {ruta_archivo}.")
        logger.debug(f"Excepción al guardar {ruta_archivo}: {e}")
        print(f"❌ Error: No se pudieron guardar los datos en {ruta_archivo}.")

def registrar_usuario_en_memoria(email, nombre, contraseña, usuarios, sesion_activa, ruta_guardado=RUTA_USUARIOS):
    rol = "cliente"
    usuarios[email] = {
        "nombre": nombre,
        "contraseña": contraseña,
        "rol": rol,
        "activo": True
    }
    guardar_datos(ruta_guardado, usuarios)
    sesion_activa["email"] = email
    sesion_activa["rol"] = rol
    
# ===============
# Carga de Datos
# ===============
usuarios = cargar_datos(RUTA_USUARIOS, {})
stock = cargar_datos(RUTA_STOCK, {})
precios = cargar_datos(RUTA_PRECIOS, {})
historial_ventas = cargar_datos(RUTA_HISTORIAL_VENTAS, [])
ventas_realizadas = cargar_datos(RUTA_VENTAS_REALIZADAS, [])

sesion_activa = {
    "email": None,
    "rol": None
}

def pedir_input_con_cancelar(mensaje):
    # ingrese usuario: 
    respuesta = input(mensaje).strip()
    if respuesta == "":
        print("↩️ Operación cancelada.")
        return None
    return respuesta

# VALIDACIONES PARA INICIO DE SESION Y REGISTRO
def es_email_valido(email):
    # Expresión regular para validar el formato del email
    patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron_email, email) is not None and email not in usuarios

def es_contraseña_valida(contraseña):
    # Valida: 6 caracteres o mas, debe contener, mayus, caracter especial
    patron_contraseña = r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&()])[A-Za-z\d@$!%*?&()]{6,}$'
    return re.match(patron_contraseña, contraseña) is not None

def es_email_registrado(email):
    return email in usuarios

def es_contraseña_correcta(email, contraseña):
    return usuarios[email]["contraseña"] == contraseña

def obtener_email_valido():
    while True:
        email_input = pedir_input_con_cancelar("Ingresá tu email: ")
        if email_input is None:
            return None

        email = email_input.lower()

        if email in usuarios:
            print("⚠️ Ya existe un usuario registrado con ese email. Intentá con otro.")
        elif not es_email_valido(email):
            print("⚠️ El email debe contener '@' y '.'. Intentá de nuevo.")
            print()
        else:
            return email

def obtener_nombre():
    return pedir_input_con_cancelar("Ingresá tu nombre completo: ")

def obtener_contraseña_confirmada():
    while True:
        contraseña = pedir_input_con_cancelar("Ingresá una contraseña (mín. 6 caracteres, 1 mayúscula, 1 caracter especial): ")
        if contraseña is None:
            return None

        if not es_contraseña_valida(contraseña):
            print("⚠️ La contraseña debe tener al menos 6 caracteres, una mayúscula y un caracter especial.")
            print()
            continue

        confirmar = pedir_input_con_cancelar("Confirmá la contraseña: ")
        if confirmar is None:
            return None

        if contraseña == confirmar:
            return contraseña
        else:
            print("⚠️ Las contraseñas no coinciden. Intentá nuevamente.")

def obtener_email_existente():
    while True:
        email_input = pedir_input_con_cancelar("Ingresá tu email: ")
        if email_input is None:
            return None

        email = email_input.lower()

        if es_email_registrado(email):
            return email
        else:
            print("⚠️ El email no está registrado. Volvé a intentarlo o registrate.")

def obtener_contraseña_para_login(email):
    while True:
        contraseña_ingresada = pedir_input_con_cancelar("Ingresá tu contraseña: ")
        if contraseña_ingresada is None:
            return None

        if es_contraseña_correcta(email, contraseña_ingresada):
            return contraseña_ingresada
        else:
            print("⚠️ Contraseña incorrecta. Volvé a intentarlo.")

# CREAR, INICIAR SESIÓN, CERRAR SESIÓN
def crear_usuario(stock, precios, sesion_activa, historial_ventas, ventas_realizadas):
    print("\n--- Registrarse ---")
    print("(Podés presionar Enter en cualquier momento para cancelar)")

    try:
        email = obtener_email_valido()
        if email is None:
            logger.info("Registro cancelado al ingresar el email.")
            return

        nombre = obtener_nombre()
        if nombre is None:
            logger.info(f"Registro cancelado por el usuario {email} al ingresar el nombre.")
            return

        contraseña = obtener_contraseña_confirmada()
        if contraseña is None:
            logger.info(f"Registro cancelado por el usuario {email} al ingresar la contraseña.")
            return

        registrar_usuario_en_memoria(email, nombre, contraseña, usuarios, sesion_activa)

        logger.info(f"Usuario {email} redirigido al menú cliente después del registro.")

        print(f"\n✅ ¡Registro exitoso para {nombre} como CLIENTE!")
        print(f"✅ ¡Bienvenido/a, {nombre}!")
        print(f"Rol: {sesion_activa['rol'].capitalize()}")

        menu_cliente(stock, precios, sesion_activa, historial_ventas, ventas_realizadas, email)

    except Exception as e:
        logger.error(f"Error inesperado durante el registro de usuario {email if 'email' in locals() else '[desconocido]'}: {e}")
        print("❌ Hubo un error al registrarse. Por favor, intentá de nuevo.")

def iniciar_sesion():
    print("\n--- Iniciar Sesión ---")
    print("(Podés presionar Enter en cualquier momento para cancelar)")

    try:
        email = obtener_email_existente()
        if email is None:
            logger.info("Inicio de sesión cancelado al ingresar el email.")
            return

        contraseña = obtener_contraseña_para_login(email)
        if contraseña is None:
            logger.info(f"Inicio de sesión cancelado por el usuario {email} al ingresar la contraseña.")
            return

        sesion_activa["email"] = email
        sesion_activa["rol"] = usuarios[email]["rol"]

        logger.info(f"Inicio de sesión exitoso: {email} (rol: {usuarios[email]['rol']})")

        print()
        print(f"✅ ¡Bienvenido/a, {usuarios[email]['nombre']}!")
        print(f"Rol: {usuarios[email]['rol'].capitalize()}")

        if usuarios[email]["rol"] == "administrador":
            menu_administrador(stock, precios, usuarios, historial_ventas)
        else:
            menu_cliente(stock, precios, sesion_activa, historial_ventas, ventas_realizadas, email)

    except Exception as e:
        logger.error(f"Error inesperado durante el inicio de sesión: {e}")
        print("❌ Hubo un error al iniciar sesión. Por favor, intentá de nuevo.")

def cerrar_sesion():
    try:
        if sesion_activa["email"]:
            nombre_usuario = usuarios.get(sesion_activa["email"], {}).get("nombre", sesion_activa["email"])
            print(f"\n🔒 Sesión cerrada para {nombre_usuario}.")
            logger.info(f"Sesión cerrada para {sesion_activa['email']}.")
            sesion_activa["email"] = None
            sesion_activa["rol"] = None
        else:
            print("\nℹ️ No hay una sesión activa para cerrar.")
            logger.info("Se intentó cerrar sesión sin que haya una sesión activa.")
    except Exception as e:
        logger.error(f"Error al cerrar sesión: {e}")
        print("❌ Hubo un error al cerrar sesión.")

# INVENTARIO Y STOCK
def obtener_categorias_con_productos(stock_actual):
    """Devuelve un diccionario con las categorías que tienen productos."""
    return dict(filter(lambda item: len(item[1]) > 0, stock_actual.items()))

def formatear_encabezado_categoria(categoria):
    return [
        f"📁 Categoría: {categoria.capitalize()}",
        f"    {'Producto':<25} | {'Stock':<12} | {'Precio':<10}",
        "    " + "-" * 50
    ]

def formatear_linea_producto(producto, cantidad, precio):
    stock_str = "Sin stock" if cantidad <= 0 else str(cantidad)
    precio_str = f"${precio:.2f}" if precio is not None else "No definido"
    return f"    - {producto.capitalize():<24} | {stock_str:<12} | {precio_str:<10}"

def obtener_lineas_categoria(categoria, productos, precios_categoria):
    lineas = formatear_encabezado_categoria(categoria)
    for producto, cantidad in sorted(productos.items()):
        precio = precios_categoria.get(producto.lower())
        linea = formatear_linea_producto(producto, cantidad, precio)
        lineas.append(linea)
    lineas.append("-" * 40)
    return lineas

def mostrar_stock_detallado(stock_actual, precios_actuales):
    print("\n📦 Inventario Actual:")
    print("-" * 70)

    if not stock_actual:
        print("El inventario de stock está vacío.")
        print("-" * 70)
        return

    categorias_con_productos = stock_actual

    if not categorias_con_productos:
        print("No hay categorías con productos para mostrar.")
        print("-" * 70)
        return

    for categoria, productos in sorted(categorias_con_productos.items()):
        precios_categoria = precios_actuales.get(categoria, {})
        lineas = obtener_lineas_categoria(categoria, productos, precios_categoria)
        for linea in lineas:
            print(linea)

    print("-" * 70)

def obtener_categorias_validas(stock_disponible):
    return {
        cat: productos for cat, productos in stock_disponible.items()
        if any(cantidad > 0 for cantidad in productos.values())
    }

def mostrar_categorias_disponibles(lista_categorias):
    for i, cat_key in enumerate(lista_categorias):
        print(f"{i + 1}) {cat_key.capitalize()}")
    print(f"\n{len(lista_categorias) + 1}) ✅ Finalizar compra y ver carrito")
    print(f"{len(lista_categorias) + 2}) ❌ Cancelar compra y volver al menú")

def interpretar_opcion_categoria(opcion, lista_categorias):
    if 1 <= opcion <= len(lista_categorias):
        return lista_categorias[opcion - 1]
    elif opcion == len(lista_categorias) + 1:
        return "FINALIZAR_COMPRA"
    elif opcion == len(lista_categorias) + 2:
        return "CANCELAR_COMPRA_TOTAL"
    else:
        print("⚠️ Opción de categoría inválida. Intentá de nuevo.")
        return None

def seleccionar_categoria_para_compra(stock_disponible):
    print("\n🛒 ¿De qué categoría te gustaría comprar?")

    categorias_validas = obtener_categorias_validas(stock_disponible)

    if not categorias_validas:
        print("ℹ️ Lo sentimos, no hay productos disponibles en este momento.")
        return "CANCELAR_COMPRA_TOTAL"

    lista_categorias_mostrables = sorted(categorias_validas.keys())

    mostrar_categorias_disponibles(lista_categorias_mostrables)

    while True:
        try:
            opcion_str = pedir_input_con_cancelar("\n→ Elegí una opción de categoría (o Enter para cancelar esta selección): ")
            if opcion_str is None:
                return "VOLVER_MENU_CLIENTE"
            if not opcion_str:
                continue
            opcion = int(opcion_str)

            resultado = interpretar_opcion_categoria(opcion, lista_categorias_mostrables)
            if resultado is not None:
                return resultado

        except ValueError:
            print("⚠️ Entrada inválida. Por favor, ingresá un número.")

def obtener_productos_con_stock(productos_en_categoria):
    return {
        prod: stock_val for prod, stock_val in productos_en_categoria.items() if stock_val > 0
    }

def mostrar_lista_productos(productos_mostrables, precios_categoria):
    lista_productos = sorted(productos_mostrables.keys())
    for i, prod_key in enumerate(lista_productos):
        precio_unitario = precios_categoria.get(prod_key.lower(), 0.0)
        stock_actual = productos_mostrables[prod_key]
        print(f"  {i + 1}) {prod_key.capitalize()} (Stock: {stock_actual}, Precio: ${precio_unitario:.2f})")
    return lista_productos

def mostrar_opcion_volver(indice):
    print(f"\n  {indice}) ↩️ Volver a elegir categoría")

def seleccionar_producto_para_compra(categoria_key, productos_en_categoria, precios_categoria):
    """
    Muestra productos de una categoría con stock y permite al cliente seleccionar uno.
    """
    print(f"\n 🛒 Productos disponibles en '{categoria_key.capitalize()}':")
    productos_mostrables = obtener_productos_con_stock(productos_en_categoria)

    if not productos_mostrables:
        print(f"ℹ️ No quedan productos con stock en la categoría '{categoria_key.capitalize()}'.")
        return None

    lista_productos_mostrables = mostrar_lista_productos(productos_mostrables, precios_categoria)
    mostrar_opcion_volver(len(lista_productos_mostrables) + 1)

    while True:
        try:
            opcion_str = pedir_input_con_cancelar("  → Elegí el producto (o Enter para volver a categorías): ")
            if opcion_str is None:
                return None  # Volver a categorías
            if not opcion_str:
                continue
            opcion = int(opcion_str)

            if 1 <= opcion <= len(lista_productos_mostrables):
                return lista_productos_mostrables[opcion - 1]
            elif opcion == len(lista_productos_mostrables) + 1:
                return None  # Volver a categorías
            else:
                print("⚠️ Opción de producto inválida. Intentá de nuevo.")
        except ValueError:
            print("⚠️ Entrada inválida. Por favor, ingresá un número.")

def validar_cantidad(cantidad_str, stock_para_agregar):
    try:
        if cantidad_str is None:
            return -1
        if not cantidad_str:
            return "continuar"
        cantidad = int(cantidad_str)

        if cantidad == 0:
            return 0
        if cantidad < 0:
            print("⚠️ La cantidad no puede ser negativa.")
            return "continuar"
        if cantidad > stock_para_agregar:
            print(f"⚠️ No podés agregar más de {stock_para_agregar} unidades.")
            return "continuar"
        return cantidad
    except ValueError:
        print("⚠️ Ingresaste algo que no es un número.")
        return "continuar"

def solicitar_cantidad_producto(producto_key, stock_disponible_real, cantidad_en_carrito_actual):
    """
    Pide al cliente la cantidad de un producto, validando contra el stock disponible.
    """
    stock_para_agregar = stock_disponible_real
    if stock_para_agregar <= 0:
        print(f"ℹ️ Ya no hay más stock disponible para agregar de '{producto_key.capitalize()}' (o ya está todo en tu carrito).")
        return 0

    while True:
        cantidad_str = pedir_input_con_cancelar(f"  → ¿Cuántas unidades querés agregar? (0 para no agregar, Enter para cancelar selección de cantidad): ")
        resultado = validar_cantidad(cantidad_str, stock_para_agregar)

        if resultado == "continuar":
            continue
        return resultado

def calcular_subtotal(cantidad, precio_unitario):
    return cantidad * precio_unitario

def armar_item_para_historial(categoria, producto, cantidad, precio_unitario, subtotal):
    return {
        "categoria": categoria,
        "producto": producto,
        "cantidad": cantidad,
        "precio_unitario": precio_unitario,
        "subtotal": subtotal
    }

def calcular_costo_total(items_historial):
    return reduce(lambda acc, item: acc + item['subtotal'], items_historial, 0.0)

def mostrar_encabezado():
    print("-" * 70)
    print(f"{'Producto (Categoría)':<35} | {'Cantidad':<10} | {'P. Unit.':<10} | {'Subtotal':<10}")
    print("-" * 70)

def mostrar_linea_producto(producto_display, categoria_display, cantidad, precio_unitario, subtotal):
    print(f"- {producto_display:<25} ({categoria_display}) | {cantidad:<10} | ${precio_unitario:<9.2f} | ${subtotal:<9.2f}")

def mostrar_pie_resumen(costo_total):
    print("-" * 70)
    print(f"{'Costo Total:':<58} ${costo_total:.2f}")
    print("-" * 70)

def mostrar_resumen_carrito_modificado(carrito_actual_cliente):
    """
    Muestra el resumen del carrito y calcula el costo total.
    """
    if not carrito_actual_cliente:
        print("El carrito está vacío.")
        return 0.0, []

    mostrar_encabezado()
    items_para_historial = []

    for clave_carrito, detalles_item in sorted(carrito_actual_cliente.items()):
        categoria, producto_original = clave_carrito.split(":", 1)
        cantidad = detalles_item["cantidad"]
        precio_unitario = detalles_item["precio_unitario_registrado"]
        subtotal = calcular_subtotal(cantidad, precio_unitario)

        producto_display = detalles_item.get("producto_display", producto_original.capitalize())
        categoria_display = detalles_item.get("categoria_display", categoria.capitalize())

        logger.debug(f"Subtotal para '{producto_display}' ({cantidad} uds. x ${precio_unitario:.2f}) = ${subtotal:.2f}")

        items_para_historial.append(
            armar_item_para_historial(categoria, producto_original, cantidad, precio_unitario, subtotal)
        )

        mostrar_linea_producto(producto_display, categoria_display, cantidad, precio_unitario, subtotal)

    costo_total_venta = calcular_costo_total(items_para_historial) if items_para_historial else 0.0
    logger.debug(f"Costo total del carrito para resumen: ${costo_total_venta:.2f}")
    
    mostrar_pie_resumen(costo_total_venta)
    return costo_total_venta, items_para_historial

def actualizar_stock(carrito_actual, stock):
    for clave_carrito, detalles_item_carrito in carrito_actual.items():
        categoria, producto_original = clave_carrito.split(":", 1)
        cantidad_comprada = detalles_item_carrito["cantidad"]

        if categoria in stock and producto_original in stock[categoria]:
            stock[categoria][producto_original] -= cantidad_comprada

            logger.debug(
                f"Stock actualizado: '{producto_original}' en '{categoria}' -{cantidad_comprada} uds. → Nuevo stock: {stock[categoria][producto_original]}"
            )

            if stock[categoria][producto_original] < 0:
                print(f"⚠️ ADVERTENCIA: Stock negativo para {producto_original} en {categoria}. Corrigiendo a 0.")
                logger.error(
                    f"Stock negativo detectado para '{producto_original}' en '{categoria}'. Ajustado a 0."
                )
                stock[categoria][producto_original] = 0
        else:
            print(f"⚠️ ADVERTENCIA CRÍTICA: El producto '{producto_original}' de la categoría '{categoria}' no fue encontrado en el stock para actualizar.")
            logger.error(
                f"Producto no encontrado en stock al actualizar: '{producto_original}' en '{categoria}'."
            )

    return stock

def confirmar_compra():
    while True:
        confirmacion = input("\n¿Confirmás la compra? (s/n): ").strip().lower()
        if confirmacion in ['s', 'n']:
            return confirmacion == 's'
        print("⚠️ Por favor, ingresá 's' para sí o 'n' para no.")

# VENTAS
def procesar_venta(email_cliente, items_para_historial, costo_total_venta, historial_ventas, ventas_realizadas, guardar_datos_func, rutas):
    try:
        venta_registrada = {
            "cliente_email": email_cliente,
            "items": items_para_historial,
            "costo_total": costo_total_venta,
        }

        historial_ventas.append(venta_registrada)
        guardar_datos_func(rutas["historial_ventas"], historial_ventas)

        ventas_realizadas.append({"subtotal": costo_total_venta})
        guardar_datos_func(rutas["ventas_realizadas"], ventas_realizadas)

        logger.info(f"Venta procesada correctamente para {email_cliente}. Total: ${costo_total_venta:.2f}")
    
    except Exception as e:
        logger.error(f"Error al procesar la venta para {email_cliente}: {e}")

def confirmar_y_procesar_venta(
    carrito_actual,
    email_cliente,
    stock,
    precios,
    historial_ventas,
    ventas_realizadas,
    guardar_datos_func=guardar_datos,
    rutas={
        "stock": RUTA_STOCK,
        "ventas_realizadas": RUTA_VENTAS_REALIZADAS,
        "historial_ventas": RUTA_HISTORIAL_VENTAS
    },
    mostrar_resumen_func=mostrar_resumen_carrito_modificado,
    confirmar_func=confirmar_compra  
):
    try:
        if not carrito_actual:
            print("\nℹ️ Tu carrito está vacío. No se procesó ninguna compra.")
            logger.info(f"Compra no procesada: carrito vacío para {email_cliente}.")
            logger.debug(f"Carrito recibido: {carrito_actual}")
            return False

        print("\n📋 --- Resumen Final de tu Carrito ---")
        costo_total_venta, items_para_historial = mostrar_resumen_func(carrito_actual)

        logger.debug(f"Resumen generado - Total: {costo_total_venta}, Items: {items_para_historial}")

        if not items_para_historial and costo_total_venta == 0:
            print("ℹ️ No se pudo procesar el resumen del carrito. Compra no finalizada.")
            logger.info(f"Resumen del carrito inválido para {email_cliente}. No se finalizó la compra.")
            return False

        if confirmar_func():
            logger.debug("El usuario confirmó la compra.")
            stock_actualizado = actualizar_stock(carrito_actual, stock)
            logger.debug(f"Stock actualizado: {stock_actualizado}")

            guardar_datos_func(rutas["stock"], stock_actualizado)
            logger.debug("Stock guardado correctamente.")

            procesar_venta(
                email_cliente,
                items_para_historial,
                costo_total_venta,
                historial_ventas,
                ventas_realizadas,
                guardar_datos_func,
                rutas
            )

            logger.info(f"Compra confirmada por {email_cliente}. Total: ${costo_total_venta:.2f}")
            print("\n✅ ¡Gracias por tu compra!")
            return True
        else:
            print("\n❌ Compra cancelada.")
            logger.info(f"Compra cancelada por el usuario: {email_cliente}")
            return False

    except Exception as e:
        logger.error(f"Error durante el proceso de confirmación de compra para {email_cliente}: {e}")
        print("❌ Ocurrió un error al procesar tu compra.")
        return False

def copiar_stock(stock_original):
    stock_copia = {}
    for categoria, productos in stock_original.items():
        stock_copia[categoria] = {}
        for producto, cantidad in productos.items():
            stock_copia[categoria][producto] = cantidad
    return stock_copia

def ventas_reestructurada(stock, precios, sesion_activa, historial_ventas, ventas_realizadas):
    carrito_cliente = {}
    stock_temp = copiar_stock(stock)
    seguir_comprando = True

    while seguir_comprando:
        mostrar_inicio_tienda(stock_temp, precios)

        accion_categoria = seleccionar_categoria_para_compra(stock_temp)

        seguir_comprando = not manejar_accion_categoria(accion_categoria, carrito_cliente, sesion_activa, precios, historial_ventas, ventas_realizadas, stock)

        if seguir_comprando:
            categoria_elegida = accion_categoria
            producto_elegido_key = seleccionar_producto_para_compra(categoria_elegida, stock_temp[categoria_elegida], precios.get(categoria_elegida, {}))

            if producto_elegido_key is not None:
                manejar_agregado_producto_al_carrito(carrito_cliente, categoria_elegida, producto_elegido_key, stock_temp, precios)
                mostrar_carrito_actual(carrito_cliente)

                seguir_comprando = manejar_opcion_post_agregado(carrito_cliente, sesion_activa, precios, historial_ventas, ventas_realizadas, stock)

    print("\n👋 Saliendo del sistema de compras.")

def mostrar_inicio_tienda(stock, precios):
    print("\n" + "="*15 + " TIENDA VIRTUAL " + "="*15)
    mostrar_stock_detallado(stock, precios)

def manejar_accion_categoria(accion_categoria, carrito_cliente, sesion_activa, precios, historial_ventas, ventas_realizadas, stock_real):
    if accion_categoria == "CANCELAR_COMPRA_TOTAL":
        print("\n↩️ Compra cancelada. Volviendo al menú principal del cliente...")
        return True
    elif accion_categoria == "VOLVER_MENU_CLIENTE":
        print("\n↩️ Volviendo al menú del cliente...")
        return True
    elif accion_categoria == "FINALIZAR_COMPRA":
        if confirmar_y_procesar_venta(carrito_cliente, sesion_activa["email"], stock_real, precios, historial_ventas, ventas_realizadas):
            carrito_cliente.clear()
        if not carrito_cliente or input("¿Desea realizar otra compra o agregar más ítems? (s/n): ").lower() != 's':
            return True
    elif accion_categoria is None:
        return True
    return False

def manejar_agregado_producto_al_carrito(
    carrito_cliente, categoria, producto_key, stock, precios,
    solicitar_cantidad_fn=solicitar_cantidad_producto
):
    try:
        stock_disponible = stock[categoria][producto_key]
        clave_carrito = f"{categoria}:{producto_key}"
        cantidad_actual = carrito_cliente.get(clave_carrito, {}).get("cantidad", 0)

        cantidad_a_agregar = solicitar_cantidad_fn(producto_key, stock_disponible, cantidad_actual)

        if cantidad_a_agregar > 0:
            precio_unitario = precios.get(categoria, {}).get(producto_key, precios.get(categoria, {}).get(producto_key.lower(), 0.0))
            carrito_cliente[clave_carrito] = {
                "cantidad": cantidad_actual + cantidad_a_agregar,
                "precio_unitario_registrado": precio_unitario,
                "producto_display": producto_key.capitalize(),
                "categoria_display": categoria.capitalize()
            }
            stock[categoria][producto_key] -= cantidad_a_agregar
            logger.info(f"'{producto_key}' agregado al carrito ({cantidad_a_agregar} uds.) - Categoría: {categoria}")
            print(f"✅ '{producto_key.capitalize()}' ({cantidad_a_agregar} uds.) agregado/actualizado en el carrito.")
        
        elif cantidad_a_agregar == -1:
            logger.info(f"Adición cancelada por el usuario para el producto '{producto_key}' en la categoría '{categoria}'.")
            print(f"ℹ️ Adición de '{producto_key.capitalize()}' cancelada.")

    except Exception as e:
        logger.error(f"Error al agregar '{producto_key}' al carrito (categoría: {categoria}): {e}")
        print(f"❌ Error al agregar '{producto_key.capitalize()}' al carrito.")

def mostrar_carrito_actual(carrito):
    if carrito:
        print("\n🛒 Carrito Actual:")
        for clave, item in carrito.items():
            cat, prod = clave.split(":", 1)
            print(f"  - {item.get('producto_display', prod.capitalize())} ({item.get('categoria_display', cat.capitalize())}): {item['cantidad']} uds.")
        print("-" * 20)
    else:
        print("\n🛒 Tu carrito está vacío.")

def manejar_opcion_post_agregado(carrito, sesion, precios, historial, ventas, stock_real):
    while True:
        op = input("¿Desea (a)gregar otro producto, (f)inalizar compra, o (c)ancelar toda la compra? (a/f/c): ").strip().lower()
        if op == 'a':
            return True
        elif op == 'f':
            if confirmar_y_procesar_venta(carrito, sesion["email"], stock_real, precios, historial, ventas):
                carrito.clear()
            print("\n↩️ Volviendo al menú del cliente...")
            return False
        elif op == 'c':
            print("\n↩️ Compra totalmente cancelada. Volviendo al menú del cliente...")
            return False
        else:
            print("⚠️ Opción inválida.")
            return None

def mostrar_historial_compras(compras, email):
    """Imprime todas las compras del cliente."""
    print(f"\n--- Historial de Compras para {usuarios[email]['nombre']} ---")
    for i, venta in enumerate(compras, start=1):
        mostrar_venta_individual(venta, i)
    print("-" * 60)
    print("\n--- Fin del Historial de Compras ---")

def mostrar_venta_individual(venta, numero):
    """Muestra una sola venta en formato detallado."""
    print("-" * 60)
    print(f"| Compra #{numero}|")
    print("Items Comprados:")
    if 'items' in venta and venta['items']:
        print(f"  {'Producto (Categoría)':<30} | {'Cant.':<5} | {'P.Unit':<10} | {'Subtotal':<10}")
        print("  " + "-" * 60)
        for item in venta['items']:
            mostrar_item_historial(item)
    else:
        print("  (No hay detalle de items)")
    print(f"Costo Total Venta: ${venta.get('costo_total', 0.0):.2f}")

# GESTIÓN DE CUENTA DEL CLIENTE
def cuenta_cliente(email):
    '''
    Menú de gestión de cuenta del cliente con opciones para administrar su cuenta
    '''
    usuario = usuarios.get(email)
    if not usuario:
        print("❌ Usuario no encontrado")
        return

    while True:
        print(f"\n--- GESTIÓN DE CUENTA ({usuario['nombre']}) ---")
        print("1. Cambiar contraseña")
        print("2. Actualizar nombre")
        print("3. Volver al menú principal")
        
        opcion = input("Seleccione una opción: ").strip()
        
        if opcion == "1":
            cambiar_contrasena(email)
        elif opcion == "2":
            actualizar_nombre(email)
        elif opcion == "3":
            print("↩️ Volviendo al menú principal...")
            return
        else:
            print("⚠️ Opción inválida. Intente nuevamente.")

def menu_cliente(stock, precios, sesion_activa, historial_ventas, ventas_realizadas, email):

    ejecutando_cliente = True
    while ejecutando_cliente:
        print("\n━━━━━ MENÚ CLIENTE ━━━━━")
        print(f"Bienvenido/a {usuarios.get(sesion_activa['email'], {}).get('nombre', 'Cliente')}")
        print("1) Ver productos")
        print("2) Realizar compra")
        print("3) Ver mis compras (historial)")
        print("4) Administrar cuenta")
        print("5) Cerrar sesión")

        opcion = input("\n→ Ingresá el número de la opción: ").strip()

        if opcion == "1":
            mostrar_stock_detallado(stock, precios)
        elif opcion == "2":
            ventas_reestructurada(stock, precios, sesion_activa, historial_ventas, ventas_realizadas) 
        elif opcion == "3":
            ver_historial_compras_cliente()
        elif opcion == "4":
            cuenta_cliente(email)
        elif opcion == "5":
            cerrar_sesion()
            ejecutando_cliente = False
        else:
            print("⚠️ Opción inválida. Intentá nuevamente.")

def ver_historial_compras_cliente():
    """Muestra el historial de compras para el cliente actualmente logueado."""
    if not sesion_activa["email"]:
        print("⚠️ Debes iniciar sesión para ver tu historial de compras.")
        return

    email_cliente_actual = sesion_activa["email"]
    compras_cliente = obtener_compras_cliente(email_cliente_actual)

    if not compras_cliente:
        print("\nℹ️ Aún no has realizado ninguna compra.")
        return

    mostrar_historial_compras(compras_cliente, email_cliente_actual)

def obtener_compras_cliente(email):
    """Devuelve la lista de compras realizadas por el cliente."""
    return [venta for venta in historial_ventas if venta.get("cliente_email") == email]

def mostrar_item_historial(item):
    """Muestra un ítem dentro de una venta."""
    prod_cat = f"{item.get('producto', '?').capitalize()} ({item.get('categoria', '?').capitalize()})"
    cant = item.get('cantidad', 0)
    p_unit = item.get('precio_unitario', 0.0)
    subt = item.get('subtotal', 0.0)
    print(f"  - {prod_cat:<29} | {cant:<5} | ${p_unit:<9.2f} | ${subt:<9.2f}")

def menu_administrador(stock, precios, usuarios, historial_ventas):
    ejecutando_admin = True
    while ejecutando_admin:
        print("\n━━━━━ MENÚ ADMINISTRADOR ━━━━━")
        print(f"Sesión: {usuarios.get(sesion_activa['email'], {}).get('nombre', 'Admin')}")

        print("\n---- GESTIÓN DE USUARIOS ----")
        print("1) Ver clientes")
        print("2) Ver administradores")
        print("3) Gestionar clientes")
        print("4) Gestionar administradores")
        print("5) Crear nuevo administrador")
        print("6) Ver clientes eliminados")
        print("7) Ver administradores eliminados")

        print("\n---- GESTIÓN DE PRODUCTOS ----")
        print("8) Gestionar Inventario (Stock y Precios)")

        print("\n---- REPORTES ----")
        print("9) Ver historial de todas las ventas")
        print("10) Consultar porcentaje de cumplimiento de objetivo")

        print("\n---- SESIÓN ----")
        print("11) Cerrar sesión")

        opcion = input("\n→ Ingresá el número de la opción: ").strip()

        if opcion == "1":
            ver_usuarios_por_rol("cliente")
        elif opcion == "2":
            ver_usuarios_por_rol("administrador")
        elif opcion == "3":
            gestionar_clientes(usuarios, guardar_datos, RUTA_USUARIOS)
        elif opcion == "4":
            gestionar_administradores()
        elif opcion == "5":
            crear_nuevo_administrador()
        elif opcion == "6":
            ver_clientes_inactivos("cliente", usuarios)
        elif opcion == "7":
            ver_administradores_inactivos("administrador", usuarios)
        elif opcion == "8":
            administrar_inventario_menu(stock, precios)
        elif opcion == "9":
            ver_historial_ventas_admin(historial_ventas)
        elif opcion == "10":
            porcentaje_objetivo_ganancias(ventas_realizadas)
        elif opcion == "11":
            cerrar_sesion()
            ejecutando_admin = False
        else:
            print("⚠️ Opción inválida. Intentá nuevamente.")

def ver_usuarios_por_rol(rol):
    print(f"\n--- Lista de Usuarios con Rol: {rol.capitalize()} ---")
    try:
        encontrados = False
        for email, data in usuarios.items():
            if data.get("rol") == rol and data.get("activo", True):
                print(f"- Email: {email}, Nombre: {data.get('nombre', 'N/A')}")
                encontrados = True

        if not encontrados:
            print("ℹ️ No se encontraron usuarios con ese rol.")
            logger.info(f"No se encontraron usuarios con el rol: {rol}")
        else:
            logger.info(f"Se consultaron usuarios con rol: {rol}")

    except Exception as e:
        logger.error(f"Error al consultar usuarios por rol: {rol}: {e}")
        print("❌ Ocurrió un error al consultar los usuarios.")

def ver_historial_ventas_admin(historial_a_mostrar):
    print("\n--- Historial Completo de Ventas (Admin) ---")

    if not historial_a_mostrar:
        print("⚠️ Aún no se han registrado ventas.")
        return

    ventas_por_pagina = 3
    total_ventas = len(historial_a_mostrar)
    pagina_actual = 1
    salir = False

    while not salir:
        inicio, _ = calcular_indices_paginacion(pagina_actual, ventas_por_pagina)
        if inicio >= total_ventas:
            if pagina_actual > 1:
                pagina_actual -= 1
            else:
                salir = True
                continue

        mostrar_pagina(historial_a_mostrar, pagina_actual, ventas_por_pagina)
        accion = obtener_opcion_navegacion()

        if accion == 'q':
            salir = True
        else:
            pagina_actual = actualizar_pagina_actual(accion, pagina_actual, total_ventas, ventas_por_pagina)

    print("\n--- Fin del Historial de Ventas (Admin) ---")

#  ADMINISTRACIÓN PROPIA PARA EL CLIENTE
def cambiar_contrasena(email):
    """Cambia la contraseña del usuario con validación"""
    print("\n--- CAMBIAR CONTRASEÑA ---")
    contraseña_valida = False
    
    try:
        while not contraseña_valida:
            nueva_contraseña = input("Nueva contraseña (mín. 6 caracteres, 1 mayúscula, 1 caracter especial): ").strip()
            if not nueva_contraseña:
                print("↩️ Operación cancelada")
                logger.info(f"Cambio de contraseña cancelado para {email}")
                return

            if len(nueva_contraseña) < 6 or not any(c.isupper() for c in nueva_contraseña):
                print("❌ La contraseña debe tener al menos 6 caracteres, una mayúscula y un caracter especial.")
                logger.debug(f"Intento de contraseña inválida para {email}")
                continue

            confirmacion = input("Confirmar nueva contraseña: ").strip()
            if nueva_contraseña != confirmacion:
                print("❌ Las contraseñas no coinciden")
                logger.debug(f"Confirmación de contraseña fallida para {email}")
            else:
                contraseña_valida = True

        usuarios[email]["contraseña"] = nueva_contraseña
        guardar_datos(RUTA_USUARIOS, usuarios)
        print("✅ Contraseña actualizada exitosamente")
        logger.info(f"Contraseña actualizada correctamente para {email}")

    except Exception as e:
        logger.error(f"Error inesperado al cambiar contraseña para {email}: {e}")
        print("❌ Ocurrió un error al actualizar la contraseña.")

def actualizar_nombre(email):
    """Actualiza el nombre del usuario"""
    print("\n--- ACTUALIZAR NOMBRE ---")

    try:
        while True:
            nuevo_nombre = input("Nuevo nombre completo: ").strip()
            if not nuevo_nombre:
                print("↩️ Operación cancelada")
                logger.info(f"Actualización de nombre cancelada para {email}")
                return
                
            usuarios[email]["nombre"] = nuevo_nombre
            guardar_datos(RUTA_USUARIOS, usuarios)
            print(f"✅ Nombre actualizado a: {nuevo_nombre}")
            logger.info(f"Nombre actualizado para {email}: {nuevo_nombre}")
            return
    except Exception as e:
        logger.error(f"Error al actualizar nombre para {email}: {e}")
        print("❌ Ocurrió un error al actualizar el nombre.")

# CREAR ADMINISTRADOR
def solicitar_email_valido():
    while True:
        email = input("Ingresá el email del nuevo administrador: ").strip().lower()

        if "@" not in email or "." not in email:
            print("⚠️ El formato del email es inválido (falta @ o .)")
        elif not es_email_valido(email): 
            print("⚠️ Ese email ya está registrado.")
        else:
            return email

def solicitar_nombre_valido():
    while True:
        nombre = input("Ingresá el nombre completo del nuevo administrador: ").strip()
        if nombre:
            return nombre
        print("⚠️ El nombre no puede estar vacío.")

def solicitar_contraseña_valida():
    while True:
        contraseña = input("Ingresá una contraseña para el nuevo administrador: ").strip()
        if es_contraseña_valida(contraseña):
            return contraseña
        print("⚠️ La contraseña debe tener al menos 6 caracteres, una mayúscula y un caracter especial.")

def crear_nuevo_administrador():
    print("\n--- Crear Nuevo Administrador ---")

    try:
        email = solicitar_email_valido()
        nombre = solicitar_nombre_valido()
        contraseña = solicitar_contraseña_valida()

        if email in usuarios:
            logger.warning(f"Intento de crear un administrador con email ya existente: {email}")

        usuarios[email] = {
            "nombre": nombre,
            "contraseña": contraseña,
            "rol": "administrador",
            "activo": True
        }

        guardar_datos(RUTA_USUARIOS, usuarios)
        print(f"✅ Administrador '{nombre}' creado exitosamente.")
        logger.info(f"Administrador creado: {email} ({nombre})")

    except Exception as e:
        logger.error(f"Error al guardar nuevo administrador {email}: {e}")
        print("❌ Ocurrió un error al crear el nuevo administrador.")

def administrar_inventario_menu(stock, precios):
    """Submenú para la gestión de stock y precios."""

    while True:
        print("\n--- GESTIONAR INVENTARIO (STOCK Y PRECIOS) ---")
        print("1) Ver inventario detallado")
        print("2) Agregar nueva categoría")
        print("3) Agregar nuevo producto a categoría existente")
        print("4) Modificar stock de un producto existente")
        print("5) Modificar precio de un producto existente")
        print("6) Eliminar producto")
        print("7) Eliminar categoría (¡cuidado, elimina todos sus productos!)")
        print("8) Volver al menú de administrador")

        opcion_inv = input("\n→ Ingresá tu opción: ").strip()

        if opcion_inv == "1":
            mostrar_stock_detallado(stock, precios)
        elif opcion_inv == "2":
            agregar_categoria_inventario(stock, precios)
        elif opcion_inv == "3":
            agregar_producto_inventario(stock, precios)
        elif opcion_inv == "4":
            modificar_stock_producto(stock)
        elif opcion_inv == "5":
            modificar_precio_producto(precios)
        elif opcion_inv == "6":
            eliminar_producto_inventario(stock, precios)
        elif opcion_inv == "7":
            eliminar_categoria_inventario(stock, precios)
        elif opcion_inv == "8":
            break
        else:
            print("⚠️ Opción inválida.")

# GESTIONAR CLIENTES
def gestionar_clientes(usuarios, guardar_datos, ruta):
    print("\n─── Gestionar Clientes ───")
    print()
    ver_usuarios_por_rol("cliente")
    while True:
        nombre_a_buscar = input("Ingresá el nombre o parte del nombre del cliente (Enter para volver al menú): ").strip().lower()
        if not nombre_a_buscar:
            print("↩️ Volviendo al menú.")
            return

        encontrados = buscar_clientes_por_nombre(nombre_a_buscar, usuarios)

        if encontrados:
            email, nombre = seleccionar_cliente(encontrados)
            if not email:
                return

            mostrar_datos_cliente(email, nombre)
            print("\n¿Qué deseás hacer?")
            print("1) Eliminar cliente")
            print("2) Volver al menú")
            opcion = input("\n→ Ingresá el número de la opción: ").strip()
            if opcion == "1":
                eliminar_usuario_logicamente(email, nombre, usuarios, guardar_datos, RUTA_USUARIOS)
            elif opcion == "2":
                print("↩️ Volviendo al menú.")
            else:
                print("⚠️ Opción inválida. Volviendo al menú.")
            return  # Sale después de operar sobre un cliente
        else:
            print("⚠️ No se encontró ningún cliente con ese nombre. Intentá nuevamente.")

def buscar_clientes_por_nombre(nombre_buscado, usuarios):
    nombre_buscado = nombre_buscado.strip().lower()
    return [(email, datos["nombre"]) for email, datos in usuarios.items()
            if datos.get("rol") == "cliente" and nombre_buscado in datos.get("nombre", "").lower()]

def seleccionar_cliente(encontrados):
    if len(encontrados) == 1:
        return encontrados[0]

    print("\n✅ Clientes encontrados:")
    for i, (email, nombre) in enumerate(encontrados, start=1):
        print(f"{i}) Nombre: {nombre} | Email: {email}")

    while True:
        try:
            seleccion_str = input("\n→ Ingresá el número del cliente que querés gestionar (0 para cancelar): ")
            if not seleccion_str.strip():
                print("↩️ Selección cancelada. Volviendo al menú.")
                return None, None
            seleccion = int(seleccion_str)
            if seleccion == 0:
                print("↩️ Volviendo al menú.")
                return None, None
            if 1 <= seleccion <= len(encontrados):
                return encontrados[seleccion - 1]
            else:
                print("⚠️ Número inválido. Intentá nuevamente.")
        except ValueError:
            print("⚠️ Ingresaste algo que no es un número. Intentá nuevamente.")

def mostrar_datos_cliente(email, nombre):
    print(f"\n📄 Datos del cliente:")
    print(f"- Nombre: {nombre}")
    print(f"- Email: {email}")
    print(f"- Rol: Cliente")

# GESTIONAR ADMINISTRADORES
def gestionar_administradores():
    print("\n─── Gestionar Administradores ───")
    ver_usuarios_por_rol("administrador")
    print()
    nombre = input("Ingresá el nombre o parte del nombre del administrador: ").strip().lower()
    if not nombre:
        print("ℹ️ Búsqueda cancelada. No se ingresó un nombre.")
        return

    encontrados = buscar_administradores(nombre, usuarios)
    if not encontrados:
        print("⚠️ No se encontró ningún administrador con ese nombre.")
        return

    email, nombre = seleccionar_administrador(encontrados)
    if not email:
        return

    print(f"\n📄 Datos del administrador seleccionado:")
    print(f"- Nombre: {usuarios[email].get('nombre')}")
    print(f"- Email: {email}")

    print("\n¿Qué deseás hacer?")
    print("1) Eliminar administrador")
    print("2) Actualizar datos del administrador")
    print("3) Volver al menú")

    opcion = input("\n→ Ingresá el número de la opción: ").strip()

    if opcion == "1":
        eliminar_usuario_logicamente(email, nombre, usuarios, guardar_datos, RUTA_USUARIOS)
    elif opcion == "2":
        actualizar_administrador(email, usuarios)
    elif opcion == "3":
        print("↩️ Volviendo al menú.")
    else:
        print("⚠️ Opción inválida. Volviendo al menú.")

def buscar_administradores(nombre_a_buscar, usuarios):
    nombre_a_buscar = nombre_a_buscar.strip().lower()
    if nombre_a_buscar == "":
        return []
    return [
        (email, datos["nombre"])
        for email, datos in usuarios.items()
        if datos.get("rol") == "administrador" and nombre_a_buscar in datos.get("nombre", "").lower()
    ]

def seleccionar_administrador(encontrados, input_fn=input):
    if len(encontrados) == 1:
        return encontrados[0]
    print("\n✅ Administradores encontrados:")
    for i, (email, nombre) in enumerate(encontrados, start=1):
        print(f"{i}) Nombre: {nombre} | Email: {email}")

    while True:
        try:
            seleccion_str = pedir_input_con_cancelar(
                "\n→ Ingresá el número del administrador que querés gestionar (0 o Enter para cancelar): "
            )
            if seleccion_str is None or not seleccion_str.strip() or int(seleccion_str) == 0:
                return None, None
            seleccion = int(seleccion_str)
            if 1 <= seleccion <= len(encontrados):
                return encontrados[seleccion - 1]
            print("⚠️ Número inválido. Intentá nuevamente.")
        except ValueError:
            print("⚠️ Ingresaste algo que no es un número. Intentá nuevamente.")

def actualizar_administrador(email, usuarios):
    print(f"\n--- Actualizar datos para: {usuarios[email].get('nombre')} ({email}) ---")

    try:
        nuevo_nombre_input = pedir_input_con_cancelar(
            f"Nuevo nombre (actual: '{usuarios[email].get('nombre')}', Enter para no cambiar): "
        )
        if nuevo_nombre_input is not None and nuevo_nombre_input.strip():
            usuarios[email]["nombre"] = nuevo_nombre_input.strip()
            print("🏷️ Nombre actualizado.")
            logger.info(f"Nombre de administrador actualizado para {email}: {nuevo_nombre_input.strip()}")
        elif nuevo_nombre_input == "":
            print("ℹ️ Nombre no modificado.")
            logger.info(f"Nombre no modificado para {email} (se presionó Enter).")

        nueva_contraseña_input = pedir_input_con_cancelar("Nueva contraseña (Enter para no cambiar): ")
        if nueva_contraseña_input:
            if len(nueva_contraseña_input) < 6 or not any(c.isupper() for c in nueva_contraseña_input):
                print("⚠️ La contraseña debe tener al menos 6 caracteres, una mayúscula y caracter especial. No se actualizó la contraseña.")
                logger.debug(f"Contraseña inválida ingresada para {email}")
            else:
                confirmar = pedir_input_con_cancelar("Confirmá la nueva contraseña: ")
                if confirmar and confirmar == nueva_contraseña_input:
                    usuarios[email]["contraseña"] = nueva_contraseña_input
                    print("🔑 Contraseña actualizada.")
                    logger.info(f"Contraseña actualizada para administrador {email}")
                elif confirmar is None:
                    print("ℹ️ Actualización cancelada (confirmación).")
                    logger.info(f"Confirmación de contraseña cancelada para {email}")
                else:
                    print("⚠️ Las contraseñas no coinciden. No se actualizó la contraseña.")
                    logger.debug(f"Confirmación de contraseña incorrecta para {email}")
        elif nueva_contraseña_input == "":
            print("ℹ️ Contraseña no modificada.")
            logger.info(f"Contraseña no modificada para {email} (se presionó Enter).")

        guardar_datos(RUTA_USUARIOS, usuarios)
        print(f"✅ Datos del administrador '{email}' actualizados (si se realizaron cambios).")

    except Exception as e:
        print("❌ Ocurrió un error al actualizar los datos del administrador.")
        logger.error(f"Error al actualizar datos del administrador {email}: {e}")

def eliminar_usuario_logicamente(email, nombre, usuarios, guardar_datos, ruta):
    if email not in usuarios:
        print(f"❌ El usuario con email '{email}' no existe.")
        logger.warning(f"Intento de eliminación fallido: usuario '{email}' no existe.")
        return

    if not usuarios[email].get("activo", True):
        print(f"ℹ️ El usuario '{nombre}' ya está inactivo.")
        logger.info(f"Usuario '{email}' ya estaba inactivo al intentar eliminarlo.")
        return

    confirmacion = input(f"⚠️ ¿Estás seguro que querés eliminar a '{nombre}' con email '{email}'? (s/n): ").strip().lower()
    if confirmacion == "s":
        usuarios[email]["activo"] = False
        guardar_datos(ruta, usuarios)
        print(f"✅ Usuario '{nombre}' desactivado exitosamente.")
        logger.info(f"Usuario '{email}' desactivado lógicamente.")
    else:
        print("❌ Eliminación cancelada.")
        logger.info(f"Eliminación cancelada para el usuario '{email}'.")

# FUNCIONES PARA LOS ELIMINADOS

def ver_usuarios_inactivos_por_rol(rol, usuarios):
    print(f"\n🗑️ Usuarios inactivos con rol '{rol}':")
    encontrados = False
    for email, data in usuarios.items():
        if data.get("rol") == rol and not data.get("activo", True):
            print(f"- Email: {email}, Nombre: {data.get('nombre', 'N/A')}")
            encontrados = True
    if not encontrados:
        print(f"ℹ️ No se encontraron usuarios inactivos con rol '{rol}'.")

def ver_clientes_inactivos(rol, usuarios):
    ver_usuarios_inactivos_por_rol(rol, usuarios)

def ver_administradores_inactivos(rol, usuarios):
    ver_usuarios_inactivos_por_rol(rol, usuarios)

# AGREGAR NUEVA CATEGORIA Y AGREGAR NUEVO PRODUCTO A CATEGORIA EXISTENTE
def agregar_categoria_inventario(stock, precios):
    nombre_cat = input("Nombre de la nueva categoría: ").strip().lower()

    if not nombre_cat:
        print("⚠️ El nombre no puede estar vacío.")
        logger.debug("Intento fallido de agregar categoría: nombre vacío.")
        return

    if nombre_cat.lower() in (k.lower() for k in stock.keys()):
        print(f"⚠️ La categoría '{nombre_cat}' (o una similar) ya existe.")
        logger.info(f"Intento de duplicar categoría: '{nombre_cat}' ya existe.")
        return

    stock[nombre_cat] = {}
    precios[nombre_cat] = {}

    try:
        guardar_datos(RUTA_STOCK, stock)
        guardar_datos(RUTA_PRECIOS, precios)
        print(f"✅ Categoría '{nombre_cat}' agregada.")
        logger.info(f"Categoría '{nombre_cat}' agregada exitosamente.")
    except Exception as e:
        print("❌ Error al guardar la nueva categoría.")
        logger.error(f"Error al guardar categoría '{nombre_cat}': {e}")

def agregar_producto_inventario(stock, precios):
    if not stock:
        print("ℹ️ No hay categorías. Agregá una primero.")
        logger.debug("Intento de agregar producto fallido: no hay categorías disponibles.")
        return

    cat_elegida_key = obtener_categoria_existente(stock, tipo="stock", mensaje_personalizado="Categoría del producto al que quieres agregar: ")
    if not cat_elegida_key:
        logger.debug("Selección de categoría cancelada por el usuario.")
        return

    nombre_prod = obtener_nombre_producto(stock[cat_elegida_key], cat_elegida_key)
    if not nombre_prod:
        logger.debug(f"Entrada de nombre de producto cancelada para categoría '{cat_elegida_key}'.")
        return

    cantidad_inicial, precio_inicial = obtener_stock_y_precio(nombre_prod)
    if cantidad_inicial is None or precio_inicial is None:
        logger.debug(f"Cancelación en carga de stock o precio para '{nombre_prod}' en '{cat_elegida_key}'.")
        return

    try:
        stock[cat_elegida_key][nombre_prod.lower()] = cantidad_inicial
        precios[cat_elegida_key][nombre_prod.lower()] = precio_inicial

        guardar_datos(RUTA_STOCK, stock)
        guardar_datos(RUTA_PRECIOS, precios)

        print(f"✅ Producto '{nombre_prod}' agregado a '{cat_elegida_key}'.")
        logger.info(f"Producto agregado: '{nombre_prod}' a categoría '{cat_elegida_key}' - Cantidad: {cantidad_inicial}, Precio: {precio_inicial}")
    except Exception as e:
        print("❌ Error al guardar el nuevo producto.")
        logger.error(f"Error al agregar producto '{nombre_prod}' en '{cat_elegida_key}': {e}")

def obtener_nombre_producto(stock_categoria, cat_elegida_key):
    nombre_prod = input(f"Nombre del nuevo producto para '{cat_elegida_key}': ").strip()
    if not nombre_prod:
        print("⚠️ El nombre no puede estar vacío.")
        return None
    if nombre_prod.lower() in (p.lower() for p in stock_categoria.keys()):
        print(f"⚠️ El producto '{nombre_prod}' (o similar) ya existe en '{cat_elegida_key}'.")
        return None
    return nombre_prod

def obtener_stock_y_precio(nombre_prod):
    try:
        cantidad_inicial = int(input(f"Stock inicial para '{nombre_prod}': "))
        precio_inicial_str = input(f"Precio inicial para '{nombre_prod}' (ej: 10.99): ").replace(',', '.')
        precio_inicial = float(precio_inicial_str)
        if cantidad_inicial < 0 or precio_inicial < 0:
            print("⚠️ El stock y el precio no pueden ser negativos.")
            return None, None
        return cantidad_inicial, precio_inicial
    except ValueError:
        print("⚠️ Cantidad o precio inválido.")
        return None, None

# FUNCIONES PARA ELIMINAR PRODUCTOS Y CATEGORÍAS
def obtener_categoria_existente(diccionario, tipo="stock", mensaje_personalizado=None):
    if not diccionario:
        print(f"No hay categorías en el {tipo}.")
        return None

    print("Categorías existentes:", ", ".join(diccionario.keys()))

    if mensaje_personalizado:
        prompt = mensaje_personalizado
    else:
        prompt = f"Categoría a modificar ({tipo}): "

    cat_input_usuario = input(prompt).strip().lower()
    if not cat_input_usuario:
        print(f"⚠ El nombre de la categoría no puede estar vacío.")
        return None

    for key_original in diccionario.keys():
        if key_original.lower() == cat_input_usuario:
            return key_original

    print(f"⚠ Categoría '{cat_input_usuario}' no encontrada.")
    return None

def obtener_producto_existente(diccionario, categoria, tipo="stock"):
    if not diccionario[categoria]:
        print(f"ℹ️ La categoría '{categoria}' está vacía.")
        return None

    print(f"Productos en la categoría '{categoria}': {', '.join(diccionario[categoria].keys())}")
    prod_input = input(f"Producto a modificar {tipo}: ").strip().lower()
    if not prod_input:
        print(f"⚠️ El nombre del producto no puede estar vacío.")
        return None

    if prod_input not in diccionario[categoria]:
        print(f"Producto '{prod_input}' no existe en la categoría '{categoria}'.")
        return None

    return prod_input

#MODIFICAR STOCK DE PRODUCTO
def obtener_nuevo_stock(stock_actual):
    try:
        nuevo_stock_str = input(f"Nuevo stock para {stock_actual[0]} (actual: {stock_actual[1]}): ")
        if not nuevo_stock_str.strip():
            print("⚠️ La entrada para el nuevo stock no puede estar vacía. Operación cancelada.")
            return None

        nuevo_stock = int(nuevo_stock_str)
        if nuevo_stock < 0:
            print("Stock no puede ser negativo.")
            return None

        return nuevo_stock
    except ValueError:
        print("Cantidad inválida. Por favor, ingrese un número entero.")
        return None

def modificar_stock_producto(stock):
    mostrar_tabla_stock(stock)
    if not stock:
        print("No hay stock.")
        return

    print("\n--- Modificar Stock de Producto ---")
    categoria = obtener_categoria_existente(stock, tipo="stock", mensaje_personalizado="Categoría del producto cuyo stock querés modificar: ")
    if not categoria:
        return

    producto = obtener_producto_existente(stock, categoria)
    if not producto:
        return

    nuevo_stock = obtener_nuevo_stock((producto, stock[categoria][producto]))
    if nuevo_stock is None:
        return

    stock[categoria][producto] = nuevo_stock
    guardar_datos(RUTA_STOCK, stock)
    print("✅ Stock actualizado.")

def mostrar_tabla_stock(stock_actual):
    """
    Muestra el inventario agrupado por categoría, sin la columna de precios.
    Pensada para usarse antes de editar el stock.
    """

    print("\n📋 Inventario (solo Stock):")
    print("-" * 70)

    if not stock_actual:
        print("El inventario está vacío.")
        print("-" * 70)
        return

    categorias_validas = dict(filter(
        lambda item: len(item[1]) > 0,
        stock_actual.items()
    ))

    if not categorias_validas:
        print("No hay categorías con productos.")
        print("-" * 70)
        return

    for categoria, productos in sorted(categorias_validas.items()):
        print(f"📁 Categoría: {categoria.capitalize()}")
        print(f"    {'Producto':<25} | {'Stock':<12}")
        print("    " + "-" * 60)

        for producto, cantidad in sorted(productos.items()):
            stock_str = "Sin stock" if cantidad <= 0 else str(cantidad)
            print(f"    - {producto.capitalize():<24} | {stock_str:<12}")

        print("-" * 40)

    print("-" * 70)

# MODIFICAR PRECIO DE PRODUCTO
def obtener_nuevo_valor(tipo, valor_actual):
    try:
        nuevo_valor_str = input(f"Nuevo {tipo} para {valor_actual[0]} (actual: {valor_actual[1]}): ").replace(',', '.')
        if not nuevo_valor_str.strip():
            print(f"⚠️ La entrada para el nuevo {tipo} no puede estar vacía.")
            return None

        nuevo_valor = float(nuevo_valor_str) if tipo == "precio" else int(nuevo_valor_str)
        if nuevo_valor < 0:
            print(f"{tipo.capitalize()} no puede ser negativo.")
            return None

        return nuevo_valor
    except ValueError:
        print(f"{tipo.capitalize()} inválido.")
        return None

def modificar_precio_producto(precios):
    if not precios:
        print("No hay precios definidos.")
        return

    print("\n--- Modificar Precio de Producto ---")
    categoria = obtener_categoria_existente(precios, tipo="precio", mensaje_personalizado="Categoría del producto cuyo precio querés modificar: ")
    if not categoria:
        return

    producto = obtener_producto_existente(precios, categoria, tipo="precio")
    if not producto:
        return

    nuevo_precio = obtener_nuevo_valor("precio", (producto, precios[categoria][producto]))
    if nuevo_precio is None:
        return

    precios[categoria][producto] = nuevo_precio
    guardar_datos(RUTA_PRECIOS, precios)
    print("✅ Precio actualizado.")

#ELIMINAR PRODUCTO
def pedir_confirmacion_eliminacion(producto, categoria):
    """
    Pregunta al usuario si desea eliminar el producto.
    """
    try:
        confirmacion = input(f"❓ ¿Seguro que desea eliminar el producto '{producto}' de la categoría '{categoria}'? Esto también eliminará su precio. (s/n): ").strip().lower()
        return confirmacion == 's'
    except AttributeError:
        return False

def ejecutar_eliminacion_producto(stock, precios, categoria, producto):
    """
    Realiza la eliminación del producto del stock y del archivo de precios.
    """
    del stock[categoria][producto]
    print(f"✅ Producto '{producto}' eliminado del stock de la categoría '{categoria}'.")

    if categoria in precios and producto in precios[categoria]:
        del precios[categoria][producto]
        print(f"✅ Precio para '{producto}' eliminado de la categoría '{categoria}'.")
    else:
        print(f"ℹ️ No se encontró un precio para '{producto}' en la categoría '{categoria}'.")

    guardar_datos(RUTA_STOCK, stock)
    guardar_datos(RUTA_PRECIOS, precios)
    print("✅ Cambios guardados en los archivos.")

def iniciar_eliminacion_producto(stock, precios):
    """
    Controlador principal para gestionar la eliminación de un producto del inventario.
    """
    if not stock:
        print("ℹ️ El inventario está vacío. No hay productos para eliminar.")
        return

    print("\n--- Eliminar Producto del Inventario ---")

    categoria = obtener_categoria_existente(stock, mensaje_personalizado="Categoría del producto que querés eliminar: ")
    if not categoria:
        return

    producto = obtener_producto_existente(stock, categoria)
    if not producto:
        return

    if pedir_confirmacion_eliminacion(producto, categoria):
        ejecutar_eliminacion_producto(stock, precios, categoria, producto)
    else:
        print("❌ Operación cancelada.")

def eliminar_producto_inventario(stock, precios):
    iniciar_eliminacion_producto(stock, precios)

# ELIMINAR CATEGORÍA
def pedir_confirmacion_eliminacion_categoria(categoria):
    """
    Pregunta al usuario si desea eliminar la categoría completa y todos sus productos.
    """
    print(f"\n‼️ ADVERTENCIA ‼️")
    print(f"Está a punto de eliminar la categoría '{categoria}' y TODOS sus productos asociados")
    print("del stock y de la lista de precios. Esta acción no se puede deshacer.")

    try:
        confirmacion = input(f"¿Está ABSOLUTAMENTE SEGURO de que desea eliminar la categoría '{categoria}'? (s/n): ").strip().lower()
        return confirmacion == 's'
    except AttributeError:
        print("❌ Entrada inválida para la confirmación. Operación cancelada.")
        return False

def ejecutar_eliminacion_categoria(stock, precios, categoria):
    """
    Elimina la categoría y todos sus productos del stock y precios.
    """
    del stock[categoria]
    guardar_datos(RUTA_STOCK, stock)
    print(f"✅ Categoría '{categoria}' y sus productos eliminados del stock.")

    if categoria in precios:
        del precios[categoria]
        guardar_datos(RUTA_PRECIOS, precios)
        print(f"✅ Categoría '{categoria}' y sus precios eliminados de la lista de precios.")
    else:
        print(f"ℹ️ Categoría '{categoria}' no estaba presente en la lista de precios.")

    print(f"✅ Operación de eliminación para la categoría '{categoria}' completada.")

def iniciar_eliminacion_categoria(stock, precios):
    """
    Controlador principal para eliminar una categoría del inventario.
    """
    if not stock:
        print(" ℹ️ El inventario de stock está vacío. No hay categorías para eliminar.")
        return

    print("\n--- Eliminar Categoría del Inventario ---")

    categoria = obtener_categoria_existente(stock, mensaje_personalizado="Categoría que querés eliminar: ")
    if not categoria:
        return

    if pedir_confirmacion_eliminacion_categoria(categoria):
        ejecutar_eliminacion_categoria(stock, precios, categoria)
    else:
        print(f"❌ Operación de eliminación para la categoría '{categoria}' cancelada por el usuario.")

def eliminar_categoria_inventario(stock, precios):
    iniciar_eliminacion_categoria(stock, precios)

# VER HISTORIAL DE VENTAS CON PAGINADO
def imprimir_detalle_venta(i, venta):
    print("-" * 70)
    print(f"| Venta #{i} | Cliente: {venta.get('cliente_email', 'N/A')}|")
    print("Items Comprados:")
    if 'items' in venta and venta['items']:
        print(f"  {'Producto (Categoría)':<30} | {'Cant.':<5} | {'P.Unit':<10} | {'Subtotal':<10}")
        print("  " + "-" * 60)
        for item in venta['items']:
            prod_cat = f"{item.get('producto', '?').capitalize()} ({item.get('categoria', '?').capitalize()})"
            cant = item.get('cantidad', 0)
            p_unit = item.get('precio_unitario', 0.0)
            subt = item.get('subtotal', 0.0)
            print(f"  - {prod_cat:<29} | {cant:<5} | ${p_unit:<9.2f} | ${subt:<9.2f}")
    else:
        print("  (No hay detalle de items)")
    print(f"Costo Total Venta: ${venta.get('costo_total', 0.0):.2f}")

def calcular_indices_paginacion(pagina_actual, ventas_por_pagina):
    inicio = (pagina_actual - 1) * ventas_por_pagina
    fin = inicio + ventas_por_pagina
    return inicio, fin

def obtener_opcion_navegacion():
    print("\nOpciones: (s)iguiente, (a)nterior, (q)uit/salir, o número de página")
    return input("→ Ingresá tu opción: ").strip().lower()

def actualizar_pagina_actual(accion, pagina_actual, total_ventas, ventas_por_pagina):
    max_paginas = (total_ventas + ventas_por_pagina - 1) // ventas_por_pagina

    if accion == 's':
        if pagina_actual * ventas_por_pagina < total_ventas:
            return pagina_actual + 1
        else:
            print("ℹ️ Ya estás en la última página.")
    elif accion == 'a':
        if pagina_actual > 1:
            return pagina_actual - 1
        else:
            print("ℹ️ Ya estás en la primera página.")
    elif accion.isdigit():
        num_pagina = int(accion)
        if 1 <= num_pagina <= max_paginas:
            return num_pagina
        else:
            print(f"⚠️ Número de página inválido. Debe ser entre 1 y {max_paginas}.")
    elif accion != 'q':
        print("⚠️ Opción inválida.")

    return pagina_actual

def mostrar_pagina(historial, pagina_actual, ventas_por_pagina):
    total_ventas = len(historial)
    inicio, fin = calcular_indices_paginacion(pagina_actual, ventas_por_pagina)

    print(f"\n--- Mostrando Página {pagina_actual} (Ventas {inicio + 1} a {min(fin, total_ventas)}) ---")
    for i, venta in enumerate(historial[inicio:fin], start=inicio + 1):
        imprimir_detalle_venta(i, venta)

    print(f"\nMostrando ventas {inicio + 1}-{min(fin, total_ventas)} de {total_ventas}")


# CONSULTAR PORCENTAJE DE CUMPLIMIENTO DE OBJETIVO DE GANANCIAS
def porcentaje_objetivo_ganancias(ventas_realizadas):
    """Consulta el porcentaje de cumplimiento según un objetivo ingresado."""
    objetivo_str = ""
    objetivo = None
    objetivo_valido = False

    while not objetivo_valido:
        print("\n--- Porcentaje de Cumplimiento de Objetivo de Ganancias ---")
        objetivo_str = input("¿Cuál es el objetivo de ganancias que querés consultar? (0 para cancelar): ").strip()
        if objetivo_str:
            try:
                objetivo = float(objetivo_str)
                if objetivo == 0:
                    print("↩️ Operación cancelada.")
                    return
                if objetivo > 0:
                    objetivo_valido = True
                else:
                    print("⚠ El objetivo debe ser un número positivo.")
            except ValueError:
                print("⚠ Entrada inválida. Ingresá un número válido.")
        else:
            print("⚠ El campo no puede estar vacío.")

    subtotales = map(lambda venta: venta.get("subtotal", 0.0), ventas_realizadas)
    ganancia_total = sum(subtotales) if ventas_realizadas else 0.0

    porcentaje = (ganancia_total / objetivo) * 100 if objetivo > 0 else 0

    print(f"\n💰 Ganancia actual acumulada: ${ganancia_total:.2f}")
    print(f"🎯 Objetivo ingresado: ${objetivo:.2f}")
    print(f"📈 Porcentaje de cumplimiento: {porcentaje:.2f}%")

def menu_principal():
    # Carga inicial de datos ya se hizo al inicio del script
    ejecutando = True
    while ejecutando:
        print("\n━━━━━ MENÚ PRINCIPAL ━━━━━")
        if sesion_activa["email"]:
            print(f"Sesión activa: {usuarios.get(sesion_activa['email'], {}).get('nombre', sesion_activa['email'])} ({sesion_activa['rol']})")
            if sesion_activa["rol"] == "administrador":
                print("1) Ir al Menú Administrador")
            else: # Cliente
                print("1) Ir al Menú Cliente")
            print("2) Cerrar sesión")
            print("3) Salir de la aplicación")
        else:
            print("1) Registrarse")
            print("2) Iniciar sesión")
            print("3) Salir de la aplicación")

        opcion = input("\n→ Ingresá el número de la opción: ").strip()

        if sesion_activa["email"]: # Hay sesión activa
            if opcion == "1":
                if sesion_activa["rol"] == "administrador":
                    menu_administrador(stock, precios, usuarios, historial_ventas)
                else:
                    menu_cliente(stock, precios, sesion_activa, historial_ventas, ventas_realizadas)
            elif opcion == "2":
                cerrar_sesion()
            elif opcion == "3":
                print("👋 ¡Gracias por usar la aplicación! Guardando datos...")
                # Guardar todos los datos antes de salir (aunque ya se guardan incrementalmente)
                guardar_datos(RUTA_USUARIOS, usuarios)
                guardar_datos(RUTA_STOCK, stock)
                guardar_datos(RUTA_PRECIOS, precios)
                guardar_datos(RUTA_HISTORIAL_VENTAS, historial_ventas)
                guardar_datos(RUTA_VENTAS_REALIZADAS, ventas_realizadas)
                print("💾 ¡Datos guardados! ¡Hasta luego!")
                ejecutando = False
            else:
                print("⚠️ Esa no es una opción válida. Intentá de nuevo.")
        else: # No hay sesión activa
            if opcion == "1":
                crear_usuario(stock, precios, sesion_activa, historial_ventas, ventas_realizadas)
            elif opcion == "2":
                iniciar_sesion()
            elif opcion == "3":
                print("👋 ¡Gracias por usar la aplicación! ¡Hasta luego!")
                ejecutando = False
            else:
                print("⚠️ Esa no es una opción válida. Intentá de nuevo.")

# ======================
# Ejecutar el Programa
# ======================
if __name__ == "__main__":
    menu_principal()