# ENKO Dashboard MVP 1

## Archivos
- `app.py`: aplicación principal en Streamlit
- `requirements.txt`: dependencias
- `data/dashboard_usuarios.xlsx`: archivo de ejemplo
- `config/accesos_ejemplo.csv`: credenciales de ejemplo

## Credenciales de ejemplo
En el archivo `config/accesos_ejemplo.csv` se generó una fila por aliado detectado en la base de muestra.
Para este MVP, la clave de ejemplo para todos los aliados es:

`demo123`

## Cómo ejecutar localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Cómo sustituir con datos reales
1. Reemplaza `data/dashboard_usuarios.xlsx` por tu versión más reciente de ENKO Admin.
2. Edita `config/accesos_ejemplo.csv` con aliados y claves reales.
3. Si la hoja cambia de nombre, ajusta la variable `SHEET_NAME` dentro de `app.py`
   o define la variable de entorno `ENKO_SHEET_NAME`.

## Variables de entorno opcionales
- `ENKO_DATA_PATH`
- `ENKO_ACCESS_PATH`
- `ENKO_SHEET_NAME`
- `ENKO_LOGO_PATH`

## Notas del MVP
- Usuario activo = `Lecciones completadas >= 1`
- Los filtros aparecen arriba del dashboard
- Los faltantes demográficos se muestran como `Sin dato`
- El diseño visual usa una línea morado / naranja inspirada en la marca ENKO
