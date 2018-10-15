# -*- coding: utf-8 -*-
# Create your views here.
import os
import json
import datetime
import time
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render, get_object_or_404, reverse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from blog.models import Article, Category, Comment, MindMap, MindMapImage
from django.contrib.auth.models import User, Group
from blog.utils import xmindToJson, jsonToXmind, generateRandomString, deleteDir
from django.db import connection

def index(request):
    """
    博客首页
    :param request:
    :return:
    """
    article_list = Article.objects.all().order_by('-date_time')[0:5]
    return render(request, 'blog/index.html', {"article_list": article_list,
                                               "source_id": "index"})


def articles(request, pk):
    """
    博客列表页面
    :param request:
    :param pk:
    :return:
    """
    pk = int(pk)
    if pk:
        category_object = get_object_or_404(Category, pk=pk)
        category = category_object.name
        article_list = Article.objects.filter(category_id=pk)
    else:
        # pk为0时表示全部
        article_list = Article.objects.all()  # 获取全部文章
        category = u''
    return render(request, 'blog/articles.html', {"article_list": article_list,
                                                  "category": category,
                                                  })


def about(request):
    return render(request, 'blog/about.html')


def archive(request):
    article_list = Article.objects.order_by('-date_time')
    return render(request, 'blog/archive.html', {"article_list": article_list})


def link(request):
    return render(request, 'blog/link.html')


def message(request):
    return render(request, 'blog/message_board.html', {"source_id": "message"})


@csrf_exempt
def getComment(request):
    """
    接收畅言的评论回推， post方式回推
    :param request:
    :return:
    """
    arg = request.POST
    data = arg.get('data')
    data = json.loads(data)
    title = data.get('title')
    url = data.get('url')
    source_id = data.get('sourceid')
    if source_id not in ['message']:
        article = Article.objects.get(pk=source_id)
        article.commenced()
    comments = data.get('comments')[0]
    content = comments.get('content')
    user = comments.get('user').get('nickname')
    Comment(title=title, source_id=source_id,
            user_name=user, url=url, comment=content).save()
    return JsonResponse({"status": "ok"})


def detail(request, pk):
    """
    博文详情
    :param request:
    :param pk:
    :return:
    """
    article = get_object_or_404(Article, pk=pk)
    article.viewed()
    return render(request, 'blog/detail.html', {"article": article,
                                                "source_id": article.id})


def search(request):
    """
    搜索
    :param request:
    :return:
    """
    key = request.GET['key']
    article_list = Article.objects.filter(title__icontains=key)
    return render(request, 'blog/search.html',
                  {"article_list": article_list, "key": key})


def tag(request, name):
    """
    标签
    :param request:
    :param name
    :return:
    """
    article_list = Article.objects.filter(tag__tag_name=name)
    return render(request, 'blog/tag.html', {"article_list": article_list,
                                             "tag": name})


def kityminder(request):
    return render(request, 'blog/kityminder.html')


def coverage(request):
    return render(request, 'blog/coverage.html')



def getMapInfo(request):
    map_id = request.GET.get('id', -1)
    if map_id == -1:
        return HttpResponse(json.dumps({
            'code': -1,
            'msg': 'require parameter!' #缺少map的id参数
        }), content_type="application/json")
    user_id = request.user.id
    try:
        mind_map_object = MindMap.objects.get(id=map_id)
        
        user_group_set = request.user.groups.all()
        can_edit = False
        # 如果是超级用户，则可以进行编辑，返回的json中can_edit为True
        if request.user.is_superuser:
            can_edit = True
        # 如果所在用户在用户表中，则可以进行编辑，返回的json中can_edit为True
        else:
            for user_group in user_group_set:
                if user_group in mind_map_object.group.all():
                    can_edit = True
                    break
        if can_edit:
            if (mind_map_object.lock_user_id == None) or (time.time() - mind_map_object.lock_time > 10) or (mind_map_object.lock_user_id == user_id):
                mind_map_object.lock_user_id = user_id
                mind_map_object.lock_time = time.time()
                mind_map_object.save()
                is_locked = False
            else:
                is_locked = True
        else:
            is_locked = True
        json_data = json.loads(mind_map_object.data)
        return HttpResponse(json.dumps({
            'code': 0,
            'data': json_data,
            'title': mind_map_object.title,
            'can_edit': can_edit,
            'is_locked': is_locked
        }), content_type="application/json")
    except Exception as identifier:
        print identifier
        return HttpResponse(json.dumps({
            'code': -2,
            'msg': 'Data not exist!' #数据不存在
        }), content_type="application/json")

def updateMapInfo(request):
    user = request.user
    user_id = user.id
    user_group_set = user.groups.all()
    map_id = request.POST.get('id', -1)
    data = request.POST.get('data', '')
    if map_id == -1 or data == '':
        return HttpResponse(json.dumps({
            'code': -1,
            'msg': 'require parameter!' #缺少map的id参数
        }), content_type="application/json")

    temp_data = data
    image_ids = []
    while True:
        pre_position = temp_data.find('/blog/kityminder/get_image?id=')
        if pre_position == -1:
            break
        else:
            temp_data = temp_data[pre_position + 30:]
            ex_position = temp_data.find('"')
            image_ids.append(int(temp_data[0: ex_position]))
            temp_data = temp_data[ex_position + 1:]

    
    try:
        mind_map_object = MindMap.objects.get(id=map_id)
        mind_map_object.data = data

        can_edit = False
        # 如果是超级用户，则可以进行编辑，返回的json中can_edit为True
        if request.user.is_superuser:
            can_edit = True
        # 如果所在用户在用户表中，则可以进行编辑，返回的json中can_edit为True
        else:
            for user_group in user_group_set:
                if user_group in mind_map_object.group.all():
                    can_edit = True
                    break
        if not can_edit:
            return HttpResponse(json.dumps({
                'code': -4,
                'msg': 'Permission denied!' #权限不够
            }), content_type="application/json")
        else:
            if (mind_map_object.lock_user_id == None) or (time.time() - mind_map_object.lock_time > 10) or (mind_map_object.lock_user_id == user_id):
                mind_map_object.lock_user_id = user_id
                mind_map_object.lock_time = time.time()
            else:
                return HttpResponse(json.dumps({
                    'code': -8,
                    'msg': 'Map is locked!' #文件被锁
                }), content_type="application/json")

        try:
            mind_map_object.save()
            delete_image_list = []
            for image_object in mind_map_object.image.all():
                if image_object.id not in image_ids:
                    delete_image_list.append(image_object)
            for image_object in delete_image_list:
                mind_map_object.image.remove(image_object)
            for image_id in image_ids:
                if len(mind_map_object.image.filter(id = image_id)) == 0:
                    mind_map_object.image.add(MindMapImage.objects.get(id=image_id))
            mind_map_object.save()

            with connection.cursor() as cursor:
                cursor.execute('select * from blog_mindmapimage where id not in (select mindmapimage_id from blog_mindmap_image group by mindmapimage_id order by mindmapimage_id)')
                result = cursor.fetchall()
                cursor.close()
                fileDir = os.getcwd() + '/static/map_images'
                for result_row in result:
                    print result_row
                    print fileDir+"/"+result_row[1]
                    if os.path.isfile(fileDir+"/"+result_row[1]):
                        ft = os.stat(fileDir+"/"+result_row[1])
                        ltime = int(ft.st_mtime)  # 获取文件最后修改时间
                        ntime = int(time.time())-20  # 获取现在时间减去20s
                        print ltime
                        print ntime

                        if ltime <= ntime:
                            os.remove(fileDir+"/"+result_row[1])  # 删除当前时间20s之前的时间以前的文件
                            MindMapImage.objects.get(id=result_row[0]).delete()

            return HttpResponse(json.dumps({
                'code': 0,
                'msg': 'update success',
            }), content_type="application/json")
        except Exception as identifier:
            print identifier
            return HttpResponse(json.dumps({
                'code': -3,
                'msg': 'data updates fail!' #数据更新错误
            }), content_type="application/json")
    except Exception as identifier:
        return HttpResponse(json.dumps({
            'code': -2,
            'msg': 'Data not exist!' #数据不存在
        }), content_type="application/json")
def updateLock(request):
    user = request.user
    user_id = user.id
    user_group_set = user.groups.all()
    map_id = request.GET.get('id', -1)
    mind_map_object = MindMap.objects.get(id=map_id)
    user_group_set = user.groups.all()
    # 如果是超级用户，则可以进行编辑，返回的json中can_edit为True
    if request.user.is_superuser:
        can_edit = True
    # 如果所在用户在用户表中，则可以进行编辑，返回的json中can_edit为True
    else:
        for user_group in user_group_set:
            if user_group in mind_map_object.group.all():
                can_edit = True
                break
    if not can_edit:
        return HttpResponse(json.dumps({
            'code': -4,
            'msg': 'Permission denied!' #权限不够
        }), content_type="application/json")
    else:
        if (mind_map_object.lock_user_id == None) or (time.time() - mind_map_object.lock_time > 10) or (mind_map_object.lock_user_id == user_id):
            mind_map_object.lock_user_id = user_id
            mind_map_object.lock_time = time.time()
        else:
            return HttpResponse(json.dumps({
                'code': -8,
                'msg': 'Map is locked!' #文件被锁
            }), content_type="application/json")
    
    
    mind_map_object.save()
    return HttpResponse(json.dumps({
        'code': 0,
        'msg': 'update lock success',
    }), content_type="application/json")

def downloadXMind(request):
    path = os.getcwd() + '/temp/'
    deleteDir(path, 60) #删除temp文件夹下1分钟内没有被修改的文件（清理垃圾）
    path +=  generateRandomString(20) + '.xmind'
    data = request.POST.get('data', '')
    title = request.POST.get('title', '')
    if data == '' or title == '':
        return HttpResponse(json.dumps({
            'code': -1,
            'msg': 'require parameter!' #缺少map的id参数
        }), content_type="application/json")
    try:
        jsonToXmind(data, path)
        def file_iterator(file_name, chunk_size=512):
            with open(file_name) as f:
                while True:
                    c = f.read(chunk_size)
                    if c:
                        yield c
                    else:
                        break
        filepath = path
        response = StreamingHttpResponse(file_iterator(filepath))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(title+ '.xmind')
        return response
    except Exception as identifier:
        return HttpResponse(json.dumps({
            'code': -5,
            'msg': 'Xmind file generate failed!' #生成xmind文件失败
        }), content_type="application/json")
    
    return HttpResponse(path)

def upLoadImage(request):
    errno = 0
    msg = 'ok'
    url = ''
    if request.method == 'POST':
        file_obj = request.FILES.get('upload_file')
        content_type = file_obj.content_type
        size = file_obj.size
        if (content_type == 'image/gif' or content_type == 'image/jpeg' or content_type == 'image/jpg' or content_type == 'image/png') and (size < 1 * 1000 * 1000):
            # 分为两种情况 `Ctrl + V` 和普通上传
            if file_obj.name == 'blob':
                ext_name = 'png'
            else:
                ext_name = content_type[6:]
            
            prefix_name = generateRandomString(20)
            filename = prefix_name + '.' + ext_name
            path = os.getcwd() + '/static/map_images/'
        
            f = open(path + filename, 'wb')
            for chunk in file_obj.chunks():
                f.write(chunk)
            f.close()
            mindmap_image = MindMapImage()
            mindmap_image.filename = filename
            mindmap_image.save()
            id = MindMapImage.objects.get(filename = filename).id
            url = request.GET.get('host') + '/blog/kityminder/get_image?id=' + str(id)
        else:
            errno = 416
            msg = 'File is invalid'
        
        return HttpResponse(json.dumps({
            'errno': errno,
            'msg': msg,
            'data': {
                'url': url
            }
        }), content_type="application/json")
    return HttpResponse("ok")

def getImage(request):
    id = request.GET.get('id', -1)
    if id == -1:
        return HttpResponse('',content_type="image/png")
    else:
        try:
            mind_map_image = MindMapImage.objects.get(id=id)
            filename = mind_map_image.filename
            ext_name = filename[filename.find('.'):]
            imagepath = os.getcwd() + '/static/map_images/' + filename
            image_data = open(imagepath,"rb").read()
            return HttpResponse(image_data,content_type='image/' + ext_name)
        except Exception as identifier:
            return HttpResponse('',content_type="image/png")

def kityminderList(request):
    return render(request, 'blog/kityminder_list.html')

def getCategories(request):
    dict = {
        'code': 0,
        'data': []
    }
    categories = Category.objects.all()
    for category in categories:
        dict['data'].append({
            'id': category.id,
            'name': category.name
        })
    return HttpResponse(json.dumps(dict), content_type="application/json")

def getMindmaps(request):
    dict = {
        'code': 0,
        'data': []
    }
    mindmaps = MindMap.objects.all()
    for mindmap in mindmaps:
        temp_dict = {}
        temp_dict['id'] = mindmap.id
        temp_dict['title'] = mindmap.title
        temp_dict['modify_time'] = int(time.mktime(mindmap.modify_time.timetuple())) * 1000
        user_group_set = request.user.groups.all()
        is_superuser = request.user.is_superuser
        try:
            temp_dict['modify_user_name'] = User.objects.get(id=mindmap.modify_user).username
        except Exception as identifier:
            temp_dict['modify_user_name'] = '已注销用户'
        try:
            temp_dict['create_user_name'] = User.objects.get(id=mindmap.create_user).username
        except Exception as identifier:
            temp_dict['create_user_name'] = '已注销用户'
        temp_dict['category_id'] = mindmap.category_id
        can_edit = False
        # 如果是超级用户，则可以进行编辑，返回的json中can_edit为True
        if is_superuser:
            can_edit = True
        # 如果所在用户在用户表中，则可以进行编辑，返回的json中can_edit为True
        else:
            for user_group in user_group_set:
                if user_group in mindmap.group.all():
                    can_edit = True
                    break
        temp_dict['can_edit'] = can_edit
        temp_dict['groups'] = []
        for group in mindmap.group.all():
            temp_dict['groups'].append({
                'id': group.id,
                'name': group.name
            })
        dict['data'].append(temp_dict)

    return HttpResponse(json.dumps(dict), content_type="application/json")

def delMindmap(request):
    dict = {
        'code': 0,
        'msg': ''
    }
    is_superuser = request.user.is_superuser
    user_group_set = request.user.groups.all()
    map_id = request.POST.get('id')
    try:
        mindmap = MindMap.objects.get(id=map_id)
        can_edit = False
        # 如果是超级用户，则可以进行编辑，返回的json中can_edit为True
        if is_superuser:
            can_edit = True
        # 如果所在用户在用户表中，则可以进行编辑，返回的json中can_edit为True
        else:
            for user_group in user_group_set:
                if user_group in mindmap.group.all():
                    can_edit = True
                    break
        if can_edit:
            mindmap.delete()
            dict['data'] = 'delete success'
        else:
            dict['code'] = -4
            dict['msg'] = 'Permission denied!' #权限不够
    except Exception as identifier:
        dict['code'] = -2
        dict['msg'] = 'Data not exist!' #数据不存在'
    
    return HttpResponse(json.dumps(dict), content_type="application/json")

def updateMindmapTitle(request):
    dict = {
        'code': 0,
        'msg': ''
    }
    is_superuser = request.user.is_superuser
    user_group_set = request.user.groups.all()
    map_id = request.POST.get('id')
    title = request.POST.get('title')
    try:
        mindmap = MindMap.objects.get(id=map_id)
        can_edit = False
        # 如果是超级用户，则可以进行编辑，返回的json中can_edit为True
        if is_superuser:
            can_edit = True
        # 如果所在用户在用户表中，则可以进行编辑，返回的json中can_edit为True
        else:
            for user_group in user_group_set:
                if user_group in mindmap.group.all():
                    can_edit = True
                    break
        if can_edit:
            mindmap.title = title
            mindmap.save()
            dict['data'] = 'delete success'
        else:
            dict['code'] = -4
            dict['msg'] = 'Permission denied!' #权限不够
    except Exception as identifier:
        dict['code'] = -2
        dict['msg'] = 'Data not exist!' #数据不存在'
    
    return HttpResponse(json.dumps(dict), content_type="application/json")

def getUserGroups(request):
    dict = {
        'code': 0,
        'data': []
    }
    if request.user.is_superuser:
        print Group.objects.all()
        for group in Group.objects.all():
            dict['data'].append({'id': group.id, 'name': group.name})
    else:
        user_group_set = request.user.groups.all()
        for user_group in user_group_set:
            dict['data'].append({'id': user_group.id, 'name': user_group.name})
    return HttpResponse(json.dumps(dict), content_type="application/json")

def isSuperUser(request):
    dict = {
        'code': 0,
        'data': {}
    }
    is_superuser = request.user.is_superuser
    dict['data']['is_superuser'] = is_superuser
    return HttpResponse(json.dumps(dict), content_type="application/json")


def createMindmap(request):
    dict = {
        'code': 0,
        'msg': 'create_success'
    }
    if request.method == 'POST':
        group_ids = json.dumps(request.POST.get('group_ids'))
        category_id = request.POST.get('category_id')
        title = request.POST.get('title')

        if len(title) == 0:
            dict['code'] = -6
            dict['msg'] = 'title is blank!'
            return HttpResponse(json.dumps(dict), content_type="application/json")
        
        if len(group_ids) == 0:
            dict['code'] = -7
            dict['msg'] = 'array length is 0!'
            return HttpResponse(json.dumps(dict), content_type="application/json")
        
        group_ids = group_ids[group_ids.find("\"") + 1:]
        group_ids = group_ids[0: group_ids.find("\"")]
        group_ids = group_ids.split(',')
        for i in range(0, len(group_ids)):
            group_ids[i] = int(group_ids[i])

        
        mindmap = MindMap()
        mindmap.create_user = request.user.id
        mindmap.modify_user = request.user.id
        mindmap.title = title
        mindmap.category_id = category_id
        mindmap.data = '{}'
        groups = []
        mindmap.save()

        for group_id in group_ids:
            mindmap.group.add(Group.objects.get(id=group_id))
        mindmap.save()
        dict['data'] = {'id': mindmap.id}

        return HttpResponse(json.dumps(dict), content_type="application/json")
    
def loadMindmap(request):
    dict = {
        'code': 0,
        'msg': 'create_success'
    }
    if request.method == 'POST':
        group_ids = json.dumps(request.POST.get('group_ids'))
        category_id = request.POST.get('category_id')
        title = request.POST.get('title')

        if len(title) == 0:
            dict['code'] = -6
            dict['msg'] = 'title is blank!'
            return HttpResponse(json.dumps(dict), content_type="application/json")
        
        if len(group_ids) == 0:
            dict['code'] = -7
            dict['msg'] = 'array length is 0!'
            return HttpResponse(json.dumps(dict), content_type="application/json")

        group_ids = group_ids[group_ids.find("\"") + 1:]
        group_ids = group_ids[0: group_ids.find("\"")]
        group_ids = group_ids.split(',')
        for i in range(0, len(group_ids)):
            group_ids[i] = int(group_ids[i])

        file_obj = request.FILES.get('upload_file')
        prefix_name = generateRandomString(20)
        filename = prefix_name + '.xmind' 
        path = os.getcwd() + '/temp/'
        f = open(path + filename, 'wb')
        for chunk in file_obj.chunks():
            f.write(chunk)
        f.close()


        mindmap = MindMap()
        img_ex_url = request.GET.get('host') + '/blog/kityminder/get_image?id='
        kitty_mind_json_data, img_id_list = xmindToJson(path + filename, img_ex_url)
        mindmap.create_user = request.user.id
        mindmap.modify_user = request.user.id
        mindmap.title = title
        mindmap.category_id = category_id
        mindmap.data = kitty_mind_json_data
        groups = []
        mindmap.save()
        for group_id in group_ids:
            mindmap.group.add(Group.objects.get(id=group_id))
        for img_id in img_id_list:
            mindmap.image.add(MindMapImage.objects.filter(id=img_id)[0])
        mindmap.save()
        dict['data'] = {'id': mindmap.id}
        os.remove(path + filename)
        return HttpResponse(json.dumps(dict), content_type="application/json")