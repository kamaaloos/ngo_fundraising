from dataclasses import dataclass, field


@dataclass
class AppSession:
    user_id: int | None = None
    username: str = ""
    full_name: str = ""
    role: str = "user"
    project_ids: list[int] = field(default_factory=list)
    current_project_id: int | None = None

    @property
    def is_authenticated(self) -> bool:
        return self.user_id is not None

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    def can_access_project(self, project_id: int) -> bool:
        if self.is_admin:
            return True
        return project_id in self.project_ids

    def clear(self) -> None:
        self.user_id = None
        self.username = ""
        self.full_name = ""
        self.role = "user"
        self.project_ids = []
        self.current_project_id = None


current_session = AppSession()
