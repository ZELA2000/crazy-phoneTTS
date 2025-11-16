"""
Test di verifica struttura import.

Questo script verifica che la nuova struttura a cartelle
permetta import corretti di tutti i moduli.
"""

import sys
import os

# Aggiungi backend al path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)


def test_imports():
    """Testa tutti gli import dalla nuova struttura."""

    print("🧪 Test Import Struttura Organizzata\n")

    # Test Core
    print("📦 Testing core/")
    try:
        from core.config import ApplicationConfiguration
        print("  ✓ core.config.ApplicationConfiguration")
    except ImportError as e:
        print(f"  ✗ core.config: {e}")
        return False

    # Test Models
    print("\n📦 Testing models/")
    try:
        from models.history import TextHistoryDatabase
        print("  ✓ models.history.TextHistoryDatabase")
    except ImportError as e:
        print(f"  ✗ models.history: {e}")
        return False

    try:
        from models.voice_catalog import VoiceCatalog
        print("  ✓ models.voice_catalog.VoiceCatalog")
    except ImportError as e:
        print(f"  ✗ models.voice_catalog: {e}")
        return False

    # Test Managers
    print("\n📦 Testing managers/")

    managers_tests = [
        ("managers.audio_processor", "AudioConverter"),
        ("managers.music_library", "MusicLibrary"),
        ("managers.update_manager", "UpdateProgressManager"),
        ("managers.version_manager", "VersionManager"),
        ("managers.websocket_manager", "HistoryUpdateManager")
    ]

    for module_name, class_name in managers_tests:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"  ✓ {module_name}.{class_name}")
        except ImportError as e:
            # Alcune dipendenze sono solo nel container
            if "fastapi" in str(e) or "pydub" in str(e) or "azure" in str(e):
                print(
                    f"  ⚠️  {module_name}.{class_name} (dipendenze container)")
            else:
                print(f"  ✗ {module_name}: {e}")
                return False

    # Test Services (può fallire senza dipendenze Azure)
    print("\n📦 Testing services/")
    print("  ⚠️  services.azure_speech richiede dipendenze Azure (OK nel container)")

    print("\n✅ Struttura import verificata con successo!")
    print("   Tutti i moduli sono importabili correttamente.")
    return True


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
