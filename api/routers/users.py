from fastapi import APIRouter, Depends
from pydantic import BaseModel, HttpUrl
from api.utils import JwtFactory, Const, Dao
from api.depends import token_is_valid
import requests
import json

user_router = APIRouter(
    prefix='/api/user'
)


class LoginPostBody(BaseModel):
    """
    登录请求体模型
    """
    js_code: str
    avatar_url: HttpUrl
    nickname: str


class VerifyBody(BaseModel):
    """
    登录验证模型
    """
    js_code: str
    appid: str = Const.APPID
    secret: str = Const.APPSECRET
    grant_type: str = 'authorization_code'


@user_router.post('/login')
async def user_login(login_body: LoginPostBody):
    """
    用户登录接口处理
    :param login_body:登录体
    :return:
    """
    vb = VerifyBody(js_code=login_body.js_code)
    response = requests.get(url=Const.verify_url, params=vb.dict())
    content: dict = json.loads(response.content.decode())
    if 'errcode' in content:
        return {'errcode': content.get('errcode'), 'errmsg': content.get('errmsg')}
    else:
        try:
            openid = content.get('openid')
            Dao.update_user(openid, login_body.avatar_url, login_body.nickname)
            uid = Dao.get_uid_by_openid(openid)
            return {'errcode': 0, 'token': JwtFactory.generate_token_openid_uid(openid, uid)}
        except Exception as e:
            return {'errcode': 500, 'errmsg': '服务器内部错误'}
