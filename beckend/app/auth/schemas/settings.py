from dataclasses import dataclass




@dataclass(slots=True)
class SettingsAuthDTO:
    private_key: bytes
    public_key: bytes
    algorithm: str
    access_exp: int
    refresh_exp: int

    def __repr__(self):
        return 'Настройки сервиса'


@dataclass(slots=True)
class ReqUser:
    ip: str
    user_agent: str