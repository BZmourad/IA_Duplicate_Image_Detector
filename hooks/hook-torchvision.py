"""
PyInstaller hook for torchvision - exclude problematic modules.
"""

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Don't collect all torchvision submodules as they cause issues
# Only collect what's needed
hiddenimports = [
    'torchvision.transforms',
    'torchvision.transforms.functional',
]

# Exclude problematic modules
excludedimports = [
    'torchvision.ops',
    'torchvision.models.detection',
    'torchvision._meta_registrations',
]