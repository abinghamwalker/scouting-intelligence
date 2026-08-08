"""Loopback entrypoint composition for the local W07 application."""

from scouting.web.w07 import create_w07_app

app = create_w07_app()
