import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import AsyncSessionLocal, init_db
from app.models.user import User
from app.models.farm import Farm
from passlib.context import CryptContext

pwd = CryptContext(schemes=['bcrypt'])

async def create_users():
    await init_db()
    async with AsyncSessionLocal() as db:
        # Create farm first
        farm = Farm(name='مزرعة الإسماعيلية', location='الإسماعيلية', area=50.0, crop_type='طماطم')
        db.add(farm)
        await db.flush()

        # Create admin
        admin = User(
            email='admin@cropmind.com',
            hashed_password=pwd.hash('admin123'),
            full_name='Admin CropMind',
            role='manager',
            is_active=True,
            farm_id=farm.id
        )

        # Create worker
        worker = User(
            email='worker@cropmind.com',
            hashed_password=pwd.hash('worker123'),
            full_name='محمود إبراهيم',
            role='worker',
            is_active=True,
            farm_id=farm.id
        )

        db.add(admin)
        db.add(worker)
        await db.commit()
        print('✅ Farm + Users created!')
        print('Manager: admin@cropmind.com / admin123')
        print('Worker:  worker@cropmind.com / worker123')

asyncio.run(create_users())
