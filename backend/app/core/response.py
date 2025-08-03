from pydantic import BaseModel, ConfigDict

def to_camel_case(string: str) -> str:
    """将下划线命名转换为驼峰命名"""
    components = string.split('_')
    return components[0] + ''.join(word.capitalize() for word in components[1:])

class CamelCaseModel(BaseModel):
    """支持驼峰命名的基础模型"""
    model_config = ConfigDict(
        alias_generator=to_camel_case,
        populate_by_name=True,  # 允许使用原始字段名和别名
        from_attributes=True    # 支持从ORM对象创建
    )
