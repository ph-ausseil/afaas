from __future__ import annotations
import copy
import abc
import datetime
import enum
import os
import uuid
from typing import Any, Callable, Generic, Optional, Type, TypeVar, get_args, ForwardRef
from pydantic import ConfigDict, BaseModel, Field
from pydantic_core.core_schema import ModelField
from pydantic_core import PydanticUndefined


UndefinedType = ForwardRef('UndefinedType')

T = TypeVar("T")
M = TypeVar("M", bound=BaseModel)

from AFAAS.lib.sdk.logger import AFAASLogger

LOG = AFAASLogger(name=__name__)

def update_model_config(original : ConfigDict, new : dict) -> ConfigDict:
    """Update the model_config of a BaseModel"""
    new_config = copy.deepcopy(original)
    new_config.update(new)
    return new_config


def UserConfigurable(
    default: T | UndefinedType = PydanticUndefined,
    *args,
    default_factory: Optional[Callable[[], T]] = None,
    from_env: Optional[str | Callable[[], T | None]] = None,
    description: str = "",
    **kwargs,
) -> T:
    # TODO: use this to auto-generate docs for the application configuration
    return Field(
        default,
        *args,
        default_factory=default_factory,
        description=description,
        **kwargs,
    )


class SystemConfiguration(BaseModel):

    @classmethod
    def from_env(cls):
       # FIXME : Remove method from_env() 
        ...

    model_config = ConfigDict(
        extra="allow", 
        use_enum_values=True, 
        json_encoders={
            uuid.UUID: lambda v: str(v),
            float: lambda v: str(
                9999.99 if v == float("inf") or v == float("-inf") else v
            ),
            datetime.datetime: lambda v: v.isoformat(),
        }, 
        default_exclude={
            "agent",
            "workspace",
            "prompt_manager",
            "chat_model_provider",
            "memory",
            "tool_registry",
            "prompt_settings",
            "systems",
            "configuration",
            "name",
            "description",
            "message_agent_user",
            "db",
        }, 
        allow_inf_nan=False, 
        validate_assignment=True
        )

    def json(self, **dumps_kwargs) -> str:
        LOG.warning(f"{__qualname__}.json()")
        return super().json(**dumps_kwargs)


SC = TypeVar("SC", bound=SystemConfiguration)


class AFAASModel(BaseModel):


    model_config = ConfigDict(extra="allow", 
                              use_enum_values=True, 
                              json_encoders={
                                uuid.UUID: lambda v: str(v),
                                float: lambda v: str(
                                    9999.99 if v == float("inf") or v == float("-inf") else v
                                ),
                                datetime.datetime: lambda v: str(v.isoformat()),
                                }, 
                                arbitrary_types_allowed=True, 
                                allow_inf_nan=False, 
                                default_exclude=set()
                                )

    created_at: datetime.datetime = datetime.datetime.now()
    modified_at: datetime.datetime = datetime.datetime.now()

    def dict_db(self, **dumps_kwargs) -> dict:
        LOG.trace(f"FIXME: Temporary implementation before pydantic 2.0.0")
        dict = self.model_dump(**dumps_kwargs)
        return self._apply_custom_encoders(data=dict)

    def _apply_custom_encoders(self, data: dict) -> dict:
        encoders = self.model_config['json_encoders']
        for key, value in data.items():
            for type_, encoder in encoders.items():
                if isinstance(value, type_):
                    data[key] = encoder(value)
        return data

    def model_dump(self, include_all=False, *args, **kwargs):
        # TODO: Move to System settings ?
        self.prepare_values_before_serialization()  # Call the custom treatment before .model_dump()
        if not include_all:
            kwargs["exclude"] = self.model_config['default_exclude']
        # Call the .model_dump() method with the updated exclude_arg
        return super().model_dump(*args, **kwargs)

    def json(self, *args, **kwargs):
        LOG.warning("Warning : Recomended use json_api() or json_memory()")
        LOG.warning("BaseAgent.SystemSettings.json()")
        self.prepare_values_before_serialization()  # Call the custom treatment before .json()
        kwargs["exclude"] = self.model_config['default_exclude']
        return super().json(*args, **kwargs)

    # TODO Implement a BaseSettings class and move it to the BaseSettings ?
    def prepare_values_before_serialization(self):
        pass

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        lines = [f"repr:{self.__class__.__name__}("]

        for (
            field_name,
            field_value,
        ) in self.__dict__.items():  # Use __dict__ to access object's attributes
            formatted_field_name = field_name.replace("_", " ").capitalize()
            if field_value is None:
                value_str = "Not provided"
            elif isinstance(field_value, list):
                value_str = ", ".join(map(str, field_value))
                value_str = f"[{value_str}]"
            elif isinstance(field_value, dict):
                value_str = str(field_value)
            else:
                value_str = str(field_value)

            lines.append(f"  {formatted_field_name}: {value_str}")

        lines.append(")")
        return "\n".join(lines)

    @staticmethod
    def generate_uuid():
        return str(uuid.uuid4())


class SystemSettings(AFAASModel):


    model_config = ConfigDict(default_exclude={
            "agent",
            "workspace",
            "prompt_manager",
            "default_llm_provider",
            "memory",
            "tool_registry",
            "prompt_settings",
            "systems",
            "configuration",
            "agent_setting_module",
            "agent_setting_class",
            "name",
            "description",
            "parent_agent",
            "current_task",
            "message_agent_user",
            "db",
            "plan",
    },
    )


S = TypeVar("S", bound=SystemSettings)


class Configurable(abc.ABC, Generic[S]):
    """A base class for all configurable objects."""

    class SystemSettings(SystemSettings):
        """A base class for all system settings."""

        name: str
        description: str
        model_config = ConfigDict(
        extra="allow", 
        use_enum_values=True, 
        allow_inf_nan=False
        )

    def json(self, **dumps_kwargs) -> str:
        LOG.warning(f"{__qualname__}.json()")
        return super().json(**dumps_kwargs)

    def __init__(self, settings: S, **kwargs):
        self._settings = settings


class AFAASMessageType(str, enum.Enum):
    AGENT_LLM = "agent_llm"
    AGENT_AGENT = "agent_agent"
    AGENT_USER = "agent_user"

