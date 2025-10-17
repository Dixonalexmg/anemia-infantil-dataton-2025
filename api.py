# api.py
"""
API REST para el sistema de predicción y recomendaciones de anemia infantil
Cumple con Recomendación Técnica 4: Interoperabilidad
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

# Importar servicios
from services.predictor import anemia_predictor
from services.menu_generator import menu_generator
from auth.security import decode_access_token
from auth.users import authenticate_user, get_user, User
from utils.validators import (
    validate_edad,
    validate_hemoglobina,
    validate_altitud,
    validate_presupuesto
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear app FastAPI
app = FastAPI(
    title="API Anemia Infantil - Datatón 2025",
    description="API REST para predicción de anemia y recomendaciones nutricionales personalizadas",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS (permitir acceso desde Streamlit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seguridad
security = HTTPBearer()

# ========================================================================
# MODELOS PYDANTIC (Validación de datos)
# ========================================================================

class LoginRequest(BaseModel):
    """Modelo para login"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)

class LoginResponse(BaseModel):
    """Respuesta de login"""
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class PrediccionRequest(BaseModel):
    """Modelo para solicitud de predicción"""
    hemoglobina: float = Field(..., ge=3.0, le=22.0, description="Hemoglobina en g/dL")
    edad_meses: int = Field(..., ge=6, le=59, description="Edad del niño en meses")
    altitud: int = Field(0, ge=0, le=6000, description="Altitud en metros sobre nivel del mar")
    tiene_suplemento: bool = Field(False, description="¿Recibe suplementación de hierro?")
    area_rural: Optional[bool] = Field(False, description="¿Vive en área rural?")
    cuartil_vulnerabilidad: Optional[int] = Field(2, ge=1, le=4, description="Cuartil de vulnerabilidad (1=menos, 4=más)")
    
    @validator('hemoglobina')
    def validar_hemoglobina(cls, v):
        valido, msg = validate_hemoglobina(v)
        if not valido:
            raise ValueError(msg)
        return v
    
    @validator('edad_meses')
    def validar_edad(cls, v):
        valido, msg = validate_edad(v)
        if not valido:
            raise ValueError(msg)
        return v

class PrediccionResponse(BaseModel):
    """Respuesta de predicción"""
    tiene_anemia: bool
    severidad: str
    nivel: int
    hemoglobina_ajustada: float
    deficit_g_dl: float
    categoria_riesgo: str
    probabilidad_anemia: float
    factores_riesgo: List[str]
    recomendaciones: List[Dict[str, str]]
    requiere_atencion_urgente: bool

class MenuRequest(BaseModel):
    """Modelo para solicitud de menú"""
    edad_meses: int = Field(..., ge=6, le=59)
    presupuesto_diario: float = Field(5.0, ge=1.0, le=100.0)
    region: str = Field("Costa", pattern="^(Costa|Sierra|Selva)$")
    preferencias: Optional[List[str]] = Field(None)
    excluir: Optional[List[str]] = Field(None)
    
    @validator('presupuesto_diario')
    def validar_presupuesto(cls, v):
        valido, msg = validate_presupuesto(v)
        if not valido:
            raise ValueError(msg)
        return v

class MenuResponse(BaseModel):
    """Respuesta de menú"""
    edad_meses: int
    requerimiento_hierro_mg: float
    hierro_aportado_mg: float
    cobertura_pct: float
    costo_total: float
    cumple_requerimiento: bool
    menu_items: List[Dict[str, Any]]
    preparaciones: List[str]
    evaluacion: str

# ========================================================================
# FUNCIONES DE AUTENTICACIÓN
# ========================================================================

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    Obtiene el usuario actual desde el token JWT
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username = payload.get("sub")
    user = get_user(username)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    
    return user

# ========================================================================
# ENDPOINTS
# ========================================================================

@app.get("/", tags=["General"])
async def root():
    """Endpoint raíz - Información de la API"""
    return {
        "nombre": "API Anemia Infantil - Datatón 2025",
        "version": "2.0.0",
        "descripcion": "Sistema de predicción de anemia y recomendaciones nutricionales",
        "documentacion": "/docs",
        "endpoints": {
            "autenticacion": "/api/v1/auth/login",
            "prediccion": "/api/v1/predict",
            "menu": "/api/v1/menu",
            "salud": "/health"
        }
    }

@app.get("/health", tags=["General"])
async def health_check():
    """Health check - Estado de la API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "servicios": {
            "predictor": "OK",
            "menu_generator": "OK",
            "autenticacion": "OK"
        }
    }

# ===== AUTENTICACIÓN =====

@app.post("/api/v1/auth/login", response_model=LoginResponse, tags=["Autenticación"])
async def login(request: LoginRequest):
    """
    Endpoint de login - Retorna token JWT
    """
    user = authenticate_user(request.username, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    from auth.security import create_access_token
    from datetime import timedelta
    
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(hours=8)
    )
    
    logger.info(f"Login exitoso: {user.username} ({user.role})")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.to_dict()
    }

# ===== PREDICCIÓN =====

@app.post("/api/v1/predict", response_model=PrediccionResponse, tags=["Predicción"])
async def predecir_anemia(
    request: PrediccionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint de predicción de anemia
    
    Requiere autenticación.
    """
    logger.info(f"Predicción solicitada por: {current_user.username}")
    
    try:
        # Convertir request a dict
        datos = request.dict()
        
        # Realizar predicción
        resultado = anemia_predictor.predecir(datos)
        
        # Formatear respuesta
        response = {
            "tiene_anemia": resultado["tiene_anemia"],
            "severidad": resultado["severidad"],
            "nivel": resultado["nivel"],
            "hemoglobina_ajustada": resultado["hemoglobina_ajustada"],
            "deficit_g_dl": resultado["deficit_g_dl"],
            "categoria_riesgo": resultado["categoria"],
            "probabilidad_anemia": resultado["probabilidad_anemia"],
            "factores_riesgo": resultado["factores_riesgo"],
            "recomendaciones": resultado["recomendaciones"],
            "requiere_atencion_urgente": resultado["requiere_atencion_urgente"]
        }
        
        logger.info(f"Predicción exitosa: Anemia={resultado['tiene_anemia']}, Severidad={resultado['severidad']}")
        return response
        
    except Exception as e:
        logger.error(f"Error en predicción: {e}")
        raise HTTPException(status_code=500, detail=f"Error en predicción: {str(e)}")

# ===== GENERACIÓN DE MENÚS =====

@app.post("/api/v1/menu", response_model=MenuResponse, tags=["Menús"])
async def generar_menu(
    request: MenuRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint de generación de menú personalizado
    
    Requiere autenticación.
    """
    logger.info(f"Menú solicitado por: {current_user.username}")
    
    try:
        # Generar menú
        menu = menu_generator.generar_menu(
            edad_meses=request.edad_meses,
            presupuesto_diario=request.presupuesto_diario,
            region=request.region,
            preferencias=request.preferencias,
            excluir=request.excluir
        )
        
        logger.info(f"Menú generado: {len(menu['menu_items'])} alimentos, {menu['cobertura_pct']:.1f}% cobertura")
        return menu
        
    except Exception as e:
        logger.error(f"Error en generación de menú: {e}")
        raise HTTPException(status_code=500, detail=f"Error en menú: {str(e)}")

# ===== ESTADÍSTICAS (Sin autenticación para demo) =====

@app.get("/api/v1/stats", tags=["Estadísticas"])
async def obtener_estadisticas():
    """
    Endpoint de estadísticas generales (público para demo)
    """
    from utils.data_loader import data_loader
    
    stats = data_loader.get_stats()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "archivos_disponibles": stats["archivos_disponibles"],
        "archivos_faltantes": stats["archivos_faltantes"],
        "total_registros": stats["total_registros"]
    }

# ========================================================================
# PUNTO DE ENTRADA
# ========================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
