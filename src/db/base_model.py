# coding=gbk
from mongoengine import Document
from typing import Type, TypeVar, Dict, Any, List

T = TypeVar('T', bound='BaseModel')

# 提供基础操作数据库的方法
# CURD


class BaseModel(Document):
    meta = {'abstract': True}  # 不创建该类对应的集合

    @classmethod
    def add(cls: Type[T], data: Dict[str, Any]) -> T:
        obj = cls(**data)
        obj.save()
        return obj

    @classmethod
    def delete(cls: Type[T], object_id: str) -> int:
        return cls.objects(id=object_id).delete()

    @classmethod
    def update(cls: Type[T], object_id: str, data: Dict[str, Any]) -> int:
        return cls.objects(id=object_id).update(**{f'set__{k}': v for k, v in data.items()})

    @classmethod
    def count(cls: Type[T], filter: Dict[str, Any] = None) -> int:
        return cls.objects(**(filter or {})).count()

    @classmethod
    def list(cls: Type[T], filter: Dict[str, Any] = None) -> List[T]:
        return list(cls.objects(**(filter or {})))

    @classmethod
    def list2(cls: Type[T], page: int = 0, page_size: int = 10, filter: Dict[str, Any] = None) -> List[T]:
        qs = cls.objects(**(filter or {}))
        items = list(qs.skip((page) * page_size).limit(page_size))
        return items

    @classmethod
    def list_by(cls: Type[T], filter: Dict[str, Any]) -> List[T]:
        return list(cls.objects(**filter))

    @classmethod
    def delete_many(cls: Type[T], filter: Dict[str, Any]) -> int:
        return cls.objects(**filter).delete()

    @classmethod
    def update_by(cls: Type[T], filter: Dict[str, Any], data: Dict[str, Any]) -> int:
        return cls.objects(**filter).update(**{f'set__{k}': v for k, v in data.items()})

    @classmethod
    def page(cls: Type[T], page: int = 0, page_size: int = 10, filter: Dict[str, Any] = None) -> Dict[str, Any]:
        qs = cls.objects(**(filter or {}))
        total = qs.count()
        items = list(qs.skip((page) * page_size).limit(page_size))
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'items': items
        }
