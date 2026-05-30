"""
Main tool
Run this to open the tool ui in maya
"""
from adaptive_ik_fk.ui import adaptive_ik_fk_ui


def run():
    adadptive_ik_fk_ui_instance = adaptive_ik_fk_ui.AdaptiveIKFKUI.display()
