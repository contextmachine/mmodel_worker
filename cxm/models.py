#  Copyright (c) CONTEXTMACHINE 2022.
#  AEC, computational geometry, digital engineering and Optimizing construction processes.
#
#  Author: Andrew Astakhov <sthv@contextmachine.space>, <aa@contextmachine.ru>
#
#  This program is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the
#  Free Software Foundation; either version 2 of the License, or (at your
#  option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
#  the full text of the license.
#
#

from typing import Optional, Union, Any, List, Sized
from pydantic import BaseModel
from dataclasses import dataclass
from enum import Enum
# Metadata
# ----------------------------------------------------------------------------------------------------------------------
# Configs
# ----------------------------------------------------------------------------------------------------------------------




@dataclass
class Configs:



    def __init__(self):
        super().__init__()




# Metadata
# ----------------------------------------------------------------------------------------------------------------------

class Metadata(BaseModel):
    """
        Модель содержит базовые поля метадаты для всех типов. Взаимодействующих с веб вьювером
    """
    type: str
    name: Optional[str]


# External file changes
# ----------------------------------------------------------------------------------------------------------------------

class Changes(BaseModel):
    delete: Optional[list[str]]
    add: Optional[list[str]]
    modify: Optional[list[str]]


class PatchInternal(BaseModel):
    patch: Any


# Info&Statistic Stuff: Charts, Dashboards, etc.
# ----------------------------------------------------------------------------------------------------------------------

class Chart(BaseModel):
    """
       Модель чарта с инфографикой
    """
    headers: Optional[list[str]] = None


# Scenes
# ----------------------------------------------------------------------------------------------------------------------

class SceneDefaultView(str, Enum):
    """
        Модель содержащая в себе доступные типы проекций в веб вьювере
    """
    perspective = "perspective"
    ortho = "ortho"
    top = "top"


class SceneMetadata(Metadata):
    """
        Расширение Metadata для объекта Scene
    """
    type = "scene"
    default_view: SceneDefaultView = SceneDefaultView.ortho


class Scene(BaseModel):
    """
        Модель сцены повторяющий спецификацию json
        Используется для генерации спецификаций при создании новых сцен из любых интерфейсов
    """
    includes: list[Union[str, None]] = []
    metadata: SceneMetadata = SceneMetadata()
    chart: Optional[Chart] = None


class Scenes:
    scenes = dict[str, Scene]


class ScenePatch(BaseModel):
    """
        Модель сцены повторяющий спецификацию json
        Используется для генерации спецификаций при создании новых сцен из любых интерфейсов
    """

    patch: Scene
