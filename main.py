
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from urllib.parse import urlencode
from pprint import pprint
import hmac
import hashlib
import requests
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
from fastapi.responses import HTMLResponse



# Inicialización
app = FastAPI()

cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://rastreador-gps2-default-rtdb.firebaseio.com'
})

# Credenciales de tu app de Shopify
SHOPIFY_CLIENT_ID = "d7ad6eca784abff38f6c1b06e19a0809"
SHOPIFY_CLIENT_SECRET = "51690bac71da36dbb5c00c854cbbdcc6"

@app.get("/")
def home():
    return {"mensaje": "FastAPI conecta correctamente"}


# Enpoint al que el modal flotante de shopify se conecata para obteter datos de firebase.

@app.get("/puntos/vista/{email}", response_class=HTMLResponse)
def vista_puntos(email: str):
    contact_email = email.replace(".", "_").replace("@", "_at_")
    ruta_cliente = f"mi_shopify/puntos_clientes/{contact_email}"

    cliente = db.reference(ruta_cliente).get()
    if not cliente:
        return "<h2>Cliente no encontrado</h2>"

    puntos = cliente.get("puntos_totales", 0)
    email_real = cliente.get("email", "Desconocido")

    html = f"""
    <html>
    <head><title>Mis puntos</title></head>
    <body style="font-family: Arial; padding: 20px;">
        <h2>Hola {email_real}</h2>
        <p>Tus puntos acumulados son:</p>
        <h1 style="color: purple;">{puntos} puntos</h1>
    </body>
    </html>
    """
    return HTMLResponse(content=html)







@app.get("/oauth/callback")
async def oauth_callback(request: Request):
    params = dict(request.query_params)
    code = params.get("code")
    hmac_provided = params.get("hmac")
    shop = params.get("shop")

    if not code or not hmac_provided or not shop:
        return JSONResponse(status_code=400, content={"detail": "Faltan parámetros en la URL"})

    params_to_check = {k: v for k, v in params.items() if k != "hmac"}
    message = urlencode(sorted(params_to_check.items()))
    hmac_calculated = hmac.new(
        SHOPIFY_CLIENT_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    if hmac_calculated != hmac_provided:
        return JSONResponse(status_code=403, content={"detail": "HMAC inválido"})

    access_token_url = f"https://{shop}/admin/oauth/access_token"
    data = {
        "client_id": SHOPIFY_CLIENT_ID,
        "client_secret": SHOPIFY_CLIENT_SECRET,
        "code": code
    }

    try:
        response = requests.post(access_token_url, json=data, verify=False)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error de conexión con Shopify:", e)
        return JSONResponse(status_code=500, content={
            "detail": "Error al conectar con Shopify",
            "error": str(e)
        })

    token_info = response.json()
    access_token = token_info.get("access_token")
    scope = token_info.get("scope")

    ruta = f"mi_shopify/tiendas/{shop.replace('.', '_')}"
    db.reference(ruta).set({
        "access_token": access_token,
        "scope": scope,
        "fecha_instalacion": datetime.now().isoformat()
    })

    return {
        "mensaje": f"Autenticación exitosa para {shop}",
        "token_guardado": True,
        "scope": scope
    }

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

    orden = procesar_payload(payload)
    print("\n Información procesada de la orden:")
    pprint(orden)

    fecha_actual = datetime.now().strftime("%Y%m%d")
    contact_email = payload.get('customer', {}).get('email', 'sin_email').replace(".", "_").replace("@", "_at_")
    id_orden = str(payload.get("id", "sin_id"))

    ruta_crudo = f"mi_shopify/historial_payloads_crudos/{id_orden}"
    db.reference(ruta_crudo).set(payload)
    print(f" Payload crudo guardado en: {ruta_crudo}")

    ruta_limpio = f"mi_shopify/historial_payloads_limpios/{id_orden}"
    db.reference(ruta_limpio).set(orden)
    print(f" Payload limpio guardado en: {ruta_limpio}")

    try:
        total_pagado = float(orden.get("total_pagado", 0))
    except ValueError:
        total_pagado = 0.0

    puntos_ganados = int(total_pagado)

    ruta_cliente = f"mi_shopify/puntos_clientes/{contact_email}"
    cliente_ref = db.reference(ruta_cliente)
    cliente_actual = cliente_ref.get()

    puntos_totales = cliente_actual.get("puntos_totales", 0) + puntos_ganados if cliente_actual else puntos_ganados

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

