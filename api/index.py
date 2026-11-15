"""Vercel serverless entry point for the Flask app.

The old vercel.json used the legacy "builds" format pointing at app.py,
which Vercel no longer supports for new Python projects. The current pattern
is a function under api/ that exposes the Flask app object; vercel.json
rewrites every route to it.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app  # noqa: E402  (Flask app object served by Vercel)
