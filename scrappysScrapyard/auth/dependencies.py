from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from db.dependencies import get_session
from cache.helpers import CacheHelper
from cache.dependencies import get_cache_helper

