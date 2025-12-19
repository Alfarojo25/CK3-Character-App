"""
CK3 Character Manager - Unified Application
Main entry point for the application.
"""

import sys
import os
import subprocess
import importlib.util

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Lista de requerimientos necesarios para la aplicación
REQUIREMENTS = [
    'Pillow>=10.0.0',
]


def check_requirement(package_name, import_name=None):
    """
    Verifica si un paquete está instalado.
    
    Args:
        package_name: Nombre del paquete pip
        import_name: Nombre del módulo para importar (si es diferente al package_name)
    
    Returns:
        True si está instalado, False en caso contrario
    """
    if import_name is None:
        import_name = package_name.lower().replace('-', '_')
    
    spec = importlib.util.find_spec(import_name)
    return spec is not None


def check_all_requirements():
    """
    Verifica si todos los requerimientos están instalados.
    
    Returns:
        Tupla (todos_instalados: bool, paquetes_faltantes: list)
    """
    missing_packages = []
    
    for requirement in REQUIREMENTS:
        # Extraer nombre del paquete sin versión
        package_name = requirement.split('>=')[0].split('==')[0].split('<=')[0].split('<')[0].split('>')[0].strip()
        
        if not check_requirement(package_name):
            missing_packages.append(package_name)
    
    return len(missing_packages) == 0, missing_packages


def install_requirements():
    """
    Instala los requerimientos faltantes.
    
    Returns:
        True si la instalación fue exitosa, False en caso contrario
    """
    print("📦 Instalando dependencias faltantes...")
    try:
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install'] + REQUIREMENTS,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("✅ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al instalar dependencias: {e}")
        return False


def verify_and_install_dependencies():
    """
    Verifica e instala automáticamente las dependencias faltantes.
    """
    all_installed, missing = check_all_requirements()
    
    if all_installed:
        print("✅ Todas las dependencias están instaladas")
        return True
    
    if missing:
        print(f"⚠️ Paquetes faltantes: {', '.join(missing)}")
        return install_requirements()
    
    return False


def main():
    """Main entry point."""
    # Verificar e instalar dependencias antes de importar la aplicación
    verify_and_install_dependencies()
    
    from ui import CK3CharacterApp
    
    app = CK3CharacterApp()
    app.mainloop()


if __name__ == "__main__":
    main()
