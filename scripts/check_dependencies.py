#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para revisar dependencias y vulnerabilidades
Ejecutar: python scripts/check_dependencies.py
"""

import subprocess
import sys
import os

def check_vulnerabilities():
    """Revisa vulnerabilidades en dependencias"""
    print("🔍 Revisando vulnerabilidades...")
    print("-" * 60)
    try:
        result = subprocess.run(
            ['pip-audit', '-r', 'requirements.txt'],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode != 0:
            print("\n⚠️ Se encontraron vulnerabilidades!")
            if result.stderr:
                print(result.stderr)
            return False
        if "No known vulnerabilities found" in result.stdout or "No known vulnerabilities" in result.stdout:
            print("✅ No se encontraron vulnerabilidades conocidas")
        return True
    except FileNotFoundError:
        print("❌ pip-audit no está instalado")
        print("   Instalar con: pip install pip-audit")
        return False
    except Exception as e:
        print(f"❌ Error al ejecutar pip-audit: {e}")
        return False

def check_outdated():
    """Revisa paquetes desactualizados"""
    print("\n📦 Revisando paquetes desactualizados...")
    print("-" * 60)
    try:
        result = subprocess.run(
            ['pip', 'list', '--outdated'],
            capture_output=True,
            text=True
        )
        if result.stdout.strip() and "Package" not in result.stdout:
            print(result.stdout)
            print("\n💡 Considera actualizar estos paquetes si hay nuevas versiones estables")
        else:
            print("✅ Todas las dependencias están actualizadas")
    except Exception as e:
        print(f"❌ Error: {e}")

def check_requirements_exists():
    """Verifica que requirements.txt existe"""
    if not os.path.exists('requirements.txt'):
        print("❌ No se encontró requirements.txt")
        print("   Asegúrate de ejecutar el script desde la raíz del proyecto")
        return False
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("  📦 REVISIÓN DE DEPENDENCIAS")
    print("=" * 60)
    print()
    
    # Verificar que estamos en el directorio correcto
    if not check_requirements_exists():
        sys.exit(1)
    
    vulnerabilities_ok = check_vulnerabilities()
    check_outdated()
    
    print()
    print("=" * 60)
    if vulnerabilities_ok:
        print("✅ Revisión completada")
    else:
        print("⚠️ Revisar vulnerabilidades encontradas")
        print("   Actualiza los paquetes vulnerables con:")
        print("   pip install --upgrade nombre-paquete")
    print("=" * 60)


