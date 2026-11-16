from enum import Enum
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException,Form,Query, Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.base import ApiResponse, TotalResponse
from app.lib.tools import get_specified_page, md5_hash
from app.dao.user import (get_user_by_username,
                          get_all_user,
                          count_admin,
                          create_user,
                          get_user_by_id,
                          commit_and_refresh_user,
                          soft_delete_user
                         )


router=APIRouter(prefix="/user", tags=["用户管理"])

#定义一个枚举类型，让新增用户的时候，只能选择1，2，3，修改角色的时候也只能选1，2，3
class RoleIdEnum(int, Enum):
    admin = 1
    teacher = 2
    student = 3
#定义一个权限依赖校验函数
#username: str，入参，从接口的 query 参数接收 username
#db: Session = Depends(get_db)，依赖注入，获取数据库会话
#-> User：返回类型注解，校验通过后返回一个user的ORM对象（user表的一条记录）
#Query代表这个参数从 URL 查询参数（?username=xxx）获取，不是 form、也不是请求体
def get_current_user(username: str=Query(..., description="操作者管理员用户名"),password:str=Query(...,description="操作者管理员密码"), db: Session = Depends(get_db)) -> User:
    user = get_user_by_username(db,username) #调用dao层函数，查询到该用户名的用户
#如果数据库查不到这个username，或者这个用户被禁用了则抛出异常
    password = md5_hash(password)
    if not user or user.is_active != 1:
        raise HTTPException(status_code=401, detail="用户不存在或账号已禁用")
    if user.password!=password:
        raise HTTPException(status_code=401,detail="管理员密码错误")
    return user
#上面两个校验全部通过，走到这一行，把查到的 User 对象返回出去
#后续接口里 `current_user` 拿到这个对象，就可以拿 `current_user.role.name` 判断角色权限。

#登录接口，简单实现登录操作
@router.post("/login",response_model=ApiResponse,summary="用户登录")
def user_login(
        username: str = Form(min_length=3, max_length=50, description="用户名"),
        password: str = Form(min_length=6, max_length=20, description="密码"),
        db: Session = Depends(get_db)
            ):

    #调用dao层的根据用户名查到这个用户的函数
    user=get_user_by_username(db,username)
    if not user or user.is_deleted==1: #根据用户名判断这个用户存不存在，再看他是否被删除
        raise HTTPException(status_code=401,detail="用户名不存在")

    if user.is_active!=1:
        raise HTTPException(status_code=401,detail="账号被禁用")

    password = md5_hash(password)
    if user.password!=password:
        raise HTTPException(status_code=401,detail="密码错误")

    user.is_login=1
    commit_and_refresh_user(db,user)

    return{"code":200,
           "message":"登录成功",
           "data":
               {"user_id":user.id,
                "user_name":user.username,
                "full_name":user.full_name,
                "role_id":user.role_id,
                "role_name":user.role.name,
                "is_login":user.is_login
                }
           }


#这是一个GET查询接口，用来获取全部未被软删除的用户；先通过依赖完成身份认证，再做角色权限校验，只有管理员允许查询；最后遍历ORM对象组装成字典返回给前端
@router.get("", response_model=ApiResponse[TotalResponse] ,summary="查看所有用户")
def query_user(
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    size: int = Query(10, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 权限校验：只有管理员才可以查询用户列表
    if current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="只有管理员可以查看用户列表")

    # 查询所有用户，关联role角色信息一起查出来,软删除掉的用户就不会被展示出来了
    user_list = get_all_user(db)

    # 整理返回数据
    result = [] #创建一个空列表，存放要返回给前端的字典
    for i in user_list: #遍历每一个用户ORM对象，手动取出字段，封装成字典，返回给前端
        result.append({
            "id": i.id,
            "username": i.username,
            "full_name": i.full_name,
            "role_id": i.role_id,
            "role_name": i.role.name,
            "teacher_class_ids": i.teacher_class_ids,
            "is_active": i.is_active
        })
    total, page = get_specified_page(result, page, size)
    return {"code":200,
        "message": "查询成功",
        "data": {"total": total,
                 "data":page}
    }
#为什么用空列表去存放返回给前端的字典，不直接返回ORM对象列表，因为ORM对象带有数据库会话相关属性，不能直接序列化JSON
@router.post("", response_model=ApiResponse,summary="添加新用户")
def add_user(
    username:str=Form(min_length=3,max_length=50,description="用户名"),
    password:str=Form(min_length=6,max_length=20,description="账号密码"),
    confirm_password:str=Form(min_length=6,max_length=20,description="再次输入账号密码"),
    full_name:str=Form(min_length=2,max_length=20,description="你的真名"),
    role_id:RoleIdEnum=Form(description="你的角色"),
    teacher_class_ids:Optional[str]=Form(default=None,description="选填，如果你是老师，请填写你负责的班级号"),
    db:Session=Depends(get_db),
    current_user:User=Depends(get_current_user)
    ):

    #使用校验函数，判断这个操作者是不是管理员，如果不是管理员，则不能新增用户，只有管理员才能进行用户操作
    if current_user.role.name!="admin":
        raise HTTPException(status_code=403, detail="只有管理员可以新增用户")
    #如果密码校验不一致，则会抛出异常
    if password!=confirm_password:
        raise HTTPException(status_code=400,detail="两次密码输入不一致")
    exist_user = get_user_by_username(db,username)
    # 用这个exist_user变量去接收查数据库里面User这张表的username这一列有没有等于添加用户时传进来的username,还有那些没有被软删除的用户
    if exist_user:
        raise HTTPException(status_code=400,detail="用户名已存在，请重新输入新的用户名")
    #因为role_id是一个枚举对象，需要取它的值,如果系统里面管理员的人数>=1,则不能再新增管理员了
    if role_id.value==1:
        admin_sum=count_admin(db) #用一个变量去接收dao层统计管理员人数的函数
        if admin_sum>=1:
            raise HTTPException(status_code=400,detail="系统已经存在管理员，不能新增管理员")
    new_user=User(
        username=username,
        password=md5_hash(password),
        full_name=full_name,
        teacher_class_ids=teacher_class_ids,
        is_active=1,
        role_id=role_id.value,
        is_deleted=0
                ) #实例化这个User模型
    new_user=create_user(db,new_user)
     #在数据库刷新这个对象，拿到自增的id，如果没有刷新，new_user的id就是None
    return {"code":200,
            "message":"新增用户成功",
            "data":{
                   "user_id":new_user.id,
                   "username": new_user.username,
                   "full_name":new_user.full_name,
                   "role_name":new_user.role.name
                   }
            }

@router.put("/{user_id}", response_model=ApiResponse,summary="修改用户信息")
def update_user(
    user_id: int = Path(description="要修改的用户ID"),
    username: Optional[str] = Form(default=None, min_length=6, max_length=50, description="用户名（不传则不修改）"),
    full_name: Optional[str] = Form(default=None, min_length=2, max_length=20, description="真实姓名（不传则不修改）"),
    role_id: Optional[RoleIdEnum] = Form(default=None, description="角色：1管理员，2老师，3学生（不传则不修改）"),
    teacher_class_ids: Optional[str] = Form(default=None, description="负责班级号，老师才填，（不传不修改）"),
    is_active: Optional[int] = Form(default=None, description="账号状态：1启用，0禁用，（不传不修改）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    # 处理swagger空字符串问题
    if username == "":
        username = None
    if full_name == "":
        full_name = None
    if teacher_class_ids == "":
        teacher_class_ids = None
    if is_active == "":
        is_active = None

    # 权限校验：只有管理员才能修改用户
    if current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="只有管理员可以修改用户信息")

    # 调用dao层函数，根据id找到目标用户,包含被软删除的用户
    edit_user = get_user_by_id(db,user_id)
    if not edit_user or edit_user.is_deleted==1:
        raise HTTPException(status_code=400, detail="该用户不存在")

    # 根据传上来的用户名，要判断是否和别人重名
    if username is not None:
        # 排除自己本身，不能和其他用户重名，尽管用户id一样，但是不能同个用户名
        same_user=get_user_by_username(db,username) #用same_user这个变量去接收调用dao层函数查询该用户名的用户函数
        if same_user and same_user.id!=user_id: #因为user_id是必填的，所有可以知道id一不一样
            raise HTTPException(status_code=400, detail="用户名已经被其他用户占用")
        edit_user.username = username
    #可以重名，你可以叫张三，我也可以叫张三
    if full_name is not None:
        edit_user.full_name = full_name
    #老师负责的班级ID可以修改，因为这个老师不会一直教这几个班级
    if teacher_class_ids is not None:
        edit_user.teacher_class_ids = teacher_class_ids
    #可以将这个用户禁用
    if is_active is not None:
        edit_user.is_active = is_active

    # 如果修改角色，可以为这个用户修改角色
    if role_id is not None:
        new_role_value = role_id.value
        admin_sum = count_admin(db)
        # 限制：不能新增第二个管理员
        if new_role_value == 1 and edit_user.role_id != 1:
            #要先统计一下啊数据库内管理员的数量
            if admin_sum >= 1:
                raise HTTPException(status_code=400, detail="系统已经存在管理员，不能把该用户改为管理员")
        # 限制：唯一管理员不能改成别的角色（防止系统没有管理员）
        if edit_user.role_id == 1 and new_role_value != 1: #想要修改唯一的管理员角色
            if admin_sum <= 1:
                raise HTTPException(status_code=400, detail="系统至少保留一名管理员，不能修改唯一管理员的角色")
        edit_user.role_id = new_role_value

    commit_and_refresh_user(db,edit_user)#调用dao层，提交更新用户的信息
    return {
        "code":200,
        "message": "修改用户成功",
        "data":{
                "user_id": edit_user.id,
                "username": edit_user.username,
                "full_name": edit_user.full_name,
                "role_name": edit_user.role.name,
                "teacher_class_ids": edit_user.teacher_class_ids,
                "is_active": edit_user.is_active
               }
            }




@router.delete("/{user_id}",response_model=ApiResponse,summary="删除用户")
#输入用户id，即可实现软删除该用户
def delete_user(
        user_id:int,
        db:Session=Depends(get_db),
        current_user:User=Depends(get_current_user)
):
#如果不是管理员登录，则不可以删除用户
    if current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="只有管理员可以删除用户")
#如果表格中没有该id，则显示用户不存在，也删除不了
#先用一个变量del_user接收这个要校验的id用户
    del_user=get_user_by_id(db,user_id)
    if not del_user:
        raise HTTPException(status_code=400, detail="要删除的用户不存在")
#如果这个人已经被软删除了，那这个人就不能被删除
    if del_user.is_deleted == 1:
        raise HTTPException(status_code=400, detail="该用户已经被删除")
#防止把唯一管理员删掉,必须核查一下数据库的管理员总数,而且管理员只能由一个，不能被删除掉的，这里不用再判断User.is_deleted==0
    if del_user.role_id==1:
        admin_sum=count_admin(db)
        if admin_sum <= 1:#还得去数据库统计一下管理员的人数个数
            raise HTTPException(status_code=400, detail="系统至少保留一名管理员，不允许删除唯一管理员")
    soft_delete_user(db,del_user) #调用dao层函数软删除用户
    return{
        "code":200,
        "message": "删除用户成功",
        "data":{
                "user_id": user_id,
                "username": del_user.username
                }
        }
#谢谢来到沃林

