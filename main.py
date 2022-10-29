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
import json
import os
import sys
from enum import Enum

import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import StreamingResponse, PlainTextResponse

from cxm.buckets.apps import AppSession
from cxm.models import Scene, ScenePatch, Scenes

sys.path.extend([f"{os.getenv('PWD')}/mount_sorces"])
print("Starting mmodel server ...")


class CxmViewerAppSession(AppSession):

    def __init__(self):
        self.validate_context()

        self.decompress_view = "tmpj/"
        self._existing_scenes = None
        self._topics = None
        super().__init__(buck=self.bucket)
        self.x_logo = dict(
            url=self.storage + self.bucket + self.full_icon
        )

    def stream_view(self, name):
        return self.s3.get_object(Bucket=self.bucket, Key=self.view + name)["Body"]

    def get_decompress_view(self, name):
        with self.s3.get_object(Bucket=self.bucket, Key=self.decompress_view + name)["Body"] as obj:
            yield from obj

    def get_compress_view(self, name):
        with self.s3.get_object(Bucket=self.bucket, Key=self.view + name)["Body"] as obj:
            yield from obj

    @property
    def existing_scenes(self):
        self._existing_scenes = Scenes()
        for k in self.get_keys(pref=self.scenes)[1:]:
            self._existing_scenes.scenes[k] = Scene(**json.loads(self.get_object(name=k, pref=self.scenes).read()))
        return self._existing_scenes

    @property
    def topics(self):
        return self.get_keys(self._topics)

    @topics.setter
    def topics(self, v, pref=None):
        self.put_object(self._topics, v, pref=pref)

    def validate_context(self):

        env_args = ['STORAGE', "BUCKET"]

        for arg in env_args:
            # try:
            self.__dict__[arg.lower()] = os.getenv(arg)
            # finally:
            #   raise RuntimeError(f"Missing required argument: [{arg}]")

    def __str__(self):
        return "\n\nMaster Model Server\n" \
               "---------------------------------------------------------------------------------------\n" \
               "👨‍💻 AEC, computational geometry, digital optimisation & automation .\n" \
               "👷 Yours engineering & construction processes.\n\n" \
               "\n\tconfig.json:\n{}\n\nCopyright (c) CONTEXTMACHINE 2022.\n".format(json.dumps(self.config, indent=3))


sess = CxmViewerAppSession()

# FastApi
# ----------------------------------------------------------------------------------------------------------------------
# Configurate fastapi
#

# Middleware setup

app = FastAPI(debug=True)
app.add_middleware(GZipMiddleware, minimum_size=500)

origins = [
    "*",
    "http//localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if "ssl_certfile" in sess.config["uvicorn"].keys():
    app.add_middleware(HTTPSRedirectMiddleware)


# ⚙️🔧 Basic Api setup
# －－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
# －－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－


# 📑📮 WebSockets
# －－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－

@app.get("/terms", include_in_schema=False)
def terms():
    return PlainTextResponse("""
    TERM AND TERMINATION
    
    Copyright (c) CONTEXTMACHINE 2022.
    AEC, computational geometry, digital engineering and Optimizing construction processes.
    
    Contrebuteres: 
    "Andrew Astakhov", "https://github.com/sth-v", <sthv@contextmachine.space>, <aa@contextmachine.ru>
    "Sofya Dobychina", "https://github.com/sf-d", <"sf@contextmachine.ru>
    
    This program is free software; you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by the
    Free Software Foundation; either version 2 of the License, or (at your
    option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
    the full text of the license.
    
    
    Unless otherwise terminated as specified under this Agreement. Licensee’s rights with respect to the Beta Software 
    will terminate upon the earlier of (a) the initial commercial release by Talend of a generally available version of 
    the Beta Software or (b) automatic expiration of the Beta Software based on the system date. Either party may 
    terminate this Agreement at any time for any reason or no reason by providing the other party advance written notice 
    thereof. Talend shall immediately terminate this Agreement and any Licensee rights with respect to the Beta Software 
    without notice in the event of improper disclosure of Talend’s Beta Software as specified under Section 6 (
    Confidentiality) below. Upon any expiration or termination of this Agreement, the rights and licenses granted to 
    Licensee under this Agreement shall immediately terminate, and Licensee shall immediately cease using, 
    and will return to Talend (or, at Talend’s request, destroy), the Beta Software, Documentation, and all other 
    tangible items in Licensee’s possession or control that are proprietary to or contain Confidential Information. The 
    rights and obligations of the parties set forth in Sections 2, 3, 4, 5, 6, 7, 8 9 and 10 shall survive termination or 
    expiration of this Agreement for any reason. """)


@app.get("/config")
async def get_config():
    """
    Get the ${bucket}://config.json instance configuration file
    Получить файл ${bucket}://config.json конфигурации инстанса

    :return: json/text
    """
    return sess.config


@app.get("/favicon.ico", responses={
    200: {
        "content": {"image/png": {}}
    }
}, include_in_schema=False)
async def favicon():
    return StreamingResponse(sess.get_icon(), media_type=sess.icon)


# Mmodel Viewer Api content
# ----------------------------------------------------------------------------------------------------------------------

@app.get("/get_keys")
async def get_keys():
    """
        List of available visible objects names
        Список имен доступных отображаемых объектов
    """
    return sess.get_keys(pref=sess.view)[1:]


class Encodings(str, Enum):
    """
    Available compressing
    """

    gz = "gzip"
    json = "json"


@app.get("/get_part/{name}")
async def get_part(name: str, f: Encodings = Encodings.json):
    """
        Get the visible object by name
        Получает отображаемый объект по имени
    """
    if f.name == "gz":
        return StreamingResponse(sess.s3.get_compress_view(name),
                                 media_type="gzip")
    elif f.name == "json":
        return StreamingResponse(sess.s3.get_object(Bucket=sess.bucket, Key=sess.decompress_view + name)["Body"])
    else:
        pass


# Scenes
# ----------------------------------------------------------------------------------------------------------------------

@app.get("/scenes")
async def scenes():
    """
        List of available scene objects names
        Список имен доступных сцен
    """
    return sess.get_keys(pref=sess.scenes)


@app.options("/scenes")
async def scenes():
    """
        List of available scene objects names
        Список имен доступных сцен
    """
    return sess.get_keys(pref=sess.scenes)


@app.get("/scenes/{name}")
async def get_scene(name: str):
    """
        Get the scene object by name
        Получает сцену по имени
    """
    return json.loads(sess.get_object(name=name, pref=sess.scenes).read())


@app.put("/scenes/create")
async def create_scene(data: Scene):
    """
        Сreate new scene object
        Создает новую сцену
    """
    scene = data.json(ensure_ascii=False, indent=3)
    sess.put_object(name=data.metadata.name, data=scene, pref=sess.scenes)

    return {
        data.metadata.name:
            data.dict()
    }


@app.delete("/scenes/delete/{name}")
async def delete_scene(name: str):
    """
        Delete existing scene object
        Удаляет существующуб сцену
    """
    response = sess.delete_object(name=name, pref=sess.scenes)

    return {
        "name": name,
        "is_delete": response['DeleteMarker']
    }


@app.patch("/scenes/patch/{name}", response_model=Scene)
async def patch_scene(name: str, data: ScenePatch):
    """

        :param name: Имя сцены для обновления
        :param data: Контент обновления ввиде словаря тех значений которые вы хотите обновить.

        :return: Обновленное представление объекта
    """

    print(name)
    scene_dict = json.loads(sess.get_object(name=name, pref=sess.scenes).read())
    scene_dict |= data.patch
    scene = Scene(**scene_dict)
    sess.put_object(name=name, pref=sess.scenes, data=scene.json(ensure_ascii=False, indent=3))
    return scene


@app.get("/files")
async def files():
    """
        List of available files names
        Список имен доступных файлов
    """
    return sess.get_keys(pref=sess.config["filesystem"])


@app.get("/files/{name}")
async def get_file(name: str):
    """
        Получите файл по имени.
    """

    return StreamingResponse(sess.s3.get_object(Bucket=sess.bucket, Key=sess.config["filesystem"] + name)["Body"],
                             media_type="file/bytes")


@app.post("/files/{name}")
async def upload_file(name: str, file: UploadFile = File(description="Update file as UploadFile")):
    """
        Обновите/загрузите файл.
    """
    file.filename = name
    content = await file.read()
    sess.put_object(name, pref=sess.config["filesystem"], data=content)
    with open(f"/home/sthv/ifctest/ifctest/cxm/data/{name}", "wb") as fp:
        fp.write(content)

    return {name: file.__sizeof__()}


@app.post("/files/{name}")
async def test_download(name: str, file: UploadFile = File(description="Update file as UploadFile")):
    """
        Обновите/загрузите файл.
    """
    file.filename = name
    content = await file.read()
    sess.put_object(name, pref=sess.config["filesystem"], data=content)
    with open(f"/home/sthv/ifctest/ifctest/cxm/data/{name}", "wb") as fp:
        fp.write(content)

    return {name: file.__sizeof__()}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="mmodel-api",
        version="0.1.1-beta",
        description="MasterModel OpenAPI schema. "
                    "Copyright (c)  CONTEXTMACHINE 2022."
                    "AEC, computational geometry, digital engineering and Optimizing construction processes.",

        routes=app.routes,
        terms_of_service="terms",
        contact=dict(
            info="hello@contextmachine.ru",
            autors=[
                dict(name="Andrey Astakhov", url="https://github.com/sth-v", email="aa@contextmachine.ru"),
                dict(name="Sofya Dobychina", url="https://github.com/sf-d", email="sf@contextmachine.ru")
            ]
        )

    )
    openapi_schema["info"]["x-logo"] = sess.x_logo

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# app.add_middleware(HTTPSRedirectMiddleware)
app.openapi = custom_openapi

# Press the green button in the gutter to run the script.


if __name__ == '__main__':
    uvicorn.run('main:app', port=sess.config["port"], host=sess.config["host"], **sess.config["uvicorn"])

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
