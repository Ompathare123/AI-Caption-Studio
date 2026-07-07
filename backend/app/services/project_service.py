import json
from sqlalchemy.orm import Session

from backend.app.core.errors import RenderingError
from backend.app.models.project import Project
from backend.app.models.video import Video
from backend.app.rendering.asset_manager import AssetManager


class ProjectService:

    @staticmethod
    def create_project(
        db: Session,
        video_id: str,
        subtitle_id: str = None,
        user_id: str = None,
        name: str = "Untitled Project",
    ) -> Project:
        """
        Verify video existence, load initial aligned captions JSON segments
        from disk if available, populate styles defaults, and create a Project.
        """
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise RenderingError(
                f"Video ID '{video_id}' not registered in database",
                status_code=404,
            )

        captions = []
        if subtitle_id:
            try:
                sub_path = AssetManager.get_subtitles_json_path(subtitle_id)
                with open(sub_path, "r", encoding="utf-8") as f:
                    captions = json.load(f)
            except Exception:
                captions = []

        default_style = {
            "font_family": "Arial",
            "font_size": 24,
            "font_weight": "normal",
            "text_color": "#FFFFFF",
            "highlight_color": "#FFFF00",
            "outline_color": "#000000",
            "outline_width": 2,
            "shadow_color": "#000000",
            "shadow_offset_x": 0,
            "shadow_offset_y": 0,
            "background_box": False,
            "background_color": "#000000",
            "background_opacity": 0.5,
            "border_radius": 4,
            "padding": 8,
            "line_spacing": 1.2,
            "letter_spacing": 0,
            "vertical_position": "bottom",
            "horizontal_position": "center",
            "alignment": "center",
            "safe_margin": 50,
        }

        project = Project(
            user_id=user_id,
            video_id=video_id,
            name=name,
            captions_data=captions,
            style_data=default_style,
            animation_preset="word_highlight",
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def get_project(db: Session, project_id: str) -> Project:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise RenderingError(
                f"Project '{project_id}' not found in database", status_code=404
            )
        return project

    @staticmethod
    def update_project(
        db: Session,
        project_id: str,
        captions_data: list = None,
        style_data: dict = None,
        animation_preset: str = None,
        name: str = None,
        is_favorite: bool = None,
    ) -> Project:
        project = ProjectService.get_project(db, project_id)
        if captions_data is not None:
            project.captions_data = captions_data
        if style_data is not None:
            project.style_data = style_data
        if animation_preset is not None:
            project.animation_preset = animation_preset
        if name is not None:
            project.name = name
        if is_favorite is not None:
            project.is_favorite = is_favorite
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def delete_project(db: Session, project_id: str) -> bool:
        project = ProjectService.get_project(db, project_id)
        db.delete(project)
        db.commit()
        return True

    @staticmethod
    def duplicate_project(db: Session, project_id: str) -> Project:
        source = ProjectService.get_project(db, project_id)
        duplicate = Project(
            user_id=source.user_id,
            video_id=source.video_id,
            name=f"Copy of {source.name}",
            captions_data=source.captions_data,
            style_data=source.style_data,
            animation_preset=source.animation_preset,
        )
        db.add(duplicate)
        db.commit()
        db.refresh(duplicate)
        return duplicate
