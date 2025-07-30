from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class TreeNode(BaseModel):
    name: str
    category: Optional[str] = None
    type: str  # "tag" or "image"
    children: List["TreeNode"] = []
    image_data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

TreeNode.model_rebuild()