from sqlalchemy.orm import Session
from .models import SystemConfig

def get_config(db: Session) -> SystemConfig:
    config = db.get(SystemConfig, 1)
    if config is None:
        config = SystemConfig(id=1)
        db.add(config)
        db.commit()
        db.refresh(config)
    return config
