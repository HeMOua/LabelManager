from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.crud.annotation_file import crud_annotation_file
from app.crud.annotation_group import crud_annotation_group
from app.crud.image import crud_image
from app.schemas.annotation_file import (
    AnnotationFileCreate,
    AnnotationFileUpdate,
    AnnotationFileListResponse,
    AnnotationFileDetail
)
from app.core.exceptions import NotFoundException, ValidationException


class AnnotationFileService:
    """标注文件业务逻辑服务"""

    async def get_annotation_files(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        annotation_group_id: Optional[int] = None,
        image_id: Optional[int] = None
    ) -> AnnotationFileListResponse:
        """
        获取标注文件列表

        Args:
            db: 数据库会话
            skip: 跳过记录数
            limit: 返回记录数
            annotation_group_id: 标注组ID过滤
            image_id: 图片ID过滤

        Returns:
            标注文件列表响应
        """
        if annotation_group_id:
            files = await crud_annotation_file.get_multi_by_group(
                db,
                annotation_group_id=annotation_group_id,
                skip=skip,
                limit=limit
            )
            total = await crud_annotation_file.get_count(
                db,
                filters={"annotation_group_id": annotation_group_id}
            )
        elif image_id:
            files = await crud_annotation_file.get_multi_by_image(
                db,
                image_id=image_id,
                skip=skip,
                limit=limit
            )
            total = await crud_annotation_file.get_count(
                db,
                filters={"image_id": image_id}
            )
        else:
            files = await crud_annotation_file.get_multi(db, skip=skip, limit=limit)
            total = await crud_annotation_file.get_count(db)

        return AnnotationFileListResponse(
            total=total,
            items=files,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit
        )

    async def get_annotation_file_detail(
        self,
        db: AsyncSession,
        file_id: int
    ) -> AnnotationFileDetail:
        """
        获取标注文件详情

        Args:
            db: 数据库会话
            file_id: 标注文件ID

        Returns:
            标注文件详情

        Raises:
            NotFoundException: 标注文件不存在
        """
        file = await crud_annotation_file.get(db, id=file_id)
        if not file:
            raise NotFoundException(f"AnnotationFile with id {file_id} not found")

        # 获取关联信息
        image = await crud_image.get(db, id=file.image_id)
        group = await crud_annotation_group.get(db, id=file.annotation_group_id)

        return AnnotationFileDetail(
            **file.__dict__,
            image_filename=image.filename if image else None,
            annotation_group_name=group.name if group else None
        )

    async def create_annotation_file(
        self,
        db: AsyncSession,
        file_in: AnnotationFileCreate,
        created_by: int,
        auto_version: bool = True
    ) -> dict:
        """
        创建标注文件

        Args:
            db: 数据库会话
            file_in: 创建标注文件数据
            created_by: 创建人ID
            auto_version: 是否自动生成版本号

        Returns:
            创建的标注文件

        Raises:
            NotFoundException: 标注组或图片不存在
            ValidationException: 图片不属于标注组的项目
        """
        # 检查标注组是否存在
        group = await crud_annotation_group.get(db, id=file_in.annotation_group_id)
        if not group:
            raise NotFoundException(
                f"AnnotationGroup with id {file_in.annotation_group_id} not found"
            )

        # 检查图片是否存在
        image = await crud_image.get(db, id=file_in.image_id)
        if not image:
            raise NotFoundException(f"Image with id {file_in.image_id} not found")

        # 验证图片和标注组属于同一项目
        if image.project_id != group.project_id:
            raise ValidationException(
                "Image and AnnotationGroup must belong to the same project"
            )

        # 如果启用自动版本号，创建新版本
        if auto_version:
            file = await crud_annotation_file.create_new_version(
                db,
                obj_in=file_in,
                created_by=created_by
            )
        else:
            file = await crud_annotation_file.create(
                db,
                obj_in=file_in,
                created_by=created_by
            )

        return file

    async def update_annotation_file(
        self,
        db: AsyncSession,
        file_id: int,
        file_in: AnnotationFileUpdate,
        updated_by: int
    ) -> dict:
        """
        更新标注文件

        Args:
            db: 数据库会话
            file_id: 标注文件ID
            file_in: 更新数据
            updated_by: 更新人ID

        Returns:
            更新后的标注文件

        Raises:
            NotFoundException: 标注文件不存在
        """
        # 获取标注文件
        file = await crud_annotation_file.get(db, id=file_id)
        if not file:
            raise NotFoundException(f"AnnotationFile with id {file_id} not found")

        # 更新标注文件
        file = await crud_annotation_file.update(
            db,
            db_obj=file,
            obj_in=file_in,
            updated_by=updated_by
        )
        return file

    async def delete_annotation_file(
        self,
        db: AsyncSession,
        file_id: int
    ) -> None:
        """
        删除标注文件

        Args:
            db: 数据库会话
            file_id: 标注文件ID

        Raises:
            NotFoundException:  标注文件不存在
        """
        file = await crud_annotation_file.get(db, id=file_id)
        if not file:
            raise NotFoundException(f"AnnotationFile with id {file_id} not found")

        await crud_annotation_file.delete(db, id=file_id)

    async def get_latest_annotation(
        self,
        db: AsyncSession,
        annotation_group_id: int,
        image_id: int
    ) -> Optional[dict]:
        """
        获取特定图片在标注组中的最新标注

        Args:
            db: 数据库会话
            annotation_group_id: 标注组ID
            image_id:  图片ID

        Returns:
            最新的标注文件或 None
        """
        file = await crud_annotation_file.get_by_group_and_image(
            db,
            annotation_group_id=annotation_group_id,
            image_id=image_id
        )
        return file


# 创建服务实例
annotation_file_service = AnnotationFileService()