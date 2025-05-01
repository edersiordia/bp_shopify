from fastapi import FastAPI, Request
from pprint import pprint
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

# Inicializar Firebase
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://rastreador-gps2-default-rtdb.firebaseio.com'
})

app = FastAPI()

@app.get("/")
def home():
    return {"mensaje": "FastAPI conecta correctamente"}




def procesar_payload(payload):
    order_info = {
        "shopify_id_order": payload.get("id"),
        "confirmation_number": payload.get("confirmation_number"),
        "numero_orden_tienda": payload.get("name"),
        "estado_pago": payload.get("financial_status"),
        "nombre_cliente": f"{payload.get('customer', {}).get('first_name', '')} {payload.get('customer', {}).get('last_name', '')}",
        "id_cliente": payload.get('customer', {}).get('id', ''),
        "email_cliente": payload.get('customer', {}).get('email', ''),
        "total_de_venta": payload.get("total_line_items_price"),
        "total_impuestos": payload.get("total_tax"),
        "total_pagado": payload.get("total_price"),
        "fecha_compra": payload.get("created_at"),
        "productos": []
    }

    # Productos
    for item in payload.get("line_items", []):
        order_info["productos"].append({
            "nombre_producto": item.get("name"),
            "cantidad": item.get("quantity"),
            "precio_unitario": item.get("price")
        })


    return order_info



@app.post("/webhook/test1")
async def recibir_webhook(mensaje: Request):
    payload = await mensaje.json()
    print(" Webhook completo recibido:")
    pprint(payload)

    # Procesar el payload limpio
    orden = procesar_payload(payload)
    print("\n Información procesada de la orden:")
    pprint(orden)

    # Sacar la fecha actual en formato YYYYMMDD
    fecha_actual = datetime.now().strftime("%Y%m%d")
    
    # Obtener el email del cliente
    contact_email = payload.get('customer', {}).get('email', 'sin_email').replace(".", "_").replace("@", "_at_")

    # ID de la orden
    id_orden = str(payload.get("id", "sin_id"))

    # Guardar payload crudo en Firebase
    ruta_crudo = f"mi_shopify/historial_payloads_crudos/{id_orden}"
    db.reference(ruta_crudo).set(payload)
    print(f" Payload crudo guardado en: {ruta_crudo}")

    # Guardar payload limpio en Firebase
    ruta_limpio = f"mi_shopify/historial_payloads_limpios/{id_orden}"
    db.reference(ruta_limpio).set(orden)
    print(f" Payload limpio guardado en: {ruta_limpio}")

    # ========== Sección de Puntos de Cliente ==========

    # Cálculo de puntos
    try:
        total_pagado = float(orden.get("total_pagado", 0))
    except ValueError:
        total_pagado = 0.0

    puntos_ganados = int(total_pagado)

    # Ruta del cliente en Firebase
    ruta_cliente = f"mi_shopify/puntos_clientes/{contact_email}"
    cliente_ref = db.reference(ruta_cliente)
    cliente_actual = cliente_ref.get()

    # Si el cliente existe, sumamos puntos
    if cliente_actual:
        puntos_totales = cliente_actual.get("puntos_totales", 0) + puntos_ganados
    else:
        puntos_totales = puntos_ganados

    # Actualizar puntos y agregar historial de pedidos
    cliente_ref.update({
        "email": payload.get('customer', {}).get('email', 'sin_email'),
        "puntos_totales": puntos_totales,
        f"historial_pedidos/{orden['shopify_id_order']}": {
            "puntos_ganados": puntos_ganados,
            "total_compra_mxn": total_pagado,
            "fecha_compra": orden.get("fecha_compra")
        }
    })

    print(f" Puntos actualizados para {contact_email}: {puntos_totales} puntos")

    return {"mensaje": "Webhook recibido, almacenado y puntos actualizados exitosamente"}

