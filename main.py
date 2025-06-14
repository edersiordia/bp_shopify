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
    # 1. Si no hay correo válido, mostrar mensaje de bienvenida
    if not email or "_at_" not in email:
        return HTMLResponse(content="""
                        <html lang="es">
                        <head>
                        <meta charset="UTF-8" />
                        <title>Tus puntos Carnicash</title>
                        <meta name="viewport" content="width=device-width, initial-scale=1" />
                        <link href="https://fonts.googleapis.com/css2?family=Segoe+UI&display=swap" rel="stylesheet" />


                            <style>
                            :root {
                                --morado: #6d60f6;
                                --morado-hover: #574fe0;
                                --sombra-lila: rgba(109, 96, 246, 0.25);
                            }

                            * {
                                box-sizing: border-box;
                            }

                            body {
                                margin: 0;
                                font-family: 'Segoe UI', sans-serif;
                                background: #f5f5f5;
                                color: #333;
                            }

                            /* ======= HEADER ======= */
                            .header {
                                background: linear-gradient(135deg, #4a00e0, #8e2de2);
                                color: white;
                                text-align: center;
                                padding: 2rem 1rem 4rem;
                                border-bottom-left-radius: 0px;
                                border-bottom-right-radius: 0px;
                                margin-bottom: -3.5rem;
                            }



                            .header p {
                                margin: 0;
                            }

                            .header h1 {
                                margin: 0.5rem 0 0;
                                font-size: 2rem;
                            }

                            /* ======= CARD UNIFICADO ======= */


                            .wrapper {
                            max-width: 500px;
                            width: 100%;
                            margin: 0 auto 2rem;
                            display: flex;
                            padding: 0 1rem;
                            flex-direction: column;
                            gap: 0.3rem;
                            }


                            .card {
                                background: white;
                                border-radius: 20px;
                                padding: 1.5rem;
                                margin: 1.5rem auto;
                                width: 100%;
                                max-width: 500px;
                                box-shadow: 0 12px 28px var(--sombra-lila);
                            }




                            .card h3 {
                                margin: 0 0 0.8rem;
                                font-size: 1.2rem;
                                display: flex;
                                align-items: center;
                                gap: 0.5rem;
                            }

                            .card p {
                                margin: 0.5rem 0 1rem;
                                color: #666;
                                font-size: 0.95rem;
                            }

                            .item {
                                padding-bottom: 1rem;
                                border-bottom: 1px solid #eee;
                                margin-bottom: 1rem;
                            }

                            .item:last-child {
                                border-bottom: none;
                                margin-bottom: 0;
                            }

                            /* ======= BOTÓN ======= */
                            .btn {
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                gap: 0.5rem;
                                background: var(--morado);
                                color: white;
                                border: none;
                                border-radius: 12px;
                                padding: 0.8rem 1rem;
                                font-weight: 600;
                                font-size: 1rem;
                                cursor: pointer;
                                width: 100%;
                                transition: background 0.2s ease;
                            }

                            .btn:hover {
                                background: var(--morado-hover);
                            }

                            input[type="text"] {
                                width: 100%;
                                padding: 0.8rem;
                                font-size: 14px;
                                border: 1px solid #ccc;
                                border-radius: 10px;
                                margin-bottom: 1rem;
                            }

                            .puntos {
                                font-size: 2rem;
                                color: purple;
                                margin: 0.2rem 0 1rem;
                                font-weight: bold;
                            }

                            footer {
                                text-align: center;
                                font-size: 0.85rem;
                                color: #aaa;
                                padding: 2rem;
                            }

                            .icon {
                                display: inline-block;
                                width: 1em;
                                height: 1em;
                            }

                            /* ======= ANIMACIONES ======= */
                            .fade-in-up {
                                animation: fadeUp 2.5s ease-out both;
                            }

                            @keyframes fadeUp {
                                0% {
                                opacity: 0;
                                transform: translateY(20px);
                                }
                                100% {
                                opacity: 1;
                                transform: translateY(0);
                                }
                            }

                            @keyframes zoomFadeIn {
                                0% {
                                opacity: 0;
                                transform: scale(0.8) translateY(10px);
                                }
                                100% {
                                opacity: 1;
                                transform: scale(1) translateY(0);
                                }
                            }

                            .animated-header {
                                animation: zoomFadeIn 2.4s ease-out forwards;
                            }

                            .animated-fast {
                                animation-delay: 0s;
                            }

                            .animated-medium {
                                animation-delay: 0.1s;
                            }

                            .animated-slow {
                                animation-delay: 0.2s;
                            }

                            @keyframes fadeOut {
                                to {
                                opacity: 0;
                                visibility: hidden;
                                }
                            }
                            </style>



                        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>

                        </head>
                        <body>







                            <!-- Pantalla de bienvenida -->
                            <div id="splash" style="
                                position: fixed;
                                top: 0; left: 0;
                                width: 100vw;
                                height: 100vh;
                                background: white;
                                display: flex;
                                flex-direction: column;
                                justify-content: center;
                                align-items: center;
                                z-index: 9999;
                                animation: fadeOut 0.5s ease-out 1.5s forwards;
                            ">
                            <h2 style="font-size: 2rem; color: #6d60f6; margin: 0;">👋 Carnicash</h2>
                            </div>



                            <div class="header">
                            <div style="display: flex; flex-direction: column; align-items: center; gap: 0.3rem;">
                                <div class="animated-header animated-fast" style="font-size: 1rem; opacity: 0;">
                                🥩🔥 <strong></strong>
                                </div>
                                <h1 class="animated-header animated-medium" style="font-size: 1.7rem; margin: 0; opacity: 0;">
                                 <span style="font-weight: 700;">Bienvenido a Carnicash</span>
                                </h1>
                                <div class="animated-header animated-slow" style="font-size: 0.9rem; opacity: 0.8; opacity: 0;">
                                ¡Acumula, comparte y gana!
                                
                                </div>
                            </div>
                            </div>




                        <div class="wrapper">




                            <div class="card fade-in-up">
                            <h3 style="margin-top: 0; font-size: 1.3rem;">✍️ Solo para clientes</h3>

                            <p style="font-size: 0.95rem; color: #555; margin-bottom: 1.2rem;">
                                Recibe increíbles beneficios al ser cliente de Carnicash: gana puntos y obtén recompensas exclusivas.
                            </p>

                            <a href="https://cyscfn-wn.myshopify.com/account/login"
                                target="_parent"
                                class="btn"
                                style="text-decoration: none; display: block; text-align: center; line-height: normal;">
                                Únete ya
                            </a>

                            <p class="link" style="text-align: center; font-size: 0.9rem; margin-top: 0.8rem;">
                                ¿Ya tienes una cuenta?
                                <a href="https://cyscfn-wn.myshopify.com/account/login" style="color: #6d60f6; font-weight: 500;">Iniciar sesión</a>
                            </p>
                            </div>



                            <!-- Productos de Canje -->
                            <div class="card fade-in-up">
                            <h3>🎁 ¿Qué beneficios hay?</h3>
                            <p>Mira toda la lista de productos y beneficios que puedes obtener y decide cuál será tu próximo regalito!!</p>
                            <button class="btn" onclick="window.open('https://www.mercedes-benz.com.mx/es/passengercars/models.html?group=amg&subgroup=see-all&filters=', '_blank')">
                                💎 Ver productos de canje
                            </button>
                            </div>




                            <!-- Formas de ganar puntos -->
                            <div class="card fade-in-up">
                            <h3 style="margin-bottom: 0.5rem;">Formas de ganar puntos.</h3>
                            <p style="color: #666; font-size: 0.90rem; margin-bottom: 1.5rem;">
                                Cada vez que tu o tus referidos realicen una compra, ganarás puntos.
                            </p>
                            <div style="border-bottom: 1px solid #eee; margin: 1rem 0;"></div>
                            <div class="item">
                                <div style="display: flex; align-items: center;">
                                <span style="font-size: 1.5rem; margin-right: 0.8rem;">💸</span>
                                <div>
                                    <strong>Compra de productos.</strong><br>
                                    <span style="color: #666;">1 punto por cada peso MXN gastado en la tienda.</span>
                                </div>
                                </div>
                            </div>
                            <div class="item">
                                <div style="display: flex; align-items: center;">
                                <span style="font-size: 1.5rem; margin-right: 0.8rem;">⭐</span>
                                <div>
                                    <strong>Compra de tus referidos.</strong><br>
                                    <span style="color: #666;">El 10% de los puntos que ellos reciban por siempre.</span>
                                </div>
                                </div>
                            </div>
                            </div>




                            <!-- Redes sociales -->
                            <div class="card fade-in-up" style="text-align: center;">
                            <h3 style="margin-bottom: 0.5rem; font-size: 1.2rem; display: block; width: 100%;">📣 Redes Sociales</h3>
                            <p style="margin-top: 0; font-size: 0.95rem;">Síguenos y entérate de promociones exclusivas.</p>
                            <div style="display: flex; justify-content: center; gap: 0.6rem; flex-wrap: wrap; margin-top: 1rem;">
                                <button class="btn" style="flex: 1; padding: 0.6rem; font-size: 0.85rem; background-color: #25D366;" onclick="window.open('https://wa.me/521123456789')">
                                🟢 WhatsApp
                                </button>
                                <button class="btn" style="flex: 1; padding: 0.6rem; font-size: 0.85rem; background-color: #1877F2;" onclick="window.open('https://facebook.com/Carnicash')">
                                🔵 Facebook
                                </button>
                                <button class="btn" style="flex: 1; padding: 0.6rem; font-size: 0.85rem; background-color: #E1306C;" onclick="window.open('https://instagram.com/Carnicash')">
                                💗 Instagram
                                </button>
                            </div>
                            </div>


                        <footer>
                            &copy; 2025 Luis Payan. Todos los derechos reservados.
                        </footer>

                        <script>
                            function copiarEnlace() {
                            const input = document.getElementById("enlaceReferido");
                            input.select();
                            input.setSelectionRange(0, 99999);
                            document.execCommand("copy");

                            const mensaje = document.getElementById("mensajeCopiado");
                            mensaje.style.display = "block";
                            setTimeout(() => mensaje.style.display = "none", 2000);
                            }

                            function toggleHistorial() {
                            const h = document.getElementById("historial");
                            h.style.display = h.style.display === "none" ? "block" : "none";
                            }


                            window.onload = function () {
                                // Lanzar confetti
                                confetti({
                                particleCount: 150,
                                spread: 70,
                                origin: { y: 0.3 }
                                });

                                setTimeout(() => {
                                document.getElementById('splash').style.display = 'none';
                                document.body.style.overflow = 'auto';
                                }, 3000);
                            };


                        </script>

                        </body>
                        </html>

        """)




    # 2. Si el correo fue proporcionado
    contact_email = email.replace(".", "_").replace("@", "_at_")
    ruta_cliente = f"mi_shopify/puntos_clientes/{contact_email}"
    cliente = db.reference(ruta_cliente).get()

    # 3. Si no existe en Firebase, crearlo como invitado
    if not cliente:
        db.reference(ruta_cliente).set({
            "email": email.replace("_at_", "@").replace("_", "."),
            "nombre_inicial": "que tal !!",
            "puntos_totales": 0,
            "historial_pedidos": {}
        })
        cliente = db.reference(ruta_cliente).get()

    # 4. Ya existe cliente (nuevo o existente)
    initial_name = cliente.get('nombre_inicial', 'Bienvenido')
    puntos = cliente.get("puntos_totales", 0)
    historial = cliente.get("historial_pedidos", {})

    items_historial = ""
    for k, v in historial.items():
        fecha = v.get("fecha_compra", "Sin fecha")
        total = v.get("total_compra_mxn", 0)
        razon = v.get("Razon", "Sin motivo")
        puntos_ganados = v.get("puntos_ganados", 0)
        items_historial += f"""
            <div style='margin-bottom: 10px; padding: 10px; border: 1px solid #ccc; border-radius: 8px;'>
                <strong>Orden:</strong> {k}<br>
                <strong>Fecha:</strong> {fecha}<br>
                <strong>Total:</strong> ${total}<br>
                <strong>Motivo:</strong> {razon}<br>
                <strong>Puntos ganados:</strong> {puntos_ganados}
            </div>
        """

    enlace_referido = f"https://cyscfn-wn.myshopify.com/?ref={contact_email}"








    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Mis puntos - Carnicash</title>
    <style>
        html, body {{
            height: 100%;
            margin: 0;
            padding: 0;
            background-color: #f9f9f9;
            font-family: 'Segoe UI', sans-serif;
            display: flex;
            flex-direction: column;
        }}
        * {{
            box-sizing: border-box;
        }}
        .fade-in-up {{
            opacity: 0;
            transform: translateY(40px);
            animation: fadeUp 0.8s ease-out forwards;
        }}
        .fade-delay-1 {{ animation-delay: 0.3s; }}
        .fade-delay-2 {{ animation-delay: 0.6s; }}
        .fade-delay-3 {{ animation-delay: 0.9s; }}
        @keyframes fadeUp {{
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        body {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
        }}
        .header {{
            background: linear-gradient(135deg, #4a00e0, #8e2de2);
            color: white;
            padding: 2rem 1rem 3rem;
            text-align: center;
            border-bottom-left-radius: 20px;
            border-bottom-right-radius: 20px;
        }}
        .header h1 {{
            margin: 0.2rem 0;
            font-size: 2rem;
        }}
        .container {{
            max-width: 400px;
            margin: -2rem auto 1.5rem;
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        }}
        .container h2 {{
            margin-top: 0;
            font-size: 1.2rem;
        }}
        .container p {{
            color: #666;
            font-size: 0.95rem;
        }}
        .btn {{
            display: block;
            width: 100%;
            margin: 1rem 0;
            padding: 0.9rem;
            background-color: #6d60f6;
            color: white;
            border: none;
            border-radius: 10px;
            font-weight: bold;
            font-size: 1rem;
            cursor: pointer;
        }}
        .link {{
            text-align: center;
            font-size: 0.9rem;
        }}
        .link a {{
            color: #6d60f6;
            text-decoration: none;
        }}
        .item {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 0.7rem 0;
            border-top: 1px solid #eee;
            font-size: 0.9rem;
            color: #333;
        }}
        .item:first-child {{
            border-top: none;
        }}
        .referidos, .historial {{
            max-width: 400px;
            margin: 1.5rem auto 1rem;
            background: white;
            padding: 1.5rem;
            border-radius: 16px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        }}
        footer {{
            text-align: center;
            padding: 2rem 1rem;
            font-size: 0.85rem;
            color: #888;
        }}
        input {{
            width: 100%;
            padding: 10px;
            font-size: 14px;
            border-radius: 6px;
            border: 1px solid #ccc;
        }}
    </style>
</head>
<body>


    <div class="header fade-in-up">
        <p>Hola Juan Pérez</p>
        <h1>Tus puntos Carnicash</h1>
    </div>

    <div class="container fade-in-up fade-delay-1">
        <h2>Puntos acumulados</h2>
        <p style="font-size: 2rem; color: purple; margin: 0;"><strong>130 puntos</strong></p>
        <button class="btn" onclick="document.getElementById('historial').style.display =
            document.getElementById('historial').style.display === 'none' ? 'block' : 'none'">
            Ver historial de compras
        </button>
        <div id="historial" class="historial" style="display:none;">
            <div class="item">
                <strong>Orden:</strong> #12345<br>
                <strong>Fecha:</strong> 2025-06-11<br>
                <strong>Total:</strong> $250<br>
                <strong>Motivo:</strong> Compra<br>
                <strong>Puntos ganados:</strong> 25
            </div>
        </div>
    </div>

    <div class="referidos fade-in-up fade-delay-2">
        <h3>Comparte tu enlace de referido</h3>
        <p style="color: #666; font-size: 0.95rem;">Gana el 10% de los puntos que tus referidos acumulen.</p>
        <input id="enlaceReferido" value="https://cyscfn-wn.myshopify.com/?ref=juan_perez" readonly>
        <button onclick="copiarEnlace()" class="btn" style="margin-top: 10px;">Copiar enlace</button>
        <p id="mensajeCopiado" style="color: green; display: none;">¡Enlace copiado!</p>
    </div>

    <footer class="fade-in-up fade-delay-3">
        &copy; 2025 Luis Payan. Todos los derechos reservados.
    </footer>

    <script>
    function copiarEnlace() {{
        const input = document.getElementById("enlaceReferido");
        input.select();
        input.setSelectionRange(0, 99999);
        document.execCommand("copy");

        const mensaje = document.getElementById("mensajeCopiado");
        mensaje.style.display = "block";
        setTimeout(() => mensaje.style.display = "none", 2000);
    }}

    function cerrarVentana() {{
        window.location.href = "https://cyscfn-wn.myshopify.com/";
    }}
    </script>

</body>
</html>
"""
    return HTMLResponse(content=html)










#codigo para que el backend valide y realice la conexion con la aplicacion flotante de shopify.

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





#Esta fucnion sirve para extraer los datos útiles del payload

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
    print("----------------------------------------------")
    print("Webhook completo recibido:")
    pprint(payload)
    print("----------------------------------------------")

    orden = procesar_payload(payload)
    print("Información procesada de la orden:")
    pprint(orden)
    print("----------------------------------------------")

    contact_email = payload.get('customer', {}).get('email', 'sin_email').replace(".", "_").replace("@", "_at_")
    id_orden = str(payload.get("id", "sin_id"))

    ruta_crudo = f"mi_shopify/historial_payloads_crudos/{id_orden}"
    ruta_limpio = f"mi_shopify/historial_payloads_limpios/{id_orden}"
    db.reference(ruta_crudo).set(payload)
    db.reference(ruta_limpio).set(orden)

    try:
        total_pagado = float(orden.get("total_pagado", 0))
    except ValueError:
        total_pagado = 0.0

    puntos_ganados = int(total_pagado)

    ruta_cliente = f"mi_shopify/puntos_clientes/{contact_email}"
    cliente_ref = db.reference(ruta_cliente)
    cliente_actual = cliente_ref.get()
    puntos_totales = cliente_actual.get("puntos_totales", 0) + puntos_ganados if cliente_actual else puntos_ganados

    # Extraer referidor del payload
    referido_por = None
    note_attrs = payload.get("note_attributes", [])
    for item in note_attrs:
        if item.get("name") == "referido_por":
            referido_por = item.get("value")
            break

    ya_tiene_referido = cliente_actual.get("referido_por") if cliente_actual else None
    referidor_valido = None

    # Si no tiene aún un referidor y viene uno en el payload
    if not ya_tiene_referido and referido_por:
        ruta_referidor = f"mi_shopify/puntos_clientes/{referido_por}"
        ref_data = db.reference(ruta_referidor).get()

        if ref_data and ref_data.get("puntos_totales", 0) > 5:
            cliente_ref.update({
                "referido_por": referido_por
            })
            referidor_valido = referido_por
            print(f"Referidor {referido_por} asignado al cliente {contact_email}")
        else:
            print(f"Referidor {referido_por} no tiene suficientes puntos o no existe. No se asignó.")

    elif ya_tiene_referido:
        referidor_valido = ya_tiene_referido
        print(f"Cliente {contact_email} ya tenía asignado el referidor {referidor_valido}")

    # Actualizar cliente con puntos y guardar pedido
    cliente_ref.update({
        "email": payload.get('customer', {}).get('email', 'sin_email'),
        "nombre_inicial": payload.get('customer', {}).get('first_name', 'Bienvenido'),
        "puntos_totales": puntos_totales,
        f"historial_pedidos/{orden['shopify_id_order']}": {
            "puntos_ganados": puntos_ganados,
            "total_compra_mxn": total_pagado,
            "Razon": "Compra en tienda.",
            "fecha_compra": orden.get("fecha_compra")
        }
    })
    print(f"Puntos actualizados para {contact_email}: {puntos_totales} puntos")
    print("----------------------------------------------")

    # Si hay referidor válido, darle puntos proporcionales
    if referidor_valido:
        puntos_extra = int(puntos_ganados * 0.10)
        ruta_ref = f"mi_shopify/puntos_clientes/{referidor_valido}"
        ref_ref = db.reference(ruta_ref)
        ref_data = ref_ref.get()
        puntos_totales_referidor = ref_data.get("puntos_totales", 0) + puntos_extra if ref_data else puntos_extra

        ref_ref.update({
            "puntos_totales": puntos_totales_referidor,
            f"historial_pedidos/bonus_{orden['shopify_id_order']}": {
                "puntos_ganados": puntos_extra,
                "total_compra_mxn": total_pagado,
                "Razon": f"10% por referido {contact_email}",
                "fecha_compra": orden.get("fecha_compra")
            }
        })
        print(f"{referidor_valido} recibió {puntos_extra} puntos por la compra que hizo su referido {contact_email}")
        print("----------------------------------------------")

    return {"mensaje": "Webhook recibido, almacenado y puntos actualizados exitosamente"}


