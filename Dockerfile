# Imagen base segura y completa con certificados SSL funcionales
FROM python:3.11-bullseye

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar tu código
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando para iniciar FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

