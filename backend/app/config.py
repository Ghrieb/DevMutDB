# SPDX-FileCopyrightText: 2025 Abdelkarim Hani Ghrieb
# SPDX-License-Identifier: AGPL-3.0-only

"""Configuration and environment management."""

import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Cache Settings
CACHE_TTL_SECONDS = 86400  # 24 hours

# API Timeouts (seconds)
API_TIMEOUT = 10

# DevScore Constants
TPM_99TH_PERCENTILE = 10000
CADD_MAX = 40

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
