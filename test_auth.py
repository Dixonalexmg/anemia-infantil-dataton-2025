# test_auth.py
"""Script de prueba para validar módulo de autenticación"""
import sys
from auth.security import hash_password, verify_password, create_access_token, decode_access_token
from auth.users import authenticate_user, get_user

def test_security():
    """Prueba funciones de seguridad"""
    print("=" * 60)
    print("TEST 1: Hashing y Verificación de Contraseñas")
    print("=" * 60)
    
    password = "test123"
    hashed = hash_password(password)
    print(f"✅ Hash generado: {hashed[:30]}...")
    
    # Verificar contraseña correcta
    assert verify_password(password, hashed), "❌ Falló verificación correcta"
    print("✅ Verificación de contraseña correcta: OK")
    
    # Verificar contraseña incorrecta
    assert not verify_password("wrong_password", hashed), "❌ Falló detección de contraseña incorrecta"
    print("✅ Detección de contraseña incorrecta: OK")
    
    print("\n" + "=" * 60)
    print("TEST 2: Tokens JWT")
    print("=" * 60)
    
    # Crear token
    data = {"sub": "admin", "role": "admin"}
    token = create_access_token(data)
    print(f"✅ Token generado: {token[:50]}...")
    
    # Decodificar token
    decoded = decode_access_token(token)
    assert decoded is not None, "❌ Falló decodificación de token"
    assert decoded["sub"] == "admin", "❌ Datos incorrectos en token"
    print(f"✅ Token decodificado correctamente: {decoded['sub']}")


def test_authentication():
    """Prueba autenticación de usuarios"""
    print("\n" + "=" * 60)
    print("TEST 3: Autenticación de Usuarios")
    print("=" * 60)
    
    # Autenticación exitosa
    user = authenticate_user("admin", "admin123")
    assert user is not None, "❌ Falló autenticación de admin"
    print(f"✅ Autenticación exitosa: {user.full_name} ({user.role})")
    
    # Autenticación fallida (contraseña incorrecta)
    user = authenticate_user("admin", "wrong_password")
    assert user is None, "❌ Falló rechazo de contraseña incorrecta"
    print("✅ Rechazo de contraseña incorrecta: OK")
    
    # Usuario inexistente
    user = authenticate_user("noexiste", "password")
    assert user is None, "❌ Falló rechazo de usuario inexistente"
    print("✅ Rechazo de usuario inexistente: OK")
    
    # Obtener usuario
    user = get_user("medico_demo")
    assert user is not None, "❌ Falló obtención de usuario"
    print(f"✅ Usuario obtenido: {user.full_name}")


def main():
    """Ejecuta todas las pruebas"""
    try:
        test_security()
        test_authentication()
        
        print("\n" + "=" * 60)
        print("🎉 TODOS LOS TESTS PASARON CORRECTAMENTE")
        print("=" * 60)
        print("\nMódulo de seguridad funcionando al 100%")
        print("Puedes continuar con el siguiente paso.\n")
        
    except AssertionError as e:
        print(f"\n❌ ERROR EN TEST: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
